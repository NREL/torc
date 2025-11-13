//! Resource requirements pagination functionality.
//!
//! This module provides lazy iteration and vector collection support for resource requirements.
//! It includes both simple iterators that work with the real API and mock iterators
//! for testing purposes.

use crate::client::apis;
use crate::models::*;

/// Parameters for listing resource requirements with default values and builder methods.
///
/// This struct provides a clean way to specify filtering and pagination
/// parameters for resource requirement queries. All fields have sensible defaults:
/// - `offset` defaults to 0 (start from beginning)
/// - All other fields default to `None` (no filtering)
///
#[derive(Debug, Clone)]
pub struct ResourceRequirementsListParams {
    pub job_id: Option<i64>,
    pub offset: i64,
    pub limit: Option<i64>,
    pub sort_by: Option<String>,
    pub reverse_sort: Option<bool>,
    pub name: Option<String>,
    pub memory: Option<String>,
    pub num_cpus: Option<i64>,
    pub num_gpus: Option<i64>,
    pub num_nodes: Option<i64>,
    pub runtime: Option<String>,
}

impl Default for ResourceRequirementsListParams {
    fn default() -> Self {
        Self {
            job_id: None,
            offset: 0,
            limit: None,
            sort_by: None,
            reverse_sort: None,
            name: None,
            memory: None,
            num_cpus: None,
            num_gpus: None,
            num_nodes: None,
            runtime: None,
        }
    }
}

// Builder methods for ResourceRequirementsListParams
impl ResourceRequirementsListParams {
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

/// Iterator for resource requirements with lazy pagination
pub struct ResourceRequirementsIterator {
    config: apis::configuration::Configuration,
    workflow_id: i64,
    params: ResourceRequirementsListParams,
    remaining_limit: i64,
    initial_limit: i64,
    current_page: std::vec::IntoIter<ResourceRequirementsModel>,
    finished: bool,
}

impl ResourceRequirementsIterator {
    pub fn new(
        config: apis::configuration::Configuration,
        workflow_id: i64,
        params: ResourceRequirementsListParams,
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
    ) -> Result<bool, apis::Error<apis::default_api::ListResourceRequirementsError>> {
        if self.finished || (self.remaining_limit != i64::MAX && self.remaining_limit <= 0) {
            return Ok(false);
        }

        let page_limit = std::cmp::min(self.remaining_limit, self.initial_limit);
        let response = apis::default_api::list_resource_requirements(
            &self.config,
            self.workflow_id,
            self.params.job_id,
            Some(self.params.offset),
            Some(page_limit),
            self.params.sort_by.as_deref(),
            self.params.reverse_sort,
            self.params.name.as_deref(),
            self.params.memory.as_deref(),
            self.params.num_cpus,
            self.params.num_gpus,
            self.params.num_nodes,
            self.params.runtime.as_deref(),
        )?;

        if let Some(items) = response.items {
            let items_to_take = if self.remaining_limit == i64::MAX {
                items.len()
            } else {
                std::cmp::min(items.len() as i64, self.remaining_limit) as usize
            };
            let taken_items: Vec<ResourceRequirementsModel> =
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

impl Iterator for ResourceRequirementsIterator {
    type Item = Result<
        ResourceRequirementsModel,
        apis::Error<apis::default_api::ListResourceRequirementsError>,
    >;

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

/// Create a lazy iterator for resource requirements that fetches pages on-demand.
///
/// This is the main API function for iterating over resource requirements. It provides a simple,
/// clean interface that handles all the API call details internally.
///
/// This is memory efficient as it only loads one page at a time.
/// Use this when you want to process items one by one without
/// loading all items into memory at once.
///
/// # Arguments
/// * `config` - API configuration containing base URL and authentication
/// * `workflow_id` - ID of the workflow to list resource requirements from  
/// * `params` - ResourceRequirementsListParams containing filter and pagination parameters
///
/// # Returns
/// An iterator that yields `Result<ResourceRequirementsModel, Error>` items
///
pub fn iter_resource_requirements(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: ResourceRequirementsListParams,
) -> ResourceRequirementsIterator {
    ResourceRequirementsIterator::new(config.clone(), workflow_id, params, None)
}

/// Collect all resource requirements into a vector using lazy iteration internally.
///
/// This function uses `iter_resource_requirements` internally and collects all results.
/// Use this when you need all items in memory at once for batch processing
/// or when you need to know the total count before processing.
///
/// # Arguments
/// * `config` - API configuration containing base URL and authentication
/// * `workflow_id` - ID of the workflow to list resource requirements from
/// * `params` - ResourceRequirementsListParams containing filter and pagination parameters
///
/// # Returns
/// `Result<Vec<ResourceRequirementsModel>, Error>` containing all resource requirements or an error
///
pub fn paginate_resource_requirements(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: ResourceRequirementsListParams,
) -> Result<
    Vec<ResourceRequirementsModel>,
    apis::Error<apis::default_api::ListResourceRequirementsError>,
> {
    iter_resource_requirements(config, workflow_id, params).collect()
}
