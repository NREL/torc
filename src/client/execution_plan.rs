use crate::client::workflow_spec::{WorkflowActionSpec, WorkflowSpec};
use crate::models::{JobModel, WorkflowActionModel, WorkflowModel};
use regex::Regex;
use std::collections::{HashMap, HashSet};

/// Represents a scheduler allocation in the execution plan
#[derive(Debug, Clone)]
pub struct SchedulerAllocation {
    pub scheduler_name: String,
    pub scheduler_type: String,
    pub num_allocations: i64,
    pub job_names: Vec<String>,
}

/// Represents a stage in the workflow execution plan
#[derive(Debug, Clone)]
pub struct ExecutionStage {
    pub stage_number: usize,
    pub trigger_description: String,
    pub scheduler_allocations: Vec<SchedulerAllocation>,
    pub jobs_becoming_ready: Vec<String>,
}

/// Represents the complete execution plan for a workflow
#[derive(Debug)]
pub struct ExecutionPlan {
    pub stages: Vec<ExecutionStage>,
}

impl ExecutionPlan {
    /// Build an execution plan from a workflow specification
    pub fn from_spec(spec: &WorkflowSpec) -> Result<Self, Box<dyn std::error::Error>> {
        let mut stages = Vec::new();

        // Build dependency graph (job_name -> jobs it's blocked by)
        let dependency_graph = build_dependency_graph(spec)?;

        // Build reverse dependency graph (job_name -> jobs that depend on it)
        let reverse_deps = build_reverse_dependencies(&dependency_graph);

        // Topologically sort jobs into levels
        let job_levels = topological_sort(spec, &dependency_graph)?;

        // Stage 0: on_workflow_start actions
        let workflow_start_stage = build_workflow_start_stage(spec)?;
        if !workflow_start_stage.scheduler_allocations.is_empty()
            || !workflow_start_stage.jobs_becoming_ready.is_empty()
        {
            stages.push(workflow_start_stage);
        }

        // Build stages for each job level
        for (level_idx, level_jobs) in job_levels.iter().enumerate() {
            if level_jobs.is_empty() {
                continue;
            }

            let stage_number = stages.len();
            let stage = build_job_completion_stage(
                spec,
                stage_number,
                level_idx,
                level_jobs,
                &job_levels,
                &reverse_deps,
            )?;

            // Only add the stage if it has actions or jobs becoming ready
            if !stage.scheduler_allocations.is_empty() || !stage.jobs_becoming_ready.is_empty() {
                stages.push(stage);
            }
        }

        Ok(ExecutionPlan { stages })
    }

    /// Build an execution plan from database models (workflow, jobs, actions)
    pub fn from_database_models(
        _workflow: &WorkflowModel,
        jobs: &[JobModel],
        actions: &[WorkflowActionModel],
    ) -> Result<Self, Box<dyn std::error::Error>> {
        let mut stages = Vec::new();

        // Build dependency graph from jobs (job_id -> Vec<job_ids it depends on>)
        let mut job_id_to_name = HashMap::new();
        let mut job_name_to_id = HashMap::new();
        let mut dependency_graph_by_id: HashMap<i64, Vec<i64>> = HashMap::new();

        for job in jobs {
            let job_id = job.id.ok_or("Job missing ID")?;
            job_id_to_name.insert(job_id, job.name.clone());
            job_name_to_id.insert(job.name.clone(), job_id);

            let deps = job.blocked_by_job_ids.clone().unwrap_or_default();
            dependency_graph_by_id.insert(job_id, deps);
        }

        // Convert to name-based graph for topological sort
        let mut dependency_graph_by_name: HashMap<String, Vec<String>> = HashMap::new();
        for job in jobs {
            let job_id = job.id.unwrap();
            let job_name = &job.name;
            let dep_ids = dependency_graph_by_id.get(&job_id).unwrap();
            let dep_names: Vec<String> = dep_ids
                .iter()
                .filter_map(|id| job_id_to_name.get(id).cloned())
                .collect();
            dependency_graph_by_name.insert(job_name.clone(), dep_names);
        }

        // Topologically sort jobs into levels
        let job_levels = topological_sort_by_names(jobs, &dependency_graph_by_name)?;

        // Stage 0: on_workflow_start actions
        let workflow_start_stage = build_workflow_start_stage_from_db(
            jobs,
            actions,
            &dependency_graph_by_name,
            &job_name_to_id,
        )?;
        if !workflow_start_stage.scheduler_allocations.is_empty()
            || !workflow_start_stage.jobs_becoming_ready.is_empty()
        {
            stages.push(workflow_start_stage);
        }

        // Build stages for each job level
        for (level_idx, level_jobs) in job_levels.iter().enumerate() {
            if level_jobs.is_empty() {
                continue;
            }

            let stage_number = stages.len();
            let stage = build_job_completion_stage_from_db(
                jobs,
                actions,
                stage_number,
                level_idx,
                level_jobs,
                &job_levels,
                &job_name_to_id,
            )?;

            // Only add the stage if it has actions or jobs becoming ready
            if !stage.scheduler_allocations.is_empty() || !stage.jobs_becoming_ready.is_empty() {
                stages.push(stage);
            }
        }

        Ok(ExecutionPlan { stages })
    }

    /// Display the execution plan in a human-readable format
    pub fn display(&self) {
        println!("\n{}", "=".repeat(80));
        println!("Workflow Execution Plan");
        println!("{}", "=".repeat(80));

        for stage in &self.stages {
            println!(
                "\n{} Stage {}: {}",
                if stage.stage_number == 0 {
                    "▶"
                } else {
                    "→"
                },
                stage.stage_number + 1, // Display as 1-based
                stage.trigger_description
            );
            println!("{}", "-".repeat(80));

            if !stage.scheduler_allocations.is_empty() {
                println!("\n  Scheduler Allocations:");
                for alloc in &stage.scheduler_allocations {
                    println!(
                        "    • {} ({}) - {} allocation(s)",
                        alloc.scheduler_name, alloc.scheduler_type, alloc.num_allocations
                    );
                    let compact = compact_job_list(&alloc.job_names);
                    println!("      For jobs: {}", compact.join(", "));
                }
            }

            if !stage.jobs_becoming_ready.is_empty() {
                println!("\n  Jobs Becoming Ready:");
                let compact = compact_job_list(&stage.jobs_becoming_ready);
                for item in compact {
                    println!("    • {}", item);
                }
            }

            if stage.scheduler_allocations.is_empty() && stage.jobs_becoming_ready.is_empty() {
                println!("  (No actions or jobs in this stage)");
            }
        }

        println!("\n{}", "=".repeat(80));
        println!("Total Stages: {}", self.stages.len());
        println!("{}\n", "=".repeat(80));
    }
}

/// Build dependency graph: job_name -> vec of job names it depends on
fn build_dependency_graph(
    spec: &WorkflowSpec,
) -> Result<HashMap<String, Vec<String>>, Box<dyn std::error::Error>> {
    let mut deps = HashMap::new();

    for job in &spec.jobs {
        let mut job_deps = Vec::new();

        // Add explicit dependencies from blocked_by_job_names
        if let Some(ref names) = job.blocked_by_job_names {
            job_deps.extend(names.clone());
        }

        // Add dependencies from blocked_by_job_name_regexes
        if let Some(ref regexes) = job.blocked_by_job_name_regexes {
            for regex_str in regexes {
                let re = Regex::new(regex_str)?;
                for other_job in &spec.jobs {
                    if re.is_match(&other_job.name) && !job_deps.contains(&other_job.name) {
                        job_deps.push(other_job.name.clone());
                    }
                }
            }
        }

        // Add implicit dependencies from input files
        if let Some(ref input_files) = job.input_file_names {
            for input_file in input_files {
                // Find jobs that produce this file
                for other_job in &spec.jobs {
                    if let Some(ref output_files) = other_job.output_file_names {
                        if output_files.contains(input_file) && !job_deps.contains(&other_job.name)
                        {
                            job_deps.push(other_job.name.clone());
                        }
                    }
                }
            }
        }

        // Add implicit dependencies from input user data
        if let Some(ref input_data) = job.input_user_data_names {
            for input_datum in input_data {
                // Find jobs that produce this data
                for other_job in &spec.jobs {
                    if let Some(ref output_data) = other_job.output_data_names {
                        if output_data.contains(input_datum) && !job_deps.contains(&other_job.name)
                        {
                            job_deps.push(other_job.name.clone());
                        }
                    }
                }
            }
        }

        deps.insert(job.name.clone(), job_deps);
    }

    Ok(deps)
}

/// Build reverse dependency graph: job_name -> vec of jobs that depend on it
fn build_reverse_dependencies(deps: &HashMap<String, Vec<String>>) -> HashMap<String, Vec<String>> {
    let mut reverse = HashMap::new();

    for (job, dependencies) in deps {
        for dep in dependencies {
            reverse
                .entry(dep.clone())
                .or_insert_with(Vec::new)
                .push(job.clone());
        }
    }

    reverse
}

/// Topologically sort jobs into levels based on dependencies
fn topological_sort(
    spec: &WorkflowSpec,
    deps: &HashMap<String, Vec<String>>,
) -> Result<Vec<Vec<String>>, Box<dyn std::error::Error>> {
    let mut levels = Vec::new();
    let mut remaining: HashSet<String> = spec.jobs.iter().map(|j| j.name.clone()).collect();
    let mut processed = HashSet::new();

    while !remaining.is_empty() {
        let mut current_level = Vec::new();

        // Find all jobs whose dependencies are satisfied
        for job in &spec.jobs {
            if remaining.contains(&job.name) {
                let job_deps = deps.get(&job.name).unwrap();
                if job_deps.iter().all(|d| processed.contains(d)) {
                    current_level.push(job.name.clone());
                }
            }
        }

        if current_level.is_empty() {
            return Err("Circular dependency detected in job graph".into());
        }

        // Mark these jobs as processed
        for job in &current_level {
            remaining.remove(job);
            processed.insert(job.clone());
        }

        levels.push(current_level);
    }

    Ok(levels)
}

/// Build stage for workflow start actions
fn build_workflow_start_stage(
    spec: &WorkflowSpec,
) -> Result<ExecutionStage, Box<dyn std::error::Error>> {
    let mut scheduler_allocations = Vec::new();

    // Find on_workflow_start actions
    if let Some(ref actions) = spec.actions {
        for action in actions {
            if action.trigger_type == "on_workflow_start" {
                if let Some(alloc) = build_scheduler_allocation(spec, action)? {
                    scheduler_allocations.push(alloc);
                }
            }
        }
    }

    // Build dependency graph to find jobs with no dependencies
    let dependency_graph = build_dependency_graph(spec)?;

    // Jobs with empty dependency lists become ready at start
    let mut jobs_becoming_ready = Vec::new();
    for job in &spec.jobs {
        if let Some(deps) = dependency_graph.get(&job.name) {
            if deps.is_empty() {
                jobs_becoming_ready.push(job.name.clone());
            }
        }
    }

    Ok(ExecutionStage {
        stage_number: 0,
        trigger_description: "Workflow Start".to_string(),
        scheduler_allocations,
        jobs_becoming_ready,
    })
}

/// Build stage for when a level of jobs completes
fn build_job_completion_stage(
    spec: &WorkflowSpec,
    stage_number: usize,
    level_idx: usize,
    level_jobs: &[String],
    all_levels: &[Vec<String>],
    _reverse_deps: &HashMap<String, Vec<String>>,
) -> Result<ExecutionStage, Box<dyn std::error::Error>> {
    let mut scheduler_allocations = Vec::new();

    // Find jobs that become ready after this level completes
    let jobs_becoming_ready: Vec<String> = if level_idx + 1 < all_levels.len() {
        all_levels[level_idx + 1].clone()
    } else {
        Vec::new()
    };

    // Find on_jobs_ready actions that match the jobs becoming ready
    if let Some(ref actions) = spec.actions {
        for action in actions {
            if action.trigger_type == "on_jobs_ready" {
                // Check if this action matches any of the jobs becoming ready
                let action_jobs = get_matching_jobs(spec, action)?;
                let matches_any = action_jobs.iter().any(|j| jobs_becoming_ready.contains(j));

                if matches_any {
                    if let Some(alloc) = build_scheduler_allocation(spec, action)? {
                        scheduler_allocations.push(alloc);
                    }
                }
            }
        }
    }

    // Build trigger description
    let trigger_description = if level_jobs.len() == 1 {
        format!("When job '{}' completes", level_jobs[0])
    } else if level_jobs.len() <= 3 {
        format!(
            "When jobs {} complete",
            level_jobs
                .iter()
                .map(|j| format!("'{}'", j))
                .collect::<Vec<_>>()
                .join(", ")
        )
    } else {
        format!(
            "When {} jobs complete ({}...)",
            level_jobs.len(),
            level_jobs
                .iter()
                .take(2)
                .map(|j| format!("'{}'", j))
                .collect::<Vec<_>>()
                .join(", ")
        )
    };

    Ok(ExecutionStage {
        stage_number,
        trigger_description,
        scheduler_allocations,
        jobs_becoming_ready,
    })
}

/// Get job names that match an action's job_names or job_name_regexes
fn get_matching_jobs(
    spec: &WorkflowSpec,
    action: &WorkflowActionSpec,
) -> Result<Vec<String>, Box<dyn std::error::Error>> {
    let mut matched = Vec::new();

    // Match exact names
    if let Some(ref names) = action.job_names {
        matched.extend(names.clone());
    }

    // Match regex patterns
    if let Some(ref regexes) = action.job_name_regexes {
        for regex_str in regexes {
            let re = Regex::new(regex_str)?;
            for job in &spec.jobs {
                if re.is_match(&job.name) && !matched.contains(&job.name) {
                    matched.push(job.name.clone());
                }
            }
        }
    }

    Ok(matched)
}

/// Build a scheduler allocation from an action
fn build_scheduler_allocation(
    spec: &WorkflowSpec,
    action: &WorkflowActionSpec,
) -> Result<Option<SchedulerAllocation>, Box<dyn std::error::Error>> {
    if action.action_type != "schedule_nodes" {
        return Ok(None);
    }

    let scheduler_name = action
        .scheduler_name
        .as_ref()
        .ok_or("schedule_nodes action missing scheduler_name")?
        .clone();

    let scheduler_type = action
        .scheduler_type
        .as_ref()
        .ok_or("schedule_nodes action missing scheduler_type")?
        .clone();

    let num_allocations = action.num_allocations.unwrap_or(1);

    let job_names = get_matching_jobs(spec, action)?;

    Ok(Some(SchedulerAllocation {
        scheduler_name,
        scheduler_type,
        num_allocations,
        job_names,
    }))
}

/// Topologically sort jobs by name
fn topological_sort_by_names(
    jobs: &[JobModel],
    deps: &HashMap<String, Vec<String>>,
) -> Result<Vec<Vec<String>>, Box<dyn std::error::Error>> {
    let mut levels = Vec::new();
    let mut remaining: HashSet<String> = jobs.iter().map(|j| j.name.clone()).collect();
    let mut processed = HashSet::new();

    while !remaining.is_empty() {
        let mut current_level = Vec::new();

        // Find all jobs whose dependencies are satisfied
        for job in jobs {
            if remaining.contains(&job.name) {
                let job_deps = deps.get(&job.name).unwrap();
                if job_deps.iter().all(|d| processed.contains(d)) {
                    current_level.push(job.name.clone());
                }
            }
        }

        if current_level.is_empty() {
            return Err("Circular dependency detected in job graph".into());
        }

        // Mark these jobs as processed
        for job in &current_level {
            remaining.remove(job);
            processed.insert(job.clone());
        }

        levels.push(current_level);
    }

    Ok(levels)
}

/// Build stage for workflow start from database models
fn build_workflow_start_stage_from_db(
    jobs: &[JobModel],
    actions: &[WorkflowActionModel],
    dependency_graph: &HashMap<String, Vec<String>>,
    _job_name_to_id: &HashMap<String, i64>,
) -> Result<ExecutionStage, Box<dyn std::error::Error>> {
    let mut scheduler_allocations = Vec::new();

    // Find on_workflow_start actions
    for action in actions {
        if action.trigger_type == "on_workflow_start" {
            if let Some(alloc) = build_scheduler_allocation_from_db_action(action, jobs)? {
                scheduler_allocations.push(alloc);
            }
        }
    }

    // Jobs with empty dependency lists become ready at start
    let mut jobs_becoming_ready = Vec::new();
    for job in jobs {
        if let Some(deps) = dependency_graph.get(&job.name) {
            if deps.is_empty() {
                jobs_becoming_ready.push(job.name.clone());
            }
        }
    }

    Ok(ExecutionStage {
        stage_number: 0,
        trigger_description: "Workflow Start".to_string(),
        scheduler_allocations,
        jobs_becoming_ready,
    })
}

/// Build stage for when a level of jobs completes from database models
fn build_job_completion_stage_from_db(
    jobs: &[JobModel],
    actions: &[WorkflowActionModel],
    stage_number: usize,
    level_idx: usize,
    level_jobs: &[String],
    all_levels: &[Vec<String>],
    job_name_to_id: &HashMap<String, i64>,
) -> Result<ExecutionStage, Box<dyn std::error::Error>> {
    let mut scheduler_allocations = Vec::new();

    // Find jobs that become ready after this level completes
    let jobs_becoming_ready: Vec<String> = if level_idx + 1 < all_levels.len() {
        all_levels[level_idx + 1].clone()
    } else {
        Vec::new()
    };

    // Find on_jobs_ready actions that match the jobs becoming ready
    for action in actions {
        if action.trigger_type == "on_jobs_ready" {
            // Check if this action matches any of the jobs becoming ready
            let empty_vec = vec![];
            let action_job_ids = action.job_ids.as_ref().unwrap_or(&empty_vec);

            let matches_any = action_job_ids.iter().any(|action_job_id| {
                jobs_becoming_ready
                    .iter()
                    .any(|job_name| job_name_to_id.get(job_name) == Some(action_job_id))
            });

            if matches_any {
                if let Some(alloc) = build_scheduler_allocation_from_db_action(action, jobs)? {
                    scheduler_allocations.push(alloc);
                }
            }
        }
    }

    // Build trigger description
    let trigger_description = if level_jobs.len() == 1 {
        format!("When job '{}' completes", level_jobs[0])
    } else if level_jobs.len() <= 3 {
        format!(
            "When jobs {} complete",
            level_jobs
                .iter()
                .map(|j| format!("'{}'", j))
                .collect::<Vec<_>>()
                .join(", ")
        )
    } else {
        format!(
            "When {} jobs complete ({}...)",
            level_jobs.len(),
            level_jobs
                .iter()
                .take(2)
                .map(|j| format!("'{}'", j))
                .collect::<Vec<_>>()
                .join(", ")
        )
    };

    Ok(ExecutionStage {
        stage_number,
        trigger_description,
        scheduler_allocations,
        jobs_becoming_ready,
    })
}

/// Build a scheduler allocation from a database action model
fn build_scheduler_allocation_from_db_action(
    action: &WorkflowActionModel,
    jobs: &[JobModel],
) -> Result<Option<SchedulerAllocation>, Box<dyn std::error::Error>> {
    if action.action_type != "schedule_nodes" {
        return Ok(None);
    }

    // action_config is already a serde_json::Value
    let config = &action.action_config;

    let scheduler_type = config["scheduler_type"]
        .as_str()
        .ok_or("Action config missing scheduler_type")?
        .to_string();

    let num_allocations = config["num_allocations"].as_i64().unwrap_or(1);

    // Get job names from job IDs
    let empty_vec = vec![];
    let action_job_ids = action.job_ids.as_ref().unwrap_or(&empty_vec);
    let mut job_names = Vec::new();
    for job_id in action_job_ids {
        if let Some(job) = jobs.iter().find(|j| j.id == Some(*job_id)) {
            job_names.push(job.name.clone());
        }
    }

    // For scheduler_name, we'd need to look it up from the database
    // For now, use a placeholder based on the scheduler_type
    let scheduler_name = format!("{}_scheduler", scheduler_type);

    Ok(Some(SchedulerAllocation {
        scheduler_name,
        scheduler_type,
        num_allocations,
        job_names,
    }))
}

/// Compact a list of job names by detecting and collapsing sequential patterns
/// e.g., ["job_001", "job_002", "job_003"] -> ["job_{001-003}"]
fn compact_job_list(jobs: &[String]) -> Vec<String> {
    if jobs.is_empty() {
        return vec![];
    }

    if jobs.len() <= 3 {
        return jobs.to_vec();
    }

    // Try to detect pattern: prefix + numeric suffix
    let pattern_re = Regex::new(r"^(.+?)(\d+)$").unwrap();

    #[derive(Debug)]
    struct JobGroup {
        prefix: String,
        numbers: Vec<(usize, String)>, // (numeric_value, original_string)
    }

    let mut groups: HashMap<String, JobGroup> = HashMap::new();
    let mut non_pattern_jobs = Vec::new();

    for job in jobs {
        if let Some(caps) = pattern_re.captures(job) {
            let prefix = caps.get(1).unwrap().as_str().to_string();
            let num_str = caps.get(2).unwrap().as_str();
            let num_val = num_str.parse::<usize>().unwrap();

            groups
                .entry(prefix.clone())
                .or_insert_with(|| JobGroup {
                    prefix: prefix.clone(),
                    numbers: Vec::new(),
                })
                .numbers
                .push((num_val, num_str.to_string()));
        } else {
            non_pattern_jobs.push(job.clone());
        }
    }

    let mut result = Vec::new();

    // Process each group
    for (_, mut group) in groups {
        group.numbers.sort_by_key(|&(n, _)| n);

        if group.numbers.len() <= 3 {
            // Too few to compact, just add them individually
            for (_, num_str) in &group.numbers {
                result.push(format!("{}{}", group.prefix, num_str));
            }
        } else {
            // Check if they're sequential
            let is_sequential = group.numbers.windows(2).all(|w| w[1].0 == w[0].0 + 1);

            if is_sequential {
                // Compact as range
                let first_num = &group.numbers.first().unwrap().1;
                let last_num = &group.numbers.last().unwrap().1;
                result.push(format!("{}{{{}..{}}}", group.prefix, first_num, last_num));
            } else {
                // Not sequential, check for multiple sequential runs
                let mut runs = Vec::new();
                let mut current_run = vec![group.numbers[0].clone()];

                for i in 1..group.numbers.len() {
                    if group.numbers[i].0 == current_run.last().unwrap().0 + 1 {
                        current_run.push(group.numbers[i].clone());
                    } else {
                        runs.push(current_run);
                        current_run = vec![group.numbers[i].clone()];
                    }
                }
                runs.push(current_run);

                // Compact runs that have 4+ elements
                for run in runs {
                    if run.len() >= 4 {
                        let first_num = &run.first().unwrap().1;
                        let last_num = &run.last().unwrap().1;
                        result.push(format!("{}{{{}..{}}}", group.prefix, first_num, last_num));
                    } else {
                        for (_, num_str) in &run {
                            result.push(format!("{}{}", group.prefix, num_str));
                        }
                    }
                }
            }
        }
    }

    // Add non-pattern jobs
    result.extend(non_pattern_jobs);

    result
}
