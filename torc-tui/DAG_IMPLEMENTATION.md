# DAG Visualization Implementation Guide

This document tracks the implementation of DAG (Directed Acyclic Graph) visualization for job dependencies in the Torc TUI.

## Status: Partially Complete

### ✅ Completed

1. **OpenAPI Specification** (`api/openapi.yaml`)
   - Added `/workflows/{id}/job_dependencies` GET endpoint (line 3661-3705)
   - Added `job_dependency_model` schema (line 4580-4600)
   - Added `list_job_dependencies_response` schema (line 4601-4636)

2. **TUI Dependencies** (`torc-tui/Cargo.toml`)
   - Added `petgraph = "0.6"` for graph data structures

3. **DAG Module** (`torc-tui/src/dag.rs`)
   - Created `JobNode` struct for representing job nodes
   - Implemented `DagLayout` with Sugiyama-style layered layout algorithm
   - Topological sorting for layer assignment
   - Position calculation and normalization

4. **App State** (`torc-tui/src/app.rs`)
   - Added `DetailViewType::Dag` to view types
   - Added `dag: Option<DagLayout>` field
   - Implemented `build_dag_from_jobs()` method (nodes only, edges TODO)
   - Updated `load_detail_data()` to build DAG on view switch

5. **UI Rendering** (`torc-tui/src/ui.rs`)
   - Implemented `draw_dag()` function using text-based layered display
   - Shows job names, IDs, and status for each node
   - Color-coded jobs based on status:
     - Green: Completed (✓)
     - Yellow: Running (▶)
     - Red: Failed (✗)
     - Magenta: Canceled (○)
     - Cyan: Other (◦)
   - Topological layout showing dependency layers with visual flow indicators (↓↓↓)
   - Helper function `dag_compute_layers()` for layer-based topological sort

6. **Documentation** (`torc-tui/README.md`)
   - Added DAG to feature list
   - Added DAG Visualization section explaining implementation
   - Updated keyboard controls for DAG view in Tab rotation

### ✅ Completed: Server-Side Implementation (Partially)

**Location**: `src/server/api/workflows.rs`

Server endpoint has been implemented to query the `job_blocked_by` table with job names included.

**What was completed**:
1. Added `JobDependencyModel` and `ListJobDependenciesResponse` to `src/models.rs` (lines 10404-10471)
   - Includes job_id, job_name, blocked_by_job_id, blocked_by_job_name, workflow_id fields
2. Added `ListJobDependenciesResponse` enum to `src/server/api_types.rs` (lines 297-304)
3. Updated `src/server/routing.rs` imports to include `ListJobDependenciesResponse` (line 40)
4. Added `list_job_dependencies` method to `WorkflowsApi` trait in `src/server/api/workflows.rs` (lines 68-75)
5. Implemented `list_job_dependencies` in `WorkflowsApiImpl` (lines 1041-1124)
   - Queries job_blocked_by with JOINs to get job names from job table
   - Returns paginated results with offset/limit support
   - Includes total count and has_more pagination info

**Implementation**: See `src/server/api/workflows.rs:1041-1124`

The implementation queries the job_blocked_by table with JOINs to retrieve job names:
```sql
SELECT
    jb.job_id as job_id,
    j1.name as job_name,
    jb.blocked_by_job_id as blocked_by_job_id,
    j2.name as blocked_by_job_name,
    jb.workflow_id as workflow_id
FROM job_blocked_by jb
INNER JOIN job j1 ON jb.job_id = j1.id
INNER JOIN job j2 ON jb.blocked_by_job_id = j2.id
WHERE jb.workflow_id = ?
LIMIT ? OFFSET ?
```

### ✅ Completed: Server Routing

**Location**: `src/server/routing.rs`

Server routing has been fully implemented:

1. **Added regex pattern** (line 104):
   ```rust
   r"^/torc-service/v1/workflows/(?P<id>[^/?#]*)/job_dependencies$"
   ```

2. **Added ID constant and regex** (lines 355-361):
   ```rust
   pub(crate) static ID_WORKFLOWS_ID_JOB_DEPENDENCIES: usize = 45;
   lazy_static! {
       pub static ref REGEX_WORKFLOWS_ID_JOB_DEPENDENCIES: regex::Regex =
           #[allow(clippy::invalid_regex)]
           regex::Regex::new(r"^/torc-service/v1/workflows/(?P<id>[^/?#]*)/job_dependencies$")
               .expect("Unable to create regex for WORKFLOWS_ID_JOB_DEPENDENCIES");
   }
   ```

3. **Added routing handler** (lines 7789-7909):
   - Extracts path parameter `id` (workflow_id)
   - Parses optional query parameters: `offset` and `limit`
   - Calls `api_impl.list_job_dependencies()`
   - Returns 200 with JSON on success, 500 on error
   - Handles invalid parameters with 400 Bad Request

**Endpoint is now accessible at**: `GET /torc-service/v1/workflows/{id}/job_dependencies?offset=0&limit=100`

### ✅ Completed: Client-Side Integration

**Location**: `torc-tui/src/api.rs` and `torc-tui/src/app.rs`

**What was completed**:

1. **Added Client Models** (`src/client/models/`):
   - Created `job_dependency_model.rs` with JobDependencyModel struct
   - Created `list_job_dependencies_response.rs` with ListJobDependenciesResponse struct
   - Updated `mod.rs` to export both new models

2. **Added API Function** (`src/client/apis/default_api.rs`):
   - Added `ListJobDependenciesError` enum (lines 403-409)
   - Implemented `list_job_dependencies()` function (lines 3581-3644)
   - Handles path parameter (workflow_id) and query parameters (offset, limit)

3. **Added TUI Client Wrapper** (`torc-tui/src/api.rs:138-148`):
   - Wrapper function that calls the API and returns job dependencies

4. **Completed Edge Building** (`torc-tui/src/app.rs:561-580`):
   - Fetches job dependencies from server API
   - Maps job IDs to graph node indices
   - Creates edges from blocked_by_job_id → job_id
   - Gracefully continues without edges if API call fails

5. **Fixed Pattern Matching**:
   - Updated all match statements in `app.rs` to handle `DetailViewType::Dag`
   - Updated tab selection in `ui.rs` (line 239)
   - DAG view doesn't support filtering or table navigation (returns early from those functions)

## ✅ Implementation Complete!

All code has been implemented and the project builds successfully with zero errors or warnings.

### Final Fix Applied

**Problem**: The routing code in `src/server/routing.rs` called `api_impl.list_job_dependencies()` but the method didn't exist in the `Api` trait.

**Solution**: Added `list_job_dependencies` method to three locations in `src/server/api_types.rs`:
1. `Api<C>` trait definition (lines 1183-1190)
2. `ApiNoContext<C>` trait definition (lines 1906-1912)
3. `ApiNoContext` implementation for `ContextWrapper` (lines 2705-2716)

Also added delegation in `torc-server/src/server.rs` (lines 1635-1646) to forward calls to `self.workflows_api.list_job_dependencies()`.

### Testing Checklist

To test the DAG visualization:

- [ ] Start torc-server: `cargo run --bin torc-server`
- [ ] Create a test workflow with job dependencies
- [ ] Open torc-tui: `cargo run --bin torc-tui`
- [ ] Navigate to a workflow and press Enter
- [ ] Press Tab to cycle to DAG view
- [ ] Press Enter to load DAG
- [ ] Verify jobs appear with names and IDs in layered format
- [ ] Verify dependency flow shows correct order (jobs that must run first appear at top)
- [ ] Verify color coding matches job status:
  - Green (✓) = Completed
  - Yellow (▶) = Running
  - Red (✗) = Failed
  - Magenta (○) = Canceled
  - Cyan (◦) = Other
- [ ] Verify layout is readable with layer separators (↓↓↓) between dependency levels

### Future Enhancements

- [ ] Interactive navigation (select nodes, view job details)
- [ ] Scrolling support for very large DAGs
- [ ] Show dependency details (which files/data connect jobs)
- [ ] Highlight critical path
- [ ] Filter view to show only failed/problematic nodes
- [ ] Export DAG as DOT format for external visualization tools
- [ ] Real-time status updates in DAG view
- [ ] Graphical rendering option (return to Canvas-based visualization with proper text labels)

## Architecture Decisions

**Why vector of structs over DOT format?**
- **Flexibility**: TUI can manipulate graph structure (filter, transform)
- **Simplicity**: Server just returns raw table data, no string parsing
- **Performance**: Efficient data transfer, computation done client-side
- **Extensibility**: Easy to add graph algorithms (path finding, cycle detection)

**Why petgraph?**
- Industry-standard Rust graph library
- Built-in algorithms (topological sort, traversal, etc.)
- Well-documented and maintained
- Type-safe graph operations

**Why Text-Based Rendering (not Canvas)?**
- Canvas widget in Ratatui has limited text rendering capabilities
- Text-based approach allows clear job names and IDs to be displayed
- Easier to read in terminal environments
- Topological layering makes dependencies clear
- Can be extended with scrolling for large workflows
- Users can easily see which jobs block others
