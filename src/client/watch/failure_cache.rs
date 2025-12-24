//! Failure pattern cache using SQLite.
//!
//! Caches failure diagnoses to avoid repeated API calls for similar failures.

use std::path::Path;

use log::{debug, warn};
use rusqlite::{Connection, params};
use sha2::{Digest, Sha256};

use super::claude_client::Diagnosis;

/// Cache for storing failure patterns and their diagnoses.
pub struct FailureCache {
    conn: Connection,
}

impl FailureCache {
    /// Open or create a failure cache database.
    pub fn open(path: &Path) -> Result<Self, String> {
        let conn =
            Connection::open(path).map_err(|e| format!("Failed to open cache database: {}", e))?;

        // Create tables if they don't exist
        conn.execute(
            r#"
            CREATE TABLE IF NOT EXISTS failure_patterns (
                id INTEGER PRIMARY KEY,
                job_name_pattern TEXT NOT NULL,
                error_signature TEXT NOT NULL,
                diagnosis_json TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                last_used_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(job_name_pattern, error_signature)
            )
            "#,
            [],
        )
        .map_err(|e| format!("Failed to create cache table: {}", e))?;

        // Create index for faster lookups
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_failure_patterns_lookup ON failure_patterns(job_name_pattern, error_signature)",
            [],
        )
        .map_err(|e| format!("Failed to create cache index: {}", e))?;

        Ok(Self { conn })
    }

    /// Compute an error signature from stderr content.
    ///
    /// This normalizes the error output by:
    /// 1. Extracting lines containing error keywords
    /// 2. Removing timestamps and PIDs
    /// 3. Hashing the result
    pub fn compute_signature(stderr: &str) -> String {
        let error_keywords = [
            "error",
            "Error",
            "ERROR",
            "exception",
            "Exception",
            "EXCEPTION",
            "failed",
            "Failed",
            "FAILED",
            "oom",
            "OOM",
            "Out of memory",
            "killed",
            "Killed",
            "KILLED",
            "timeout",
            "Timeout",
            "TIMEOUT",
            "cuda",
            "CUDA",
            "segfault",
            "Segmentation fault",
            "permission denied",
            "Permission denied",
            "not found",
            "No such file",
        ];

        let mut error_lines: Vec<String> = Vec::new();

        for line in stderr.lines() {
            let line_lower = line.to_lowercase();
            if error_keywords
                .iter()
                .any(|kw| line_lower.contains(&kw.to_lowercase()))
            {
                // Normalize the line: remove timestamps, PIDs, paths
                let normalized = normalize_error_line(line);
                if !normalized.is_empty() {
                    error_lines.push(normalized);
                }
            }
        }

        // If no error lines found, hash the last 20 lines
        if error_lines.is_empty() {
            error_lines = stderr
                .lines()
                .rev()
                .take(20)
                .map(|l| normalize_error_line(l))
                .filter(|l| !l.is_empty())
                .collect();
            error_lines.reverse();
        }

        // Compute hash
        let mut hasher = Sha256::new();
        for line in &error_lines {
            hasher.update(line.as_bytes());
            hasher.update(b"\n");
        }
        let result = hasher.finalize();
        format!("{:x}", result)
    }

    /// Look up a cached diagnosis for a failure pattern.
    pub fn lookup(
        &self,
        job_name: &str,
        error_signature: &str,
    ) -> Result<Option<Diagnosis>, String> {
        // Extract job name pattern (remove numeric suffixes like _001, _42, etc.)
        let job_pattern = extract_job_pattern(job_name);

        let result: Result<(String, i64, i64), _> = self.conn.query_row(
            r#"
            SELECT diagnosis_json, success_count, failure_count
            FROM failure_patterns
            WHERE job_name_pattern = ?1 AND error_signature = ?2
            "#,
            params![job_pattern, error_signature],
            |row| Ok((row.get(0)?, row.get(1)?, row.get(2)?)),
        );

        match result {
            Ok((json, success_count, failure_count)) => {
                // Update last_used_at
                let _ = self.conn.execute(
                    "UPDATE failure_patterns SET last_used_at = datetime('now') WHERE job_name_pattern = ?1 AND error_signature = ?2",
                    params![job_pattern, error_signature],
                );

                // Only use cache if success rate is reasonable
                let total = success_count + failure_count;
                if total > 0 && failure_count as f64 / total as f64 > 0.5 {
                    debug!(
                        "Cache hit for {} but success rate too low ({}/{}), skipping",
                        job_name, success_count, total
                    );
                    return Ok(None);
                }

                let diagnosis: Diagnosis = serde_json::from_str(&json)
                    .map_err(|e| format!("Failed to parse cached diagnosis: {}", e))?;

                debug!(
                    "Cache hit for {} (success: {}, failure: {})",
                    job_name, success_count, failure_count
                );
                Ok(Some(diagnosis))
            }
            Err(rusqlite::Error::QueryReturnedNoRows) => {
                debug!("Cache miss for {}", job_name);
                Ok(None)
            }
            Err(e) => Err(format!("Cache lookup failed: {}", e)),
        }
    }

    /// Store a diagnosis in the cache.
    pub fn store(
        &mut self,
        job_name: &str,
        error_signature: &str,
        diagnosis: &Diagnosis,
    ) -> Result<(), String> {
        let job_pattern = extract_job_pattern(job_name);
        let json = serde_json::to_string(diagnosis)
            .map_err(|e| format!("Failed to serialize diagnosis: {}", e))?;

        self.conn
            .execute(
                r#"
            INSERT INTO failure_patterns (job_name_pattern, error_signature, diagnosis_json)
            VALUES (?1, ?2, ?3)
            ON CONFLICT(job_name_pattern, error_signature) DO UPDATE SET
                diagnosis_json = ?3,
                last_used_at = datetime('now')
            "#,
                params![job_pattern, error_signature, json],
            )
            .map_err(|e| format!("Failed to store diagnosis: {}", e))?;

        debug!("Cached diagnosis for {}", job_name);
        Ok(())
    }

    /// Record a successful recovery using a cached diagnosis.
    pub fn record_success(&self, job_name: &str, error_signature: &str) {
        let job_pattern = extract_job_pattern(job_name);
        if let Err(e) = self.conn.execute(
            "UPDATE failure_patterns SET success_count = success_count + 1 WHERE job_name_pattern = ?1 AND error_signature = ?2",
            params![job_pattern, error_signature],
        ) {
            warn!("Failed to record cache success: {}", e);
        }
    }

    /// Record a failed recovery attempt.
    pub fn record_failure(&self, job_name: &str, error_signature: &str) {
        let job_pattern = extract_job_pattern(job_name);
        if let Err(e) = self.conn.execute(
            "UPDATE failure_patterns SET failure_count = failure_count + 1 WHERE job_name_pattern = ?1 AND error_signature = ?2",
            params![job_pattern, error_signature],
        ) {
            warn!("Failed to record cache failure: {}", e);
        }
    }

    /// Get cache statistics.
    #[allow(dead_code)]
    pub fn stats(&self) -> Result<CacheStats, String> {
        let total_entries: i64 = self
            .conn
            .query_row("SELECT COUNT(*) FROM failure_patterns", [], |row| {
                row.get(0)
            })
            .map_err(|e| format!("Failed to get cache stats: {}", e))?;

        let total_successes: i64 = self
            .conn
            .query_row(
                "SELECT COALESCE(SUM(success_count), 0) FROM failure_patterns",
                [],
                |row| row.get(0),
            )
            .map_err(|e| format!("Failed to get success count: {}", e))?;

        let total_failures: i64 = self
            .conn
            .query_row(
                "SELECT COALESCE(SUM(failure_count), 0) FROM failure_patterns",
                [],
                |row| row.get(0),
            )
            .map_err(|e| format!("Failed to get failure count: {}", e))?;

        Ok(CacheStats {
            total_entries: total_entries as usize,
            total_successes: total_successes as usize,
            total_failures: total_failures as usize,
        })
    }
}

/// Cache statistics.
#[derive(Debug)]
pub struct CacheStats {
    pub total_entries: usize,
    pub total_successes: usize,
    pub total_failures: usize,
}

/// Normalize an error line by removing timestamps, PIDs, and paths.
fn normalize_error_line(line: &str) -> String {
    let mut result = line.to_string();

    // Remove timestamps (various formats)
    // ISO: 2024-01-15T10:30:45
    // Common: [2024-01-15 10:30:45], Jan 15 10:30:45
    let timestamp_patterns = [
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?",
        r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]",
        r"[A-Z][a-z]{2} \d{1,2} \d{2}:\d{2}:\d{2}",
    ];
    for pattern in timestamp_patterns {
        if let Ok(re) = regex::Regex::new(pattern) {
            result = re.replace_all(&result, "[TIME]").to_string();
        }
    }

    // Remove PIDs
    if let Ok(re) = regex::Regex::new(r"\bpid[=: ]?\d+\b|\bPID[=: ]?\d+\b|\[\d+\]") {
        result = re.replace_all(&result, "[PID]").to_string();
    }

    // Remove absolute paths but keep the filename
    if let Ok(re) = regex::Regex::new(r"/[^\s:]+/([^\s/:]+)") {
        result = re.replace_all(&result, "[PATH]/$1").to_string();
    }

    // Remove memory addresses
    if let Ok(re) = regex::Regex::new(r"0x[0-9a-fA-F]+") {
        result = re.replace_all(&result, "[ADDR]").to_string();
    }

    // Trim whitespace
    result.trim().to_string()
}

/// Extract a job name pattern by removing numeric suffixes.
fn extract_job_pattern(job_name: &str) -> String {
    // Remove common numeric suffixes like _001, _42, -1, etc.
    if let Ok(re) = regex::Regex::new(r"[_-]\d+$") {
        re.replace(job_name, "[N]").to_string()
    } else {
        job_name.to_string()
    }
}
