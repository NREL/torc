//! Tests for version checking utilities.

use torc::client::version_check::{VersionMismatchSeverity, compare_versions, parse_version};

#[test]
fn test_parse_version() {
    assert_eq!(parse_version("0.8.0"), Some((0, 8, 0)));
    assert_eq!(parse_version("1.2.3"), Some((1, 2, 3)));
    assert_eq!(parse_version("v1.2.3"), Some((1, 2, 3)));
    assert_eq!(parse_version("1.2.3-beta"), Some((1, 2, 3)));
    // Versions with git hash suffix
    assert_eq!(parse_version("0.8.0 (abc1234)"), Some((0, 8, 0)));
    assert_eq!(parse_version("0.8.0 (abc1234-dirty)"), Some((0, 8, 0)));
    assert_eq!(parse_version("v1.2.3 (def5678)"), Some((1, 2, 3)));
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
