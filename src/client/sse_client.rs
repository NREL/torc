//! SSE (Server-Sent Events) client for real-time event streaming.
//!
//! This module provides a client for connecting to the SSE endpoint and
//! receiving real-time job events from the server.

use crate::client::apis::configuration::Configuration;
use serde::{Deserialize, Serialize};
use std::io::{BufRead, BufReader};
use std::time::Duration;

/// A broadcast event received from the SSE stream.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SseEvent {
    /// The workflow ID this event belongs to.
    pub workflow_id: i64,
    /// Timestamp in milliseconds since Unix epoch.
    pub timestamp: i64,
    /// The type of event (e.g., "job_started", "job_completed", "job_failed").
    pub event_type: String,
    /// Event-specific data as JSON.
    pub data: serde_json::Value,
}

/// Error type for SSE client operations.
#[derive(Debug)]
pub enum SseError {
    /// HTTP request failed
    Request(reqwest::Error),
    /// Failed to parse event data
    Parse(String),
    /// Connection closed
    ConnectionClosed,
    /// IO error
    Io(std::io::Error),
}

impl std::fmt::Display for SseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SseError::Request(e) => write!(f, "Request error: {}", e),
            SseError::Parse(e) => write!(f, "Parse error: {}", e),
            SseError::ConnectionClosed => write!(f, "Connection closed"),
            SseError::Io(e) => write!(f, "IO error: {}", e),
        }
    }
}

impl std::error::Error for SseError {}

impl From<reqwest::Error> for SseError {
    fn from(e: reqwest::Error) -> Self {
        SseError::Request(e)
    }
}

impl From<std::io::Error> for SseError {
    fn from(e: std::io::Error) -> Self {
        SseError::Io(e)
    }
}

/// SSE connection that streams events from the server.
pub struct SseConnection {
    reader: BufReader<Box<dyn std::io::Read + Send>>,
}

impl SseConnection {
    /// Connect to the SSE endpoint for a workflow.
    ///
    /// This establishes a blocking HTTP connection to the SSE endpoint
    /// and returns a connection that can be used to receive events.
    pub fn connect(config: &Configuration, workflow_id: i64) -> Result<Self, SseError> {
        let url = format!(
            "{}/workflows/{}/events/stream",
            config.base_path, workflow_id
        );

        // Use blocking client for simplicity
        let client = reqwest::blocking::Client::builder()
            .timeout(None) // No timeout for SSE connection
            .build()?;

        let response = client
            .get(&url)
            .header("Accept", "text/event-stream")
            .send()?;

        if !response.status().is_success() {
            return Err(SseError::Parse(format!(
                "Server returned error status: {}",
                response.status()
            )));
        }

        // Convert the response body into a reader
        let reader = BufReader::new(Box::new(response) as Box<dyn std::io::Read + Send>);

        Ok(SseConnection { reader })
    }

    /// Read the next event from the SSE stream.
    ///
    /// Returns `Some(event)` if an event was received, or `None` if the connection
    /// was closed.
    pub fn next_event(&mut self) -> Result<Option<SseEvent>, SseError> {
        let mut event_type = String::new();
        let mut data = String::new();

        loop {
            let mut line = String::new();
            let bytes_read = self.reader.read_line(&mut line)?;

            if bytes_read == 0 {
                // Connection closed
                return Ok(None);
            }

            let line = line.trim_end();

            if line.is_empty() {
                // Empty line marks end of event
                if !data.is_empty() {
                    // Parse the event
                    match serde_json::from_str::<SseEvent>(&data) {
                        Ok(mut event) => {
                            // Override event_type if we got one from the SSE event: field
                            if !event_type.is_empty() {
                                event.event_type = event_type;
                            }
                            return Ok(Some(event));
                        }
                        Err(e) => {
                            // Try to handle warning events
                            if event_type == "warning" {
                                return Ok(Some(SseEvent {
                                    workflow_id: 0,
                                    timestamp: chrono::Utc::now().timestamp_millis(),
                                    event_type: "warning".to_string(),
                                    data: serde_json::from_str(&data)
                                        .unwrap_or(serde_json::json!({"raw": data})),
                                }));
                            }
                            return Err(SseError::Parse(format!(
                                "Failed to parse event data: {} - data: {}",
                                e, data
                            )));
                        }
                    }
                }
                // Reset for next event
                event_type.clear();
                data.clear();
                continue;
            }

            if let Some(value) = line.strip_prefix("event: ") {
                event_type = value.to_string();
            } else if let Some(value) = line.strip_prefix("data: ") {
                if !data.is_empty() {
                    data.push('\n');
                }
                data.push_str(value);
            }
            // Ignore other fields (id:, retry:, etc.)
        }
    }
}

/// Connect to the SSE endpoint and process events with a callback.
///
/// This is a convenience function that handles the connection loop and
/// calls the provided callback for each received event.
pub fn stream_events<F>(
    config: &Configuration,
    workflow_id: i64,
    duration: Option<Duration>,
    mut callback: F,
) -> Result<(), SseError>
where
    F: FnMut(SseEvent),
{
    let mut connection = SseConnection::connect(config, workflow_id)?;
    let start = std::time::Instant::now();

    loop {
        // Check duration timeout
        if let Some(max_duration) = duration
            && start.elapsed() >= max_duration
        {
            return Ok(());
        }

        match connection.next_event()? {
            Some(event) => callback(event),
            None => return Err(SseError::ConnectionClosed),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sse_event_deserialize() {
        let json = r#"{
            "workflow_id": 123,
            "timestamp": 1234567890,
            "event_type": "job_started",
            "data": {"job_id": 42}
        }"#;

        let event: SseEvent = serde_json::from_str(json).unwrap();
        assert_eq!(event.workflow_id, 123);
        assert_eq!(event.event_type, "job_started");
    }
}
