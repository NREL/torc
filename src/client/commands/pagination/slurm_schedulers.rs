//! Slurm schedulers pagination functionality.
//!
//! This module provides lazy iteration and vector collection support for slurm schedulers.
//! It includes both simple iterators that work with the real API and mock iterators
//! for testing purposes.

use crate::client::apis;
use crate::models::*;

/// Parameters for listing slurm schedulers with default values and builder methods.
///
/// This struct provides a clean way to specify filtering and pagination
/// parameters for slurm scheduler queries. All fields have sensible defaults:
/// - `offset` defaults to 0 (start from beginning)
/// - All other fields default to `None` (no filtering)
///
#[derive(Debug, Clone, Default)]
pub struct SlurmSchedulersListParams {
    pub offset: i64,
    pub limit: Option<i64>,
    pub sort_by: Option<String>,
    pub reverse_sort: Option<bool>,
    pub name: Option<String>,
    pub account: Option<String>,
    pub gres: Option<String>,
    pub mem: Option<String>,
    pub nodes: Option<i64>,
    pub partition: Option<String>,
    pub qos: Option<String>,
    pub tmp: Option<String>,
    pub walltime: Option<String>,
}

// Builder methods for SlurmSchedulersListParams
impl SlurmSchedulersListParams {
    pub fn new() -> Self {
        Self::default()
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
}

/// Iterator for slurm schedulers with lazy pagination
pub struct SlurmSchedulersIterator {
    config: apis::configuration::Configuration,
    workflow_id: i64,
    params: SlurmSchedulersListParams,
    remaining_limit: i64,
    initial_limit: i64,
    current_page: std::vec::IntoIter<SlurmSchedulerModel>,
    finished: bool,
}

impl SlurmSchedulersIterator {
    pub fn new(
        config: apis::configuration::Configuration,
        workflow_id: i64,
        params: SlurmSchedulersListParams,
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
    ) -> Result<bool, apis::Error<apis::default_api::ListSlurmSchedulersError>> {
        if self.finished || (self.remaining_limit != i64::MAX && self.remaining_limit <= 0) {
            return Ok(false);
        }

        let page_limit = std::cmp::min(self.remaining_limit, self.initial_limit);
        let response = apis::default_api::list_slurm_schedulers(
            &self.config,
            self.workflow_id,
            Some(self.params.offset),
            Some(page_limit),
            self.params.sort_by.as_deref(),
            self.params.reverse_sort,
            self.params.name.as_deref(),
            self.params.account.as_deref(),
            self.params.gres.as_deref(),
            self.params.mem.as_deref(),
            self.params.nodes,
            self.params.partition.as_deref(),
            self.params.qos.as_deref(),
            self.params.tmp.as_deref(),
            self.params.walltime.as_deref(),
        )?;

        if let Some(items) = response.items {
            let items_to_take = if self.remaining_limit == i64::MAX {
                items.len()
            } else {
                std::cmp::min(items.len() as i64, self.remaining_limit) as usize
            };
            let taken_items: Vec<SlurmSchedulerModel> =
                items.into_iter().take(items_to_take).collect();
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

impl Iterator for SlurmSchedulersIterator {
    type Item =
        Result<SlurmSchedulerModel, apis::Error<apis::default_api::ListSlurmSchedulersError>>;

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

/// Create a lazy iterator for slurm schedulers that fetches pages on-demand.
///
/// This is the main API function for iterating over slurm schedulers. It provides a simple,
/// clean interface that handles all the API call details internally.
///
/// This is memory efficient as it only loads one page at a time.
/// Use this when you want to process items one by one without
/// loading all items into memory at once.
///
/// # Arguments
/// * `config` - API configuration containing base URL and authentication
/// * `workflow_id` - ID of the workflow to list slurm schedulers from
/// * `params` - SlurmSchedulersListParams containing filter and pagination parameters
///
/// # Returns
/// An iterator that yields `Result<SlurmSchedulerModel, Error>` items
///
pub fn iter_slurm_schedulers(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: SlurmSchedulersListParams,
) -> SlurmSchedulersIterator {
    SlurmSchedulersIterator::new(config.clone(), workflow_id, params, None)
}

/// Collect all slurm schedulers into a vector using lazy iteration internally.
///
/// This function uses `iter_slurm_schedulers` internally and collects all results.
/// Use this when you need all items in memory at once for batch processing
/// or when you need to know the total count before processing.
///
/// # Arguments
/// * `config` - API configuration containing base URL and authentication
/// * `workflow_id` - ID of the workflow to list slurm schedulers from
/// * `params` - SlurmSchedulersListParams containing filter and pagination parameters
///
/// # Returns
/// `Result<Vec<SlurmSchedulerModel>, Error>` containing all slurm schedulers or an error
///
pub fn paginate_slurm_schedulers(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: SlurmSchedulersListParams,
) -> Result<Vec<SlurmSchedulerModel>, apis::Error<apis::default_api::ListSlurmSchedulersError>> {
    iter_slurm_schedulers(config, workflow_id, params).collect()
}
