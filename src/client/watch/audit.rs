//! Audit logging for watch command actions.

use std::fs::{File, OpenOptions};
use std::io::{BufWriter, Write};
use std::path::Path;

use chrono::Utc;
use log::warn;
use serde::Serialize;

use super::claude_client::Diagnosis;
use super::recovery::RecoveryAction;

/// Audit logger for recording all watch command actions.
pub struct AuditLogger {
    writer: BufWriter<File>,
}

impl AuditLogger {
    /// Create a new audit logger writing to the specified file.
    pub fn new(path: &Path) -> Result<Self, String> {
        // Create parent directories if needed
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)
                .map_err(|e| format!("Failed to create audit log directory: {}", e))?;
        }

        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)
            .map_err(|e| format!("Failed to open audit log: {}", e))?;

        Ok(Self {
            writer: BufWriter::new(file),
        })
    }

    /// Log a diagnosis event.
    pub fn log_diagnosis(&mut self, job_id: i64, job_name: &str, diagnosis: &Diagnosis) {
        let entry = AuditEntry {
            timestamp: Utc::now().to_rfc3339(),
            event_type: "diagnosis".to_string(),
            job_id,
            job_name: job_name.to_string(),
            summary: Some(diagnosis.summary.clone()),
            root_cause: diagnosis.root_cause.clone(),
            recommended_action: diagnosis.recommended_action.clone(),
            confidence: Some(diagnosis.confidence),
            action_taken: None,
            action_success: None,
            notes: diagnosis.notes.clone(),
        };

        self.write_entry(&entry);
    }

    /// Log a recovery action event.
    pub fn log_recovery(
        &mut self,
        job_id: i64,
        job_name: &str,
        action: &RecoveryAction,
        success: bool,
    ) {
        let entry = AuditEntry {
            timestamp: Utc::now().to_rfc3339(),
            event_type: "recovery".to_string(),
            job_id,
            job_name: job_name.to_string(),
            summary: None,
            root_cause: None,
            recommended_action: None,
            confidence: None,
            action_taken: Some(action.clone()),
            action_success: Some(success),
            notes: None,
        };

        self.write_entry(&entry);
    }

    /// Log an arbitrary event.
    #[allow(dead_code)]
    pub fn log_event(
        &mut self,
        event_type: &str,
        job_id: i64,
        job_name: &str,
        notes: Option<String>,
    ) {
        let entry = AuditEntry {
            timestamp: Utc::now().to_rfc3339(),
            event_type: event_type.to_string(),
            job_id,
            job_name: job_name.to_string(),
            summary: None,
            root_cause: None,
            recommended_action: None,
            confidence: None,
            action_taken: None,
            action_success: None,
            notes,
        };

        self.write_entry(&entry);
    }

    fn write_entry(&mut self, entry: &AuditEntry) {
        let json = match serde_json::to_string(entry) {
            Ok(j) => j,
            Err(e) => {
                warn!("Failed to serialize audit entry: {}", e);
                return;
            }
        };

        if let Err(e) = writeln!(self.writer, "{}", json) {
            warn!("Failed to write audit entry: {}", e);
        }

        // Flush after each entry to ensure logs are written
        if let Err(e) = self.writer.flush() {
            warn!("Failed to flush audit log: {}", e);
        }
    }
}

/// A single audit log entry (JSON lines format).
#[derive(Debug, Serialize)]
struct AuditEntry {
    timestamp: String,
    event_type: String,
    job_id: i64,
    job_name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    summary: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    root_cause: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    recommended_action: Option<RecoveryAction>,
    #[serde(skip_serializing_if = "Option::is_none")]
    confidence: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    action_taken: Option<RecoveryAction>,
    #[serde(skip_serializing_if = "Option::is_none")]
    action_success: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    notes: Option<String>,
}
