//! Version checking utilities for comparing client and server versions.
//!
//! This module provides functions to check version compatibility between
//! client applications and the torc-server, with appropriate warning levels.

use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;

/// The current version of this binary, set at compile time.
pub const CLIENT_VERSION: &str = env!("CARGO_PKG_VERSION");

/// The git commit hash of this binary, set at compile time via build.rs.
pub const GIT_HASH: &str = env!("GIT_HASH");

/// Suffix indicating if the build was from a dirty working directory.
pub const GIT_DIRTY: &str = env!("GIT_DIRTY");

/// Returns the full version string including git hash (e.g., "0.8.0 (abc1234)")
pub fn full_version() -> String {
    format!("{} ({}{})", CLIENT_VERSION, GIT_HASH, GIT_DIRTY)
}

/// Returns just the version with git hash suffix (e.g., "0.8.0-abc1234")
pub fn version_with_hash() -> String {
    format!("{}-{}{}", CLIENT_VERSION, GIT_HASH, GIT_DIRTY)
}

/// Severity level for version mismatches.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VersionMismatchSeverity {
    /// Versions match exactly - no warning needed.
    None,
    /// Only patch version differs - minor warning.
    Patch,
    /// Minor version of client is higher than server - strong warning.
    Minor,
    /// Major version differs - error condition.
    Major,
}

impl VersionMismatchSeverity {
    /// Returns true if this severity level should prevent operation.
    pub fn is_blocking(&self) -> bool {
        matches!(self, VersionMismatchSeverity::Major)
    }

    /// Returns true if any warning should be displayed.
    pub fn has_warning(&self) -> bool {
        !matches!(self, VersionMismatchSeverity::None)
    }
}

/// Result of a version check operation.
#[derive(Debug, Clone)]
pub struct VersionCheckResult {
    /// The client (local) version.
    pub client_version: String,
    /// The server version (if successfully retrieved).
    pub server_version: Option<String>,
    /// The severity of any version mismatch.
    pub severity: VersionMismatchSeverity,
    /// A human-readable message describing the result.
    pub message: String,
}

impl VersionCheckResult {
    /// Creates a new result for when the server couldn't be reached.
    pub fn server_unreachable() -> Self {
        Self {
            client_version: CLIENT_VERSION.to_string(),
            server_version: None,
            severity: VersionMismatchSeverity::None,
            message: "Could not check server version".to_string(),
        }
    }

    /// Creates a new result for a successful version check.
    pub fn new(client_version: &str, server_version: &str) -> Self {
        let severity = compare_versions(client_version, server_version);
        let message = format_version_message(client_version, server_version, severity);

        Self {
            client_version: client_version.to_string(),
            server_version: Some(server_version.to_string()),
            severity,
            message,
        }
    }
}

/// Parses a version string into (major, minor, patch) components.
/// Returns None if parsing fails.
fn parse_version(version: &str) -> Option<(u32, u32, u32)> {
    // Strip any leading 'v' if present
    let version = version.strip_prefix('v').unwrap_or(version);

    let parts: Vec<&str> = version.split('.').collect();
    if parts.len() < 3 {
        return None;
    }

    let major = parts[0].parse().ok()?;
    let minor = parts[1].parse().ok()?;
    // Handle patch versions that may have suffixes like "-beta"
    let patch_str = parts[2].split('-').next().unwrap_or(parts[2]);
    let patch = patch_str.parse().ok()?;

    Some((major, minor, patch))
}

/// Compares two version strings and returns the severity of any mismatch.
pub fn compare_versions(client_version: &str, server_version: &str) -> VersionMismatchSeverity {
    let client = match parse_version(client_version) {
        Some(v) => v,
        None => {
            eprintln!(
                "Warning: failed to parse client version '{}'; skipping version comparison",
                client_version
            );
            return VersionMismatchSeverity::None;
        }
    };

    let server = match parse_version(server_version) {
        Some(v) => v,
        None => {
            eprintln!(
                "Warning: failed to parse server version '{}'; skipping version comparison",
                server_version
            );
            return VersionMismatchSeverity::None;
        }
    };

    // Check major version difference
    if client.0 != server.0 {
        return VersionMismatchSeverity::Major;
    }

    // Check if client minor version is higher than server
    if client.1 > server.1 {
        return VersionMismatchSeverity::Minor;
    }

    // Check if versions differ in minor or patch
    if client.1 != server.1 || client.2 != server.2 {
        return VersionMismatchSeverity::Patch;
    }

    VersionMismatchSeverity::None
}

/// Formats a human-readable message for the version check result.
fn format_version_message(
    client_version: &str,
    server_version: &str,
    severity: VersionMismatchSeverity,
) -> String {
    match severity {
        VersionMismatchSeverity::None => {
            format!("Version {} matches server", client_version)
        }
        VersionMismatchSeverity::Patch => {
            format!(
                "Version mismatch: client {} vs server {} (patch difference)",
                client_version, server_version
            )
        }
        VersionMismatchSeverity::Minor => {
            format!(
                "Warning: Client version {} is newer than server {} - some features may not work",
                client_version, server_version
            )
        }
        VersionMismatchSeverity::Major => {
            format!(
                "Error: Major version mismatch - client {} vs server {} - incompatible versions",
                client_version, server_version
            )
        }
    }
}

/// Fetches the server version from the API.
pub fn get_server_version(config: &Configuration) -> Option<String> {
    match default_api::get_version(config) {
        Ok(value) => {
            // The server returns the version as a JSON string
            if let Some(version) = value.as_str() {
                Some(version.to_string())
            } else {
                // Try to extract from object if wrapped
                value
                    .get("version")
                    .and_then(|v| v.as_str())
                    .map(|s| s.to_string())
            }
        }
        Err(_) => None,
    }
}

/// Performs a version check between the client and server.
pub fn check_version(config: &Configuration) -> VersionCheckResult {
    match get_server_version(config) {
        Some(server_version) => VersionCheckResult::new(CLIENT_VERSION, &server_version),
        None => VersionCheckResult::server_unreachable(),
    }
}

/// Prints a version warning to stderr if appropriate.
/// Returns the severity level for programmatic use.
pub fn print_version_warning(result: &VersionCheckResult) -> VersionMismatchSeverity {
    match result.severity {
        VersionMismatchSeverity::None => {}
        VersionMismatchSeverity::Patch => {
            eprintln!("Note: {}", result.message);
        }
        VersionMismatchSeverity::Minor => {
            eprintln!("Warning: {}", result.message);
        }
        VersionMismatchSeverity::Major => {
            eprintln!("Error: {}", result.message);
        }
    }
    result.severity
}

/// Checks the server version and prints appropriate warnings.
/// Returns true if the version check passed (no major incompatibility).
pub fn check_and_warn(config: &Configuration) -> bool {
    let result = check_version(config);
    let severity = print_version_warning(&result);
    !severity.is_blocking()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_version() {
        assert_eq!(parse_version("0.8.0"), Some((0, 8, 0)));
        assert_eq!(parse_version("1.2.3"), Some((1, 2, 3)));
        assert_eq!(parse_version("v1.2.3"), Some((1, 2, 3)));
        assert_eq!(parse_version("1.2.3-beta"), Some((1, 2, 3)));
        assert_eq!(parse_version("invalid"), None);
    }

    #[test]
    fn test_compare_versions_exact_match() {
        assert_eq!(
            compare_versions("0.8.0", "0.8.0"),
            VersionMismatchSeverity::None
        );
    }

    #[test]
    fn test_compare_versions_patch_diff() {
        assert_eq!(
            compare_versions("0.8.1", "0.8.0"),
            VersionMismatchSeverity::Patch
        );
        assert_eq!(
            compare_versions("0.8.0", "0.8.1"),
            VersionMismatchSeverity::Patch
        );
    }

    #[test]
    fn test_compare_versions_minor_client_higher() {
        assert_eq!(
            compare_versions("0.9.0", "0.8.0"),
            VersionMismatchSeverity::Minor
        );
    }

    #[test]
    fn test_compare_versions_minor_server_higher() {
        // Server being newer is just a patch-level concern
        assert_eq!(
            compare_versions("0.8.0", "0.9.0"),
            VersionMismatchSeverity::Patch
        );
    }

    #[test]
    fn test_compare_versions_major_diff() {
        assert_eq!(
            compare_versions("1.0.0", "0.8.0"),
            VersionMismatchSeverity::Major
        );
        assert_eq!(
            compare_versions("0.8.0", "1.0.0"),
            VersionMismatchSeverity::Major
        );
    }
}
