//! User data pagination functionality.
//!
//! This module provides lazy iteration and vector collection support for user data.
//! It includes both simple iterators that work with the real API and mock iterators
//! for testing purposes.

use crate::client::apis;
use crate::models::*;

/// Parameters for listing user data with default values and builder methods.
///
/// This struct provides a clean way to specify filtering and pagination
/// parameters for user data queries. All fields have sensible defaults:
/// - `offset` defaults to 0 (start from beginning)
/// - All other fields default to `None` (no filtering)
///
#[derive(Debug, Clone)]
pub struct UserDataListParams {
    pub consumer_job_id: Option<i64>,
    pub producer_job_id: Option<i64>,
    pub offset: i64,
    pub limit: Option<i64>,
    pub sort_by: Option<String>,
    pub reverse_sort: Option<bool>,
    pub name: Option<String>,
    pub is_ephemeral: Option<bool>,
}

impl Default for UserDataListParams {
    fn default() -> Self {
        Self {
            consumer_job_id: None,
            producer_job_id: None,
            offset: 0,
            limit: None,
            sort_by: None,
            reverse_sort: None,
            name: None,
            is_ephemeral: None,
        }
    }
}

// Builder methods for UserDataListParams
impl UserDataListParams {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn with_consumer_job_id(mut self, job_id: i64) -> Self {
        self.consumer_job_id = Some(job_id);
        self
    }

    pub fn with_producer_job_id(mut self, job_id: i64) -> Self {
        self.producer_job_id = Some(job_id);
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

    pub fn with_name(mut self, name: String) -> Self {
        self.name = Some(name);
        self
    }

    pub fn with_is_ephemeral(mut self, is_ephemeral: bool) -> Self {
        self.is_ephemeral = Some(is_ephemeral);
        self
    }
}

/// Iterator for user data with lazy pagination
pub struct UserDataIterator {
    config: apis::configuration::Configuration,
    workflow_id: i64,
    params: UserDataListParams,
    remaining_limit: i64,
    initial_limit: i64,
    current_page: std::vec::IntoIter<UserDataModel>,
    finished: bool,
}

impl UserDataIterator {
    pub fn new(
        config: apis::configuration::Configuration,
        workflow_id: i64,
        params: UserDataListParams,
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
    ) -> Result<bool, apis::Error<apis::default_api::ListUserDataError>> {
        if self.finished || (self.remaining_limit != i64::MAX && self.remaining_limit <= 0) {
            return Ok(false);
        }

        let page_limit = std::cmp::min(self.remaining_limit, self.initial_limit);
        let response = apis::default_api::list_user_data(
            &self.config,
            self.workflow_id,
            self.params.consumer_job_id,
            self.params.producer_job_id,
            Some(self.params.offset),
            Some(page_limit),
            self.params.sort_by.as_deref(),
            self.params.reverse_sort,
            self.params.name.as_deref(),
            self.params.is_ephemeral,
        )?;

        if let Some(items) = response.items {
            let items_to_take = if self.remaining_limit == i64::MAX {
                items.len()
            } else {
                std::cmp::min(items.len() as i64, self.remaining_limit) as usize
            };
            let taken_items: Vec<UserDataModel> = items.into_iter().take(items_to_take).collect();
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

impl Iterator for UserDataIterator {
    type Item = Result<UserDataModel, apis::Error<apis::default_api::ListUserDataError>>;

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

/// Create a lazy iterator for user data that fetches pages on-demand.
///
/// This is the main API function for iterating over user data. It provides a simple,
/// clean interface that handles all the API call details internally.
///
/// This is memory efficient as it only loads one page at a time.
/// Use this when you want to process items one by one without
/// loading all items into memory at once.
///
/// # Arguments
/// * `config` - API configuration containing base URL and authentication
/// * `workflow_id` - ID of the workflow to list user data from  
/// * `params` - UserDataListParams containing filter and pagination parameters
///
/// # Returns
/// An iterator that yields `Result<UserDataModel, Error>` items
///
pub fn iter_user_data(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: UserDataListParams,
) -> UserDataIterator {
    UserDataIterator::new(config.clone(), workflow_id, params, None)
}

/// Collect all user data into a vector using lazy iteration internally.
///
/// This function uses `iter_user_data` internally and collects all results.
/// Use this when you need all items in memory at once for batch processing
/// or when you need to know the total count before processing.
///
/// # Arguments
/// * `config` - API configuration containing base URL and authentication
/// * `workflow_id` - ID of the workflow to list user data from
/// * `params` - UserDataListParams containing filter and pagination parameters
///
/// # Returns
/// `Result<Vec<UserDataModel>, Error>` containing all user data or an error
///
pub fn paginate_user_data(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: UserDataListParams,
) -> Result<Vec<UserDataModel>, apis::Error<apis::default_api::ListUserDataError>> {
    iter_user_data(config, workflow_id, params).collect()
}
