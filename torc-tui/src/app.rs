use anyhow::Result;
use ratatui::widgets::TableState;
use torc::models::{EventModel, FileModel, JobModel, ResultModel, WorkflowModel};

use crate::api::TorcClient;
use crate::dag::{DagLayout, JobNode};

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum DetailViewType {
    Jobs,
    Files,
    Events,
    Results,
    Dag,
}

impl DetailViewType {
    pub fn as_str(&self) -> &str {
        match self {
            Self::Jobs => "Jobs",
            Self::Files => "Files",
            Self::Events => "Events",
            Self::Results => "Results",
            Self::Dag => "DAG",
        }
    }

    pub fn all() -> Vec<Self> {
        vec![
            Self::Jobs,
            Self::Files,
            Self::Events,
            Self::Results,
            Self::Dag,
        ]
    }

    pub fn next(&self) -> Self {
        match self {
            Self::Jobs => Self::Files,
            Self::Files => Self::Events,
            Self::Events => Self::Results,
            Self::Results => Self::Dag,
            Self::Dag => Self::Jobs,
        }
    }

    pub fn previous(&self) -> Self {
        match self {
            Self::Jobs => Self::Dag,
            Self::Files => Self::Jobs,
            Self::Events => Self::Files,
            Self::Results => Self::Events,
            Self::Dag => Self::Results,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Focus {
    Workflows,
    Details,
    FilterInput,
    ServerUrlInput,
    UserInput,
}

#[derive(Debug, Clone, PartialEq)]
pub struct Filter {
    pub column: String,
    pub value: String,
}

pub struct App {
    pub client: TorcClient,
    pub server_url: String,
    pub server_url_input: String,
    pub user_filter: Option<String>,
    pub user_input: String,
    pub show_all_users: bool,
    pub workflows: Vec<WorkflowModel>,
    pub workflows_state: TableState,
    pub jobs: Vec<JobModel>,
    pub jobs_all: Vec<JobModel>,
    pub jobs_state: TableState,
    pub files: Vec<FileModel>,
    pub files_all: Vec<FileModel>,
    pub files_state: TableState,
    pub events: Vec<EventModel>,
    pub events_all: Vec<EventModel>,
    pub events_state: TableState,
    pub results: Vec<ResultModel>,
    pub results_all: Vec<ResultModel>,
    pub results_state: TableState,
    pub dag: Option<DagLayout>,
    pub detail_view: DetailViewType,
    pub selected_workflow_id: Option<i64>,
    pub focus: Focus,
    pub filter: Option<Filter>,
    pub filter_input: String,
    pub filter_column_index: usize,
}

impl App {
    pub fn new() -> Result<Self> {
        let client = TorcClient::new()?;
        let server_url = client.get_base_url().to_string();

        // Get current user from environment
        let current_user = std::env::var("USER")
            .or_else(|_| std::env::var("USERNAME"))
            .unwrap_or_else(|_| "unknown".to_string());

        let mut app = Self {
            client,
            server_url: server_url.clone(),
            server_url_input: String::new(),
            user_filter: Some(current_user.clone()),
            user_input: String::new(),
            show_all_users: false,
            workflows: Vec::new(),
            workflows_state: TableState::default(),
            jobs: Vec::new(),
            jobs_all: Vec::new(),
            jobs_state: TableState::default(),
            files: Vec::new(),
            files_all: Vec::new(),
            files_state: TableState::default(),
            events: Vec::new(),
            events_all: Vec::new(),
            events_state: TableState::default(),
            results: Vec::new(),
            results_all: Vec::new(),
            results_state: TableState::default(),
            dag: None,
            detail_view: DetailViewType::Jobs,
            selected_workflow_id: None,
            focus: Focus::Workflows,
            filter: None,
            filter_input: String::new(),
            filter_column_index: 0,
        };

        // Load initial workflows
        app.refresh_workflows()?;

        Ok(app)
    }

    pub fn refresh_workflows(&mut self) -> Result<()> {
        self.workflows = if self.show_all_users {
            self.client.list_workflows()?
        } else if let Some(ref user) = self.user_filter {
            self.client.list_workflows_for_user(user)?
        } else {
            self.client.list_workflows()?
        };

        if !self.workflows.is_empty() && self.workflows_state.selected().is_none() {
            self.workflows_state.select(Some(0));
        }
        Ok(())
    }

    pub fn toggle_focus(&mut self) {
        self.focus = match self.focus {
            Focus::Workflows => Focus::Details,
            Focus::Details => Focus::Workflows,
            Focus::FilterInput => Focus::FilterInput, // Stay in filter mode
            Focus::ServerUrlInput => Focus::ServerUrlInput, // Stay in URL input mode
            Focus::UserInput => Focus::UserInput,     // Stay in user input mode
        };
    }

    pub fn next_in_active_table(&mut self) {
        match self.focus {
            Focus::Workflows => {
                self.workflows_state.select(Some(
                    self.workflows_state
                        .selected()
                        .map(|i| (i + 1).min(self.workflows.len().saturating_sub(1)))
                        .unwrap_or(0),
                ));
            }
            Focus::Details => {
                let (state, len) = match self.detail_view {
                    DetailViewType::Jobs => (&mut self.jobs_state, self.jobs.len()),
                    DetailViewType::Files => (&mut self.files_state, self.files.len()),
                    DetailViewType::Events => (&mut self.events_state, self.events.len()),
                    DetailViewType::Results => (&mut self.results_state, self.results.len()),
                    DetailViewType::Dag => return, // DAG view doesn't support table navigation
                };
                if len > 0 {
                    state.select(Some(
                        state
                            .selected()
                            .map(|i| (i + 1).min(len.saturating_sub(1)))
                            .unwrap_or(0),
                    ));
                }
            }
            Focus::FilterInput => {}    // No navigation in filter mode
            Focus::ServerUrlInput => {} // No navigation in URL input mode
            Focus::UserInput => {}      // No navigation in user input mode
        }
    }

    pub fn previous_in_active_table(&mut self) {
        match self.focus {
            Focus::Workflows => {
                self.workflows_state.select(Some(
                    self.workflows_state
                        .selected()
                        .map(|i| i.saturating_sub(1))
                        .unwrap_or(0),
                ));
            }
            Focus::Details => {
                let (state, len) = match self.detail_view {
                    DetailViewType::Jobs => (&mut self.jobs_state, self.jobs.len()),
                    DetailViewType::Files => (&mut self.files_state, self.files.len()),
                    DetailViewType::Events => (&mut self.events_state, self.events.len()),
                    DetailViewType::Results => (&mut self.results_state, self.results.len()),
                    DetailViewType::Dag => return, // DAG view doesn't support table navigation
                };
                if len > 0 {
                    state.select(Some(
                        state.selected().map(|i| i.saturating_sub(1)).unwrap_or(0),
                    ));
                }
            }
            Focus::FilterInput => {}    // No navigation in filter mode
            Focus::ServerUrlInput => {} // No navigation in URL input mode
            Focus::UserInput => {}      // No navigation in user input mode
        }
    }

    pub fn load_detail_data(&mut self) -> Result<()> {
        if let Some(idx) = self.workflows_state.selected() {
            if let Some(workflow) = self.workflows.get(idx) {
                self.selected_workflow_id = workflow.id;
                if let Some(workflow_id) = workflow.id {
                    // Clear any existing filter when loading new data
                    self.filter = None;

                    match self.detail_view {
                        DetailViewType::Jobs => {
                            self.jobs_all = self.client.list_jobs(workflow_id)?;
                            self.jobs = self.jobs_all.clone();
                            if !self.jobs.is_empty() {
                                self.jobs_state.select(Some(0));
                            }
                        }
                        DetailViewType::Files => {
                            self.files_all = self.client.list_files(workflow_id)?;
                            self.files = self.files_all.clone();
                            if !self.files.is_empty() {
                                self.files_state.select(Some(0));
                            }
                        }
                        DetailViewType::Events => {
                            self.events_all = self.client.list_events(workflow_id)?;
                            self.events = self.events_all.clone();
                            if !self.events.is_empty() {
                                self.events_state.select(Some(0));
                            }
                        }
                        DetailViewType::Results => {
                            self.results_all = self.client.list_results(workflow_id)?;
                            self.results = self.results_all.clone();
                            if !self.results.is_empty() {
                                self.results_state.select(Some(0));
                            }
                        }
                        DetailViewType::Dag => {
                            // Load jobs if not already loaded
                            if self.jobs_all.is_empty() {
                                self.jobs_all = self.client.list_jobs(workflow_id)?;
                                self.jobs = self.jobs_all.clone();
                            }
                            // Build the DAG
                            self.build_dag_from_jobs();
                        }
                    }
                }
            }
        }
        Ok(())
    }

    pub fn next_detail_view(&mut self) {
        self.detail_view = self.detail_view.next();
    }

    pub fn previous_detail_view(&mut self) {
        self.detail_view = self.detail_view.previous();
    }

    pub fn start_filter(&mut self) {
        self.focus = Focus::FilterInput;
        self.filter_input.clear();
        self.filter_column_index = 0;
    }

    pub fn cancel_filter(&mut self) {
        self.focus = Focus::Details;
        self.filter_input.clear();
    }

    pub fn get_filter_columns(&self) -> Vec<&str> {
        match self.detail_view {
            DetailViewType::Jobs => vec!["Status", "Name", "Command"],
            DetailViewType::Files => vec!["Name", "Path"],
            DetailViewType::Events => vec!["Data"],
            DetailViewType::Results => vec!["Status", "Return Code"],
            DetailViewType::Dag => vec![], // DAG view doesn't support filtering
        }
    }

    pub fn next_filter_column(&mut self) {
        let columns = self.get_filter_columns();
        self.filter_column_index = (self.filter_column_index + 1) % columns.len();
    }

    pub fn prev_filter_column(&mut self) {
        let columns = self.get_filter_columns();
        if self.filter_column_index == 0 {
            self.filter_column_index = columns.len() - 1;
        } else {
            self.filter_column_index -= 1;
        }
    }

    pub fn add_filter_char(&mut self, c: char) {
        self.filter_input.push(c);
    }

    pub fn remove_filter_char(&mut self) {
        self.filter_input.pop();
    }

    pub fn apply_filter(&mut self) {
        if self.filter_input.is_empty() {
            self.clear_filter();
            self.focus = Focus::Details;
            return;
        }

        let columns = self.get_filter_columns();
        let column = columns[self.filter_column_index].to_string();
        let value = self.filter_input.clone().to_lowercase();

        self.filter = Some(Filter {
            column: column.clone(),
            value: value.clone(),
        });

        match self.detail_view {
            DetailViewType::Jobs => {
                self.jobs = self
                    .jobs_all
                    .iter()
                    .filter(|job| match column.as_str() {
                        "Status" => job
                            .status
                            .as_ref()
                            .map(|s| format!("{:?}", s).to_lowercase().contains(&value))
                            .unwrap_or(false),
                        "Name" => job.name.to_lowercase().contains(&value),
                        "Command" => job.command.to_lowercase().contains(&value),
                        _ => false,
                    })
                    .cloned()
                    .collect();
                if !self.jobs.is_empty() {
                    self.jobs_state.select(Some(0));
                } else {
                    self.jobs_state.select(None);
                }
            }
            DetailViewType::Files => {
                self.files = self
                    .files_all
                    .iter()
                    .filter(|file| match column.as_str() {
                        "Name" => file.name.to_lowercase().contains(&value),
                        "Path" => file.path.to_lowercase().contains(&value),
                        _ => false,
                    })
                    .cloned()
                    .collect();
                if !self.files.is_empty() {
                    self.files_state.select(Some(0));
                } else {
                    self.files_state.select(None);
                }
            }
            DetailViewType::Events => {
                self.events = self
                    .events_all
                    .iter()
                    .filter(|event| match column.as_str() {
                        "Data" => event.data.to_string().to_lowercase().contains(&value),
                        _ => false,
                    })
                    .cloned()
                    .collect();
                if !self.events.is_empty() {
                    self.events_state.select(Some(0));
                } else {
                    self.events_state.select(None);
                }
            }
            DetailViewType::Results => {
                self.results = self
                    .results_all
                    .iter()
                    .filter(|result| match column.as_str() {
                        "Status" => format!("{:?}", result.status)
                            .to_lowercase()
                            .contains(&value),
                        "Return Code" => result.return_code.to_string().contains(&value),
                        _ => false,
                    })
                    .cloned()
                    .collect();
                if !self.results.is_empty() {
                    self.results_state.select(Some(0));
                } else {
                    self.results_state.select(None);
                }
            }
            DetailViewType::Dag => {
                // DAG view doesn't support filtering
            }
        }

        self.focus = Focus::Details;
    }

    pub fn clear_filter(&mut self) {
        self.filter = None;
        match self.detail_view {
            DetailViewType::Jobs => {
                self.jobs = self.jobs_all.clone();
                if !self.jobs.is_empty() {
                    self.jobs_state.select(Some(0));
                }
            }
            DetailViewType::Files => {
                self.files = self.files_all.clone();
                if !self.files.is_empty() {
                    self.files_state.select(Some(0));
                }
            }
            DetailViewType::Events => {
                self.events = self.events_all.clone();
                if !self.events.is_empty() {
                    self.events_state.select(Some(0));
                }
            }
            DetailViewType::Results => {
                self.results = self.results_all.clone();
                if !self.results.is_empty() {
                    self.results_state.select(Some(0));
                }
            }
            DetailViewType::Dag => {
                // DAG view doesn't support filtering
            }
        }
    }

    pub fn start_server_url_input(&mut self) {
        self.focus = Focus::ServerUrlInput;
        self.server_url_input = self.server_url.clone();
    }

    pub fn cancel_server_url_input(&mut self) {
        self.focus = Focus::Workflows;
        self.server_url_input.clear();
    }

    pub fn add_server_url_char(&mut self, c: char) {
        self.server_url_input.push(c);
    }

    pub fn remove_server_url_char(&mut self) {
        self.server_url_input.pop();
    }

    pub fn apply_server_url(&mut self) -> Result<()> {
        if self.server_url_input.is_empty() {
            self.cancel_server_url_input();
            return Ok(());
        }

        // Create new client with updated URL
        self.client = TorcClient::from_url(self.server_url_input.clone())?;
        self.server_url = self.server_url_input.clone();
        self.focus = Focus::Workflows;

        // Refresh workflows with new connection
        self.refresh_workflows()?;

        Ok(())
    }

    pub fn start_user_input(&mut self) {
        self.focus = Focus::UserInput;
        self.user_input = self.user_filter.clone().unwrap_or_default();
    }

    pub fn cancel_user_input(&mut self) {
        self.focus = Focus::Workflows;
        self.user_input.clear();
    }

    pub fn add_user_char(&mut self, c: char) {
        self.user_input.push(c);
    }

    pub fn remove_user_char(&mut self) {
        self.user_input.pop();
    }

    pub fn apply_user_filter(&mut self) -> Result<()> {
        if self.user_input.is_empty() {
            self.user_filter = None;
        } else {
            self.user_filter = Some(self.user_input.clone());
        }
        self.focus = Focus::Workflows;

        // Refresh workflows with new user filter
        self.refresh_workflows()?;

        Ok(())
    }

    pub fn toggle_show_all_users(&mut self) -> Result<()> {
        self.show_all_users = !self.show_all_users;
        self.refresh_workflows()?;
        Ok(())
    }

    pub fn get_current_user_display(&self) -> String {
        if self.show_all_users {
            "All Users".to_string()
        } else if let Some(ref user) = self.user_filter {
            user.clone()
        } else {
            "All Users".to_string()
        }
    }

    pub fn build_dag_from_jobs(&mut self) {
        use petgraph::graph::NodeIndex;
        use std::collections::HashMap;

        let mut dag = DagLayout::new();
        let mut job_id_to_node: HashMap<i64, NodeIndex> = HashMap::new();

        // Create nodes for all jobs
        for job in &self.jobs_all {
            if let Some(job_id) = job.id {
                let node = dag.add_node(JobNode {
                    id: job_id,
                    name: job.name.clone(),
                    status: job.status.as_ref().map(|s| format!("{:?}", s)),
                });
                job_id_to_node.insert(job_id, node);
            }
        }

        // Fetch blocking relationships from server
        if let Some(workflow_id) = self.selected_workflow_id {
            match self.client.list_job_dependencies(workflow_id) {
                Ok(dependencies) => {
                    // Add edges to graph
                    for dep in dependencies {
                        if let (Some(&from_node), Some(&to_node)) = (
                            job_id_to_node.get(&dep.blocked_by_job_id),
                            job_id_to_node.get(&dep.job_id),
                        ) {
                            dag.add_edge(from_node, to_node);
                        }
                    }
                }
                Err(e) => {
                    log::warn!("Failed to load job dependencies: {}", e);
                    // Continue without edges - at least show nodes
                }
            }
        }

        dag.compute_layout();
        self.dag = Some(dag);
    }
}
