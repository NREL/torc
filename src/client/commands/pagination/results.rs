//! Result pagination functionality.
//!
//! This module provides lazy iteration and vector collection support for results.
//! It includes both simple iterators that work with the real API and mock iterators
//! for testing purposes.

use crate::client::apis;
use crate::models::*;

/// Parameters for listing results with default values and builder methods.
///
/// This struct provides a clean way to specify filtering and pagination
/// parameters for result queries. All fields have sensible defaults:
/// - `offset` defaults to 0 (start from beginning)
/// - All other fields default to `None` (no filtering)
///
#[derive(Debug, Clone)]
pub struct ResultListParams {
    pub job_id: Option<i64>,
    pub run_id: Option<i64>,
    pub offset: i64,
    pub limit: Option<i64>,
    pub sort_by: Option<String>,
    pub reverse_sort: Option<bool>,
    pub return_code: Option<i64>,
    pub status: Option<JobStatus>,
    pub all_runs: Option<bool>,
    pub compute_node_id: Option<i64>,
}

impl Default for ResultListParams {
    fn default() -> Self {
        Self {
            job_id: None,
            run_id: None,
            offset: 0,
            limit: None,
            sort_by: None,
            reverse_sort: None,
            return_code: None,
            status: None,
            all_runs: None,
            compute_node_id: None,
        }
    }
}

// Builder methods for ResultListParams
impl ResultListParams {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn with_job_id(mut self, job_id: i64) -> Self {
        self.job_id = Some(job_id);
        self
    }

    pub fn with_run_id(mut self, run_id: i64) -> Self {
        self.run_id = Some(run_id);
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

    pub fn with_return_code(mut self, return_code: i64) -> Self {
        self.return_code = Some(return_code);
        self
    }

    pub fn with_status(mut self, status: JobStatus) -> Self {
        self.status = Some(status);
        self
    }

    pub fn with_all_runs(mut self, all_runs: bool) -> Self {
        self.all_runs = Some(all_runs);
        self
    }

    pub fn with_compute_node_id(mut self, compute_node_id: i64) -> Self {
        self.compute_node_id = Some(compute_node_id);
        self
    }
}

/// Iterator for results with lazy pagination
pub struct ResultsIterator {
    config: apis::configuration::Configuration,
    workflow_id: i64,
    params: ResultListParams,
    remaining_limit: i64,
    initial_limit: i64,
    current_page: std::vec::IntoIter<ResultModel>,
    finished: bool,
}

impl ResultsIterator {
    pub fn new(
        config: apis::configuration::Configuration,
        workflow_id: i64,
        params: ResultListParams,
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

    fn fetch_next_page(
        &mut self,
    ) -> Result<bool, apis::Error<apis::default_api::ListResultsError>> {
        if self.finished || (self.remaining_limit != i64::MAX && self.remaining_limit <= 0) {
            return Ok(false);
        }

        let page_limit = std::cmp::min(self.remaining_limit, self.initial_limit);
        let response = apis::default_api::list_results(
            &self.config,
            self.workflow_id,
            self.params.job_id,
            self.params.run_id,
            Some(self.params.offset),
            Some(page_limit),
            self.params.sort_by.as_deref(),
            self.params.reverse_sort,
            self.params.return_code,
            self.params.status,
            self.params.all_runs,
            self.params.compute_node_id,
        )?;

        if let Some(items) = response.items {
            let items_to_take = if self.remaining_limit == i64::MAX {
                items.len()
            } else {
                std::cmp::min(items.len() as i64, self.remaining_limit) as usize
            };
            let taken_items: Vec<ResultModel> = items.into_iter().take(items_to_take).collect();
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

impl Iterator for ResultsIterator {
    type Item = Result<ResultModel, apis::Error<apis::default_api::ListResultsError>>;

    fn next(&mut self) -> Option<Self::Item> {
        if let Some(item) = self.current_page.next() {
            return Some(Ok(item));
        }

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

/// Create a lazy iterator for results that fetches pages on-demand.
///
/// This is the main API function for iterating over results. It provides a simple,
/// clean interface that handles all the API call details internally.
///
/// This is memory efficient as it only loads one page at a time.
/// Use this when you want to process items one by one without
/// loading all items into memory at once.
///
/// # Arguments
/// * `config` - API configuration containing base URL and authentication
/// * `workflow_id` - ID of the workflow to list results from  
/// * `params` - ResultListParams containing filter and pagination parameters
///
/// # Returns
/// An iterator that yields `Result<ResultModel, Error>` items
///
pub fn iter_results(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: ResultListParams,
) -> ResultsIterator {
    ResultsIterator::new(config.clone(), workflow_id, params, None)
}

/// Collect all results into a vector using lazy iteration internally.
///
/// This function uses `iter_results` internally and collects all results.
/// Use this when you need all items in memory at once for batch processing
/// or when you need to know the total count before processing.
///
/// # Arguments
/// * `config` - API configuration containing base URL and authentication
/// * `workflow_id` - ID of the workflow to list results from
/// * `params` - ResultListParams containing filter and pagination parameters
///
/// # Returns
/// `Result<Vec<ResultModel>, Error>` containing all results or an error
///
pub fn paginate_results(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: ResultListParams,
) -> Result<Vec<ResultModel>, apis::Error<apis::default_api::ListResultsError>> {
    iter_results(config, workflow_id, params).collect()
}
