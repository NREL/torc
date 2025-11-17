use crate::client::apis::configuration::Configuration;
use crate::client::apis::default_api;
use crate::models::{
    EventModel, FileModel, JobDependencyModel, JobModel, ResultModel, WorkflowModel,
};
use anyhow::{Context, Result};
use std::env;

pub struct TorcClient {
    config: Configuration,
}

impl TorcClient {
    pub fn new() -> Result<Self> {
        let base_url = env::var("TORC_API_URL")
            .unwrap_or_else(|_| "http://localhost:8080/torc-service/v1".to_string());

        let config = Configuration {
            base_path: base_url,
            ..Default::default()
        };

        Ok(Self { config })
    }

    pub fn from_url(base_url: String) -> Result<Self> {
        let config = Configuration {
            base_path: base_url,
            ..Default::default()
        };

        Ok(Self { config })
    }

    pub fn get_base_url(&self) -> &str {
        &self.config.base_path
    }

    pub fn list_workflows(&self) -> Result<Vec<WorkflowModel>> {
        let response = default_api::list_workflows(
            &self.config,
            None, // offset
            None, // sort_by
            None, // reverse_sort
            None, // limit
            None, // name
            None, // user
            None, // description
            None, // is_archived
        )
        .context("Failed to list workflows")?;

        Ok(response.items.unwrap_or_default())
    }

    pub fn list_workflows_for_user(&self, user: &str) -> Result<Vec<WorkflowModel>> {
        let response = default_api::list_workflows(
            &self.config,
            None,       // offset
            None,       // sort_by
            None,       // reverse_sort
            None,       // limit
            None,       // name
            Some(user), // user filter
            None,       // description
            None,       // is_archived
        )
        .context("Failed to list workflows")?;

        Ok(response.items.unwrap_or_default())
    }

    pub fn list_jobs(&self, workflow_id: i64) -> Result<Vec<JobModel>> {
        let response = default_api::list_jobs(
            &self.config,
            workflow_id,
            None, // status
            None, // needs_file_id
            None, // upstream_job_id
            None, // offset
            None, // limit
            None, // sort_by
            None, // reverse_sort
        )
        .context("Failed to list jobs")?;

        Ok(response.items.unwrap_or_default())
    }

    pub fn list_files(&self, workflow_id: i64) -> Result<Vec<FileModel>> {
        let response = default_api::list_files(
            &self.config,
            workflow_id,
            None, // produced_by_job_id
            None, // offset
            None, // limit
            None, // sort_by
            None, // reverse_sort
            None, // name
            None, // path
        )
        .context("Failed to list files")?;

        Ok(response.items.unwrap_or_default())
    }

    pub fn list_events(&self, workflow_id: i64) -> Result<Vec<EventModel>> {
        let response = default_api::list_events(
            &self.config,
            workflow_id,
            None, // offset
            None, // limit
            None, // sort_by
            None, // reverse_sort
            None, // category
            None, // after_timestamp
        )
        .context("Failed to list events")?;

        Ok(response.items.unwrap_or_default())
    }

    pub fn list_results(&self, workflow_id: i64) -> Result<Vec<ResultModel>> {
        let response = default_api::list_results(
            &self.config,
            workflow_id,
            None, // job_id
            None, // run_id
            None, // return_code
            None, // status
            None, // offset
            None, // limit
            None, // sort_by
            None, // reverse_sort
            None, // all_runs
        )
        .context("Failed to list results")?;

        Ok(response.items.unwrap_or_default())
    }

    pub fn list_job_dependencies(&self, workflow_id: i64) -> Result<Vec<JobDependencyModel>> {
        let response = default_api::list_job_dependencies(
            &self.config,
            workflow_id,
            None, // offset
            None, // limit
        )
        .context("Failed to list job dependencies")?;

        Ok(response.items.unwrap_or_default())
    }
}
