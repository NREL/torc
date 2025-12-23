//! Job pagination functionality.
//!
//! This module provides lazy iteration and vector collection support for jobs.
//! It includes both simple iterators that work with the real API and mock iterators
//! for testing purposes.

use crate::client::apis;
use crate::models::*;

/// Parameters for listing jobs with default values and builder methods.
///
/// This struct provides a clean way to specify filtering and pagination
/// parameters for job queries. All fields have sensible defaults:
/// - `offset` defaults to 0 (start from beginning)
/// - All other fields default to `None` (no filtering)
///
#[derive(Debug, Clone)]
pub struct JobListParams {
    pub status: Option<JobStatus>,
    pub needs_file_id: Option<i64>,
    pub upstream_job_id: Option<i64>,
    pub offset: i64,
    pub limit: Option<i64>,
    pub sort_by: Option<String>,
    pub reverse_sort: Option<bool>,
    pub include_relationships: Option<bool>,
    pub active_compute_node_id: Option<i64>,
}

impl Default for JobListParams {
    fn default() -> Self {
        Self {
            status: None,
            needs_file_id: None,
            upstream_job_id: None,
            offset: 0,
            limit: None,
            sort_by: None,
            reverse_sort: None,
            include_relationships: None,
            active_compute_node_id: None,
        }
    }
}

// Builder methods for JobListParams
impl JobListParams {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn with_status(mut self, status: JobStatus) -> Self {
        self.status = Some(status);
        self
    }

    pub fn with_needs_file_id(mut self, file_id: i64) -> Self {
        self.needs_file_id = Some(file_id);
        self
    }

    pub fn with_upstream_job_id(mut self, job_id: i64) -> Self {
        self.upstream_job_id = Some(job_id);
        self
    }

    pub fn with_offset(mut self, offset: i64) -> Self {
        self.offset = offset;
        self
    }

    pub fn with_limit(mut self, limit: i64) -> Self {
        self.limit = Some(limit);
        self
    }

    pub fn with_sort_by(mut self, sort_by: String) -> Self {
        self.sort_by = Some(sort_by);
        self
    }

    pub fn with_reverse_sort(mut self, reverse: bool) -> Self {
        self.reverse_sort = Some(reverse);
        self
    }

    pub fn with_include_relationships(mut self, include: bool) -> Self {
        self.include_relationships = Some(include);
        self
    }
}

/// Iterator for jobs with lazy pagination
pub struct JobsIterator {
    config: apis::configuration::Configuration,
    workflow_id: i64,
    params: JobListParams,
    remaining_limit: i64,
    initial_limit: i64,
    current_page: std::vec::IntoIter<JobModel>,
    finished: bool,
}

impl JobsIterator {
    pub fn new(
        config: apis::configuration::Configuration,
        workflow_id: i64,
        params: JobListParams,
        initial_limit: Option<i64>,
    ) -> Self {
        let remaining_limit = params.limit.unwrap_or(i64::MAX);
        Self {
            config,
            workflow_id,
            params,
            remaining_limit,
            initial_limit: initial_limit.unwrap_or(1000),
            current_page: Vec::new().into_iter(),
            finished: false,
        }
    }

    fn fetch_next_page(&mut self) -> Result<bool, apis::Error<apis::default_api::ListJobsError>> {
        if self.finished || (self.remaining_limit != i64::MAX && self.remaining_limit <= 0) {
            return Ok(false);
        }

        let page_limit = std::cmp::min(self.remaining_limit, self.initial_limit);
        let response = apis::default_api::list_jobs(
            &self.config,
            self.workflow_id,
            self.params.status,
            self.params.needs_file_id,
            self.params.upstream_job_id,
            Some(self.params.offset),
            Some(page_limit),
            self.params.sort_by.as_deref(),
            self.params.reverse_sort,
            self.params.include_relationships,
            self.params.active_compute_node_id,
        )?;

        if let Some(items) = response.items {
            let items_to_take = if self.remaining_limit == i64::MAX {
                items.len()
            } else {
                std::cmp::min(items.len() as i64, self.remaining_limit) as usize
            };
            let taken_items: Vec<JobModel> = items.into_iter().take(items_to_take).collect();
            if self.remaining_limit != i64::MAX {
                self.remaining_limit -= taken_items.len() as i64;
            }
            self.params.offset += taken_items.len() as i64;
            self.current_page = taken_items.into_iter();

            if !response.has_more || (self.remaining_limit != i64::MAX && self.remaining_limit <= 0)
            {
                self.finished = true;
            }
            Ok(true)
        } else {
            self.finished = true;
            Ok(false)
        }
    }
}

impl Iterator for JobsIterator {
    type Item = Result<JobModel, apis::Error<apis::default_api::ListJobsError>>;

    fn next(&mut self) -> Option<Self::Item> {
        // Try to get next item from current page
        if let Some(item) = self.current_page.next() {
            return Some(Ok(item));
        }

        // If current page is exhausted, try to fetch next page
        if !self.finished {
            match self.fetch_next_page() {
                Ok(true) => self.current_page.next().map(Ok),
                Ok(false) => None,
                Err(e) => Some(Err(e)),
            }
        } else {
            None
        }
    }
}

/// Create a lazy iterator for jobs that fetches pages on-demand.
///
/// This is the main API function for iterating over jobs. It provides a simple,
/// clean interface that handles all the API call details internally.
///
/// This is memory efficient as it only loads one page at a time.
/// Use this when you want to process items one by one without
/// loading all items into memory at once.
///
/// # Arguments
/// * `config` - API configuration containing base URL and authentication
/// * `workflow_id` - ID of the workflow to list jobs from  
/// * `params` - JobListParams containing filter and pagination parameters
///
/// # Returns
/// An iterator that yields `Result<JobModel, Error>` items
///
pub fn iter_jobs(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: JobListParams,
) -> JobsIterator {
    JobsIterator::new(config.clone(), workflow_id, params, None)
}

/// Collect all jobs into a vector using lazy iteration internally.
///
/// This function uses `iter_jobs` internally and collects all results.
/// Use this when you need all items in memory at once for batch processing
/// or when you need to know the total count before processing.
///
/// # Arguments
/// * `config` - API configuration containing base URL and authentication
/// * `workflow_id` - ID of the workflow to list jobs from
/// * `params` - JobListParams containing filter and pagination parameters
///
/// # Returns
/// `Result<Vec<JobModel>, Error>` containing all jobs or an error
///
pub fn paginate_jobs(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: JobListParams,
) -> Result<Vec<JobModel>, apis::Error<apis::default_api::ListJobsError>> {
    iter_jobs(config, workflow_id, params).collect()
}
