//! Claude API client for failure diagnosis.

use log::debug;
use serde::{Deserialize, Serialize};

use crate::client::apis::configuration::Configuration;
use crate::models::JobModel;

use super::recovery::RecoveryAction;

const CLAUDE_API_URL: &str = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_VERSION: &str = "2023-06-01";

/// Diagnosis result from Claude.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Diagnosis {
    /// Summary of the failure
    pub summary: String,
    /// Root cause analysis
    pub root_cause: Option<String>,
    /// Recommended recovery action
    pub recommended_action: Option<RecoveryAction>,
    /// Confidence level (0.0 - 1.0)
    pub confidence: f64,
    /// Additional notes or suggestions
    pub notes: Option<String>,
}

/// Claude API client for diagnosing job failures.
pub struct ClaudeClient {
    api_key: String,
    model: String,
    client: reqwest::blocking::Client,
}

impl ClaudeClient {
    /// Create a new Claude client.
    pub fn new(api_key: String, model: String) -> Self {
        Self {
            api_key,
            model,
            client: reqwest::blocking::Client::new(),
        }
    }

    /// Diagnose a job failure using Claude.
    pub fn diagnose_failure(
        &self,
        config: &Configuration,
        workflow_id: i64,
        job: &JobModel,
        stdout: &str,
        stderr: &str,
    ) -> Result<Diagnosis, String> {
        let job_id = job.id.ok_or("Job has no ID")?;
        let job_name = job.name.clone();
        let command = job.command.clone();

        // Build the prompt
        let prompt =
            self.build_diagnosis_prompt(workflow_id, job_id, &job_name, &command, stdout, stderr);

        // Get tools definition
        let tools = self.get_tools_definition();

        // Make API request
        let request_body = serde_json::json!({
            "model": self.model,
            "max_tokens": 4096,
            "tools": tools,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "system": self.get_system_prompt()
        });

        debug!("Sending request to Claude API");
        let response = self
            .client
            .post(CLAUDE_API_URL)
            .header("Content-Type", "application/json")
            .header("x-api-key", &self.api_key)
            .header("anthropic-version", ANTHROPIC_VERSION)
            .json(&request_body)
            .send()
            .map_err(|e| format!("Failed to send request to Claude API: {}", e))?;

        if !response.status().is_success() {
            let status = response.status();
            let body = response
                .text()
                .unwrap_or_else(|_| "unknown error".to_string());
            return Err(format!("Claude API error ({}): {}", status, body));
        }

        let response_body: ClaudeResponse = response
            .json()
            .map_err(|e| format!("Failed to parse Claude API response: {}", e))?;

        // Parse the response
        self.parse_response(&response_body, config, workflow_id)
    }

    fn get_system_prompt(&self) -> &'static str {
        r#"You are an expert HPC workflow failure diagnostician. Your job is to analyze job failures from workflow orchestration systems and recommend recovery actions.

When analyzing a failure:
1. Look for common error patterns (OOM, timeout, missing files, permission errors, CUDA errors, etc.)
2. Consider the job's resource requirements vs actual usage
3. Recommend specific, actionable recovery steps

Available recovery actions:
- restart: Restart the job with no changes (for transient failures)
- restart_with_resources: Restart with modified resource requirements (memory, CPUs, runtime)
- cancel: Cancel the job and its dependents (for unrecoverable failures)
- skip: Mark as completed and continue (for optional jobs)

Always provide:
1. A clear summary of what went wrong
2. Root cause analysis when possible
3. A specific recovery action with parameters
4. Confidence level in your diagnosis

Use the diagnose_failure tool to report your findings."#
    }

    fn build_diagnosis_prompt(
        &self,
        workflow_id: i64,
        job_id: i64,
        job_name: &str,
        command: &str,
        stdout: &str,
        stderr: &str,
    ) -> String {
        format!(
            r#"Please diagnose the following job failure and recommend a recovery action.

## Job Information
- Workflow ID: {}
- Job ID: {}
- Job Name: {}
- Command: {}

## Standard Output (last 10KB)
```
{}
```

## Standard Error (last 10KB)
```
{}
```

Analyze this failure and use the diagnose_failure tool to report your findings."#,
            workflow_id, job_id, job_name, command, stdout, stderr
        )
    }

    fn get_tools_definition(&self) -> serde_json::Value {
        serde_json::json!([
            {
                "name": "diagnose_failure",
                "description": "Report the diagnosis of a job failure with recommended recovery action",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "Brief summary of what went wrong (1-2 sentences)"
                        },
                        "root_cause": {
                            "type": "string",
                            "description": "Detailed root cause analysis"
                        },
                        "action_type": {
                            "type": "string",
                            "enum": ["restart", "restart_with_resources", "cancel", "skip", "none"],
                            "description": "Type of recovery action to take"
                        },
                        "new_memory": {
                            "type": "string",
                            "description": "New memory requirement (e.g., '8g', '16g') for restart_with_resources"
                        },
                        "new_runtime": {
                            "type": "string",
                            "description": "New runtime limit (e.g., 'PT2H', 'PT4H') for restart_with_resources"
                        },
                        "new_num_cpus": {
                            "type": "integer",
                            "description": "New CPU count for restart_with_resources"
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence in the diagnosis (0.0 to 1.0)"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes or suggestions"
                        }
                    },
                    "required": ["summary", "action_type", "confidence"]
                }
            }
        ])
    }

    fn parse_response(
        &self,
        response: &ClaudeResponse,
        _config: &Configuration,
        _workflow_id: i64,
    ) -> Result<Diagnosis, String> {
        // Find tool use in response
        for content in &response.content {
            if content.content_type == "tool_use"
                && content.name.as_deref() == Some("diagnose_failure")
            {
                let input = content.input.as_ref().ok_or("Tool use has no input")?;

                let summary = input
                    .get("summary")
                    .and_then(|v| v.as_str())
                    .ok_or("Missing summary in diagnosis")?
                    .to_string();

                let root_cause = input
                    .get("root_cause")
                    .and_then(|v| v.as_str())
                    .map(|s| s.to_string());

                let action_type = input
                    .get("action_type")
                    .and_then(|v| v.as_str())
                    .unwrap_or("none");

                let confidence = input
                    .get("confidence")
                    .and_then(|v| v.as_f64())
                    .unwrap_or(0.5);

                let notes = input
                    .get("notes")
                    .and_then(|v| v.as_str())
                    .map(|s| s.to_string());

                let recommended_action = match action_type {
                    "restart" => Some(RecoveryAction::Restart),
                    "restart_with_resources" => {
                        let new_memory = input
                            .get("new_memory")
                            .and_then(|v| v.as_str())
                            .map(|s| s.to_string());
                        let new_runtime = input
                            .get("new_runtime")
                            .and_then(|v| v.as_str())
                            .map(|s| s.to_string());
                        let new_num_cpus = input.get("new_num_cpus").and_then(|v| v.as_i64());

                        Some(RecoveryAction::RestartWithResources {
                            memory: new_memory,
                            runtime: new_runtime,
                            num_cpus: new_num_cpus,
                        })
                    }
                    "cancel" => Some(RecoveryAction::Cancel),
                    "skip" => Some(RecoveryAction::Skip),
                    _ => None,
                };

                return Ok(Diagnosis {
                    summary,
                    root_cause,
                    recommended_action,
                    confidence,
                    notes,
                });
            }
        }

        // If no tool use found, try to extract from text
        for content in &response.content {
            if content.content_type == "text" {
                if let Some(text) = &content.text {
                    return Ok(Diagnosis {
                        summary: text.chars().take(200).collect(),
                        root_cause: None,
                        recommended_action: None,
                        confidence: 0.3,
                        notes: Some("Could not parse structured response from Claude".to_string()),
                    });
                }
            }
        }

        Err("No diagnosis found in Claude response".to_string())
    }
}

/// Claude API response structure.
#[derive(Debug, Deserialize)]
struct ClaudeResponse {
    content: Vec<ContentBlock>,
    #[allow(dead_code)]
    model: String,
    #[allow(dead_code)]
    stop_reason: Option<String>,
}

#[derive(Debug, Deserialize)]
struct ContentBlock {
    #[serde(rename = "type")]
    content_type: String,
    text: Option<String>,
    name: Option<String>,
    input: Option<serde_json::Value>,
}
