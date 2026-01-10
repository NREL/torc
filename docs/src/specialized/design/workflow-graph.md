# Workflow Graph

The `WorkflowGraph` module provides a directed acyclic graph (DAG) representation of workflow jobs
and their dependencies. It serves as the core data structure for dependency analysis, scheduler
planning, and execution visualization.

## Purpose

The graph abstraction addresses several key challenges:

- **Unified Representation**: Works with both workflow specifications (at creation time) and
  database models (at runtime), providing a consistent interface for graph algorithms
- **Dependency Analysis**: Enables topological sorting, level computation, and critical path
  detection
- **Scheduler Planning**: Groups jobs by resource requirements and dependency status for efficient
  scheduler generation
- **Sub-workflow Detection**: Identifies connected components that can be scheduled independently

## Data Structures

### JobNode

Represents a single job (or parameterized job template) in the graph:

```rust
pub struct JobNode {
    pub name: String,                           // Job name (may contain {param} placeholders)
    pub resource_requirements: Option<String>,  // Resource requirements name
    pub instance_count: usize,                  // 1 for normal jobs, N for parameterized
    pub name_pattern: String,                   // Regex pattern matching all instances
    pub scheduler: Option<String>,              // Assigned scheduler
    pub command: String,                        // Command to execute
}
```

### WorkflowGraph

The main graph structure with bidirectional edges for efficient traversal:

```rust
pub struct WorkflowGraph {
    nodes: HashMap<String, JobNode>,           // Jobs indexed by name
    depends_on: HashMap<String, HashSet<String>>,   // Forward edges (blockers)
    depended_by: HashMap<String, HashSet<String>>,  // Reverse edges (dependents)
    levels: Option<Vec<Vec<String>>>,          // Cached topological levels
    components: Option<Vec<WorkflowComponent>>, // Cached connected components
}
```

### SchedulerGroup

Groups jobs that share scheduling characteristics:

```rust
pub struct SchedulerGroup {
    pub resource_requirements: String,    // Common RR name
    pub has_dependencies: bool,           // Whether jobs have blockers
    pub job_count: usize,                 // Total instances across jobs
    pub job_name_patterns: Vec<String>,   // Regex patterns for matching
    pub job_names: Vec<String>,           // Job names in this group
}
```

## Construction Methods

### From Workflow Specification

```rust
WorkflowGraph::from_spec(&spec) -> Result<Self, Error>
```

Builds the graph at workflow creation time:

1. Creates nodes for each job specification
2. Resolves explicit dependencies (`depends_on`)
3. Resolves regex dependencies (`depends_on_regexes`)
4. Computes implicit dependencies from input/output files and user data

### From Database Models

```rust
WorkflowGraph::from_jobs(jobs, resource_requirements) -> Result<Self, Error>
```

Builds the graph from fetched database records (used for recovery and visualization):

1. Creates nodes from `JobModel` records
2. Resolves dependencies via `depends_on_job_ids` (if available)
3. Falls back to computing dependencies from file relationships

## Key Operations

### Topological Levels

Groups jobs by dependency depth for parallel execution planning:

- Level 0: Jobs with no dependencies (can start immediately)
- Level N: Jobs whose dependencies are all in levels < N

Used for execution ordering and TUI visualization.

### Connected Components

Identifies independent sub-workflows using BFS traversal:

- Each component can be scheduled independently
- Enables parallel execution of unrelated job pipelines
- Useful for large workflows with multiple independent processing chains

### Scheduler Groups

Groups jobs by `(resource_requirements, has_dependencies)` for scheduler generation:

- Jobs without dependencies: Submitted at workflow start
- Jobs with dependencies: Submitted on-demand when jobs become ready
- Enables the shared `generate_scheduler_plan()` function used by both `torc slurm generate` and
  `torc slurm regenerate`

### Critical Path

Finds the longest path through the graph (by instance count):

- Identifies bottleneck jobs that limit parallelism
- Used for estimating minimum execution time
- Helps prioritize optimization efforts

## Integration Points

### Scheduler Plan Generation

The `SchedulerPlan` module uses `WorkflowGraph::scheduler_groups()` to generate Slurm schedulers:

```rust
let graph = WorkflowGraph::from_spec(&spec)?;
let groups = graph.scheduler_groups();
let plan = generate_scheduler_plan(&graph, &resource_requirements, &profile, ...);
```

### Execution Plan Visualization

The execution plan display uses `WorkflowGraph::from_jobs()` for runtime visualization:

```rust
let graph = WorkflowGraph::from_jobs(&jobs, &resource_requirements)?;
let levels = graph.topological_levels()?;
// Render DAG visualization in TUI
```

### Recovery Scenarios

The `regenerate` command uses the graph to determine scheduler groupings for failed workflows:

```rust
let graph = WorkflowGraph::from_jobs(&jobs, &resource_requirements)?;
let plan = generate_scheduler_plan(&graph, ...);
// Apply plan to recreate schedulers and actions
```

## Design Decisions

### Bidirectional Edges

The graph maintains both `depends_on` and `depended_by` maps for O(1) traversal in either direction.
This is critical for:

- Finding what becomes ready when a job completes
- Computing connected components efficiently
- Building subgraphs for partial analysis

### Lazy Computation with Caching

Topological levels and connected components are computed on-demand and cached. This avoids
unnecessary computation for simple queries while ensuring efficient repeated access.

### Parameterized Job Handling

Parameterized jobs are represented as single nodes with `instance_count > 1`. The `name_pattern`
field provides a regex for matching expanded instances, enabling scheduler grouping without full
expansion.
