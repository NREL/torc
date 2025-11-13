//! Common API module with shared imports and traits

use log::{error, info};
use sqlx::sqlite::SqlitePool;
use std::sync::Arc;
use swagger::ApiError;
use tokio::sync::Mutex;

/// Common constants used across all API modules
pub const MAX_RECORD_TRANSFER_COUNT: i64 = 10_000;

/// Shared server context that all API modules can use
#[derive(Clone)]
pub struct ApiContext {
    pub pool: Arc<SqlitePool>,
    pub lock: Arc<Mutex<()>>,
}

impl ApiContext {
    pub fn new(pool: SqlitePool) -> Self {
        Self {
            pool: Arc::new(pool),
            lock: Arc::new(Mutex::new(())),
        }
    }
}

/// Common error handling utilities
pub fn database_error(e: impl std::fmt::Display) -> ApiError {
    error!("Database error: {}", e);
    ApiError("Database error".to_string())
}

pub fn json_parse_error(e: impl std::fmt::Display) -> ApiError {
    info!("Failed to parse JSON data: {}", e);
    ApiError("Failed to parse event data".to_string())
}

/// Common pagination response structure
#[derive(Debug)]
pub struct PaginationInfo {
    pub offset: i64,
    pub limit: Option<i64>,
    pub total_count: i64,
}

impl PaginationInfo {
    pub fn new(offset: Option<i64>, limit: Option<i64>, total_count: i64) -> Self {
        Self {
            offset: offset.unwrap_or(0),
            limit,
            total_count,
        }
    }

    pub fn has_more(&self) -> bool {
        if let Some(limit) = self.limit {
            self.offset + limit < self.total_count
        } else {
            false
        }
    }
}

// Re-export submodules
pub mod compute_nodes;
pub mod events;
pub mod files;
pub mod jobs;
pub mod resource_requirements;
pub mod results;
pub mod schedulers;
pub mod sql_query_builder;
pub mod user_data;
pub mod workflow_actions;
pub mod workflows;

// Re-export API traits and implementations
pub use compute_nodes::{ComputeNodesApi, ComputeNodesApiImpl};
pub use events::{EventsApi, EventsApiImpl};
pub use files::{FilesApi, FilesApiImpl};
pub use jobs::{JobsApi, JobsApiImpl};
pub use resource_requirements::{ResourceRequirementsApi, ResourceRequirementsApiImpl};
pub use results::{ResultsApi, ResultsApiImpl};
pub use schedulers::{SchedulersApi, SchedulersApiImpl};
pub use sql_query_builder::SqlQueryBuilder;
pub use user_data::{UserDataApi, UserDataApiImpl};
pub use workflow_actions::{WorkflowActionsApi, WorkflowActionsApiImpl};
pub use workflows::{WorkflowsApi, WorkflowsApiImpl};
