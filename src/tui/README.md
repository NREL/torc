# Torc TUI - Terminal User Interface

A terminal-based user interface for managing Torc workflows, built with [ratatui](https://ratatui.rs/).

## Features

- **Workflow List**: View all workflows with ID, name, user, and description
- **Dynamic Detail Views**: Switch between Jobs, Files, Events, Results, and DAG visualization for selected workflows
- **DAG Visualization**: Visual representation of job dependencies as a directed acyclic graph
- **Focus Management**: Independent navigation of workflows and detail tables
- **Filtering**: Filter detail views by column values with case-insensitive substring matching
  - Jobs: Filter by Status, Name, or Command
  - Files: Filter by Name or Path
  - Events: Filter by Data
  - Results: Filter by Status or Return Code
- **Server Connection Management**: Change server URL on-the-fly without restarting
- **User Filtering**: Filter workflows by username or show all users' workflows
  - Defaults to current user from environment variables
  - Quick toggle between current user and all users
- **Keyboard Navigation**: Fast, keyboard-driven interface
- **Real-time Data**: Refresh workflows and load details on demand

## Installation

```bash
cd torc-tui
cargo build --release
```

## Usage

First, make sure the Torc server is running:

```bash
# Start the server (from the torc-server directory)
cd torc-server
cargo run --bin torc-server
```

Then run the TUI:

```bash
# Set the server URL (optional, defaults to localhost:8080)
export TORC_BASE_URL="http://localhost:8080/torc-service/v1"

# Run the TUI
cargo run --bin torc-tui
```

## Keyboard Controls

| Key | Action |
|-----|--------|
| `q` | Quit the application |
| `↑` / `↓` | Navigate up/down in the active table |
| `←` / `→` | Toggle focus between Workflows and Details tables |
| `Enter` | Load details for the selected workflow |
| `Tab` | Switch to next detail view (Jobs → Files → Events → Results → DAG) |
| `Shift+Tab` | Switch to previous detail view |
| `r` | Refresh the workflow list |
| `f` | Start filtering (when Details table is focused) |
| `c` | Clear active filter (when Details table is focused) |
| `u` | Change server URL |
| `w` | Change user filter |
| `a` | Toggle show all users |

### Filter Mode Controls

When in filter input mode (press `f` to enter):

| Key | Action |
|-----|--------|
| `Type` | Enter filter value |
| `Tab` / `Shift+Tab` | Cycle through filterable columns |
| `Enter` | Apply the filter |
| `Esc` | Cancel and exit filter mode |

### Server URL Input Controls

When in server URL input mode (press `u` to enter):

| Key | Action |
|-----|--------|
| `Type` | Enter server URL |
| `Enter` | Connect to new server |
| `Esc` | Cancel and keep current connection |

### User Filter Input Controls

When in user filter input mode (press `w` to enter):

| Key | Action |
|-----|--------|
| `Type` | Enter username |
| `Enter` | Apply user filter |
| `Esc` | Cancel and keep current filter |

**Focus Management:** Use Left/Right arrows to switch focus between the workflows table (top) and the detail table (bottom). The focused table will have a green border and "[FOCUSED]" in its title. Only the focused table responds to Up/Down arrow keys.

**Filtering:** When the Details table is focused, press `f` to start filtering. Use Tab to cycle through available columns (varies by view type), type your filter text, and press Enter to apply. The filter performs case-insensitive substring matching. Press `c` to clear the active filter.

**Server Connection:** The current server URL is displayed in the Connection section. Press `u` to change the server URL. The TUI will attempt to connect to the new server and refresh workflows when you press Enter. If the connection fails, the TUI will revert to the previous URL.

**User Filtering:** The User Filter section shows the current user filter. By default, workflows are filtered to the current user (from `USER` or `USERNAME` environment variable). Press `w` to change the user filter to a specific username, or leave it empty and press Enter to show all users. Press `a` to quickly toggle between showing only your workflows and all users' workflows.

## Architecture

The TUI is organized into four main modules:

- **`main.rs`**: Entry point, terminal setup, and synchronous event loop
- **`app.rs`**: Application state management and business logic
- **`api.rs`**: Synchronous API client wrapper for Torc server communication
- **`ui.rs`**: UI rendering logic using ratatui widgets

The TUI is completely synchronous, using the blocking reqwest client from torc. No async runtime overhead!

## Screenshots

The interface is divided into six sections:

1. **Help Bar**: Shows available keyboard shortcuts (context-sensitive based on current mode)
2. **Connection**: Displays current server URL with option to change
3. **User Filter**: Shows current user filter with options to change or toggle all users
4. **Workflows Table**: Lists all workflows with ID, name, user, and description
5. **Tab Bar**: Switch between different detail views
6. **Detail Table**: Shows jobs, files, events, or results for the selected workflow

## Development

The TUI uses:
- **ratatui**: Terminal UI framework
- **crossterm**: Cross-platform terminal manipulation
- **torc client library**: Generated blocking API client from OpenAPI spec

## DAG Visualization

The DAG (Directed Acyclic Graph) view provides a visual representation of job dependencies within a workflow. Each node represents a job, and edges represent blocking relationships (job A blocks job B means B cannot run until A completes).

### Current Implementation

The DAG visualization currently displays all jobs as nodes without edges. To enable full DAG visualization with dependency edges, the server needs to expose the `job_blocked_by` table data.

### Server-Side Implementation Needed

To enable complete DAG visualization, add an API endpoint that returns job blocking relationships:

```rust
// Suggested endpoint in server API
GET /workflows/{workflow_id}/job-dependencies

// Returns:
[
  {
    "job_id": 123,
    "blocked_by_job_id": 456,
    "workflow_id": 789
  },
  ...
]
```

This data comes from the `job_blocked_by` table with columns:
- `job_id`: The job that is blocked
- `blocked_by_job_id`: The job that must complete first
- `workflow_id`: The workflow containing both jobs

Once this endpoint is available, update `TorcClient::list_job_dependencies()` in `torc-tui/src/api.rs` and uncomment the edge-building logic in `App::build_dag_from_jobs()`.

### Visual Features

- **Color-coded nodes** based on job status:
  - Green: Completed
  - Yellow: Running
  - Red: Failed
  - Magenta: Canceled
  - Cyan: Other statuses
- **Layered layout** using topological sort to arrange jobs in dependency order
- **Automatic layout** that scales to available terminal space

## Future Enhancements

Potential improvements:
- Add job blocking relationships API endpoint (see DAG Visualization section)
- Node labels with job names in DAG view
- Interactive DAG navigation (select nodes, zoom)
- Pagination for large result sets
- Sorting options
- Workflow creation/modification UI
- Real-time status updates
- Multi-workflow selection
