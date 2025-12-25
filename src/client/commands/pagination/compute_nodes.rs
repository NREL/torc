//! Compute nodes pagination functionality.
//!
//! This module provides lazy iteration and vector collection support for compute nodes.

use crate::client::apis;
use crate::models::ComputeNodeModel;

/// Parameters for listing compute nodes with default values and builder methods.
#[derive(Debug, Clone, Default)]
pub struct ComputeNodeListParams {
    pub offset: i64,
    pub limit: Option<i64>,
    pub sort_by: Option<String>,
    pub reverse_sort: Option<bool>,
    pub hostname: Option<String>,
    pub is_active: Option<bool>,
    pub scheduled_compute_node_id: Option<i64>,
}

impl ComputeNodeListParams {
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

    pub fn with_hostname(mut self, hostname: String) -> Self {
        self.hostname = Some(hostname);
        self
    }

    pub fn with_is_active(mut self, is_active: bool) -> Self {
        self.is_active = Some(is_active);
        self
    }

    pub fn with_scheduled_compute_node_id(mut self, id: i64) -> Self {
        self.scheduled_compute_node_id = Some(id);
        self
    }
}

/// Iterator for compute nodes with lazy pagination
pub struct ComputeNodesIterator {
    config: apis::configuration::Configuration,
    workflow_id: i64,
    params: ComputeNodeListParams,
    remaining_limit: i64,
    initial_limit: i64,
    current_page: std::vec::IntoIter<ComputeNodeModel>,
    finished: bool,
}

impl ComputeNodesIterator {
    pub fn new(
        config: apis::configuration::Configuration,
        workflow_id: i64,
        params: ComputeNodeListParams,
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
    ) -> Result<bool, apis::Error<apis::default_api::ListComputeNodesError>> {
        if self.finished || (self.remaining_limit != i64::MAX && self.remaining_limit <= 0) {
            return Ok(false);
        }

        let page_limit = std::cmp::min(self.remaining_limit, self.initial_limit);
        let response = apis::default_api::list_compute_nodes(
            &self.config,
            self.workflow_id,
            Some(self.params.offset),
            Some(page_limit),
            self.params.sort_by.as_deref(),
            self.params.reverse_sort,
            self.params.hostname.as_deref(),
            self.params.is_active,
            self.params.scheduled_compute_node_id,
        )?;

        if let Some(items) = response.items {
            let items_to_take = if self.remaining_limit == i64::MAX {
                items.len()
            } else {
                std::cmp::min(items.len() as i64, self.remaining_limit) as usize
            };
            let taken_items: Vec<ComputeNodeModel> =
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

impl Iterator for ComputeNodesIterator {
    type Item = Result<ComputeNodeModel, apis::Error<apis::default_api::ListComputeNodesError>>;

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

/// Create a lazy iterator for compute nodes that fetches pages on-demand.
pub fn iter_compute_nodes(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: ComputeNodeListParams,
) -> ComputeNodesIterator {
    ComputeNodesIterator::new(config.clone(), workflow_id, params, None)
}

/// Collect all compute nodes into a vector using lazy iteration internally.
pub fn paginate_compute_nodes(
    config: &apis::configuration::Configuration,
    workflow_id: i64,
    params: ComputeNodeListParams,
) -> Result<Vec<ComputeNodeModel>, apis::Error<apis::default_api::ListComputeNodesError>> {
    iter_compute_nodes(config, workflow_id, params).collect()
}
