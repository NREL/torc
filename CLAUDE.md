# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Torc** is a distributed workflow orchestration system designed for managing complex computational pipelines with job dependencies, resource requirements, and distributed execution. The system uses a client-server architecture where:

- **Server**: REST API service (Rust) that manages workflow state, job dependencies, and provides a SQLite database for persistence
- **Unified CLI**: Single `torc` binary providing all client functionality (workflow management, job execution, TUI, resource plotting)
- **Standalone Binaries**: Optional specialized binaries (`torc`, `torc-server`, `torc-slurm-job-runner`) for deployment scenarios
- **Python Client**: CLI and library for workflow management (primarily for Python-based workflows)

**Core Concepts:**
- **Workflows**: Top-level containers for related computational jobs with a unique ID
- **Jobs**: Individual computational tasks with dependencies, resource requirements, and status tracking (uninitialized → ready → scheduled → pending → running → running → completed/failed/canceled)
- **Files & User Data**: Input/output artifacts that establish implicit job dependencies
- **Resource Requirements**: CPU, memory, GPU, and runtime specifications per job
- **Schedulers**: Local or Slurm-based job execution environments
- **Compute Nodes**: Available compute resources for job execution

## Repository Structure

```
torc/
├── src/                 # Main torc library and unified CLI
│   ├── client/          # Client modules
│   │   ├── commands/    # CLI command handlers
│   │   ├── apis/        # Generated API client
│   │   ├── workflow_spec.rs    # Workflow specification system
│   │   ├── workflow_manager.rs # Workflow lifecycle management
│   │   ├── job_runner.rs       # Local job execution engine
│   │   └── async_cli_command.rs # Non-blocking job execution
│   ├── server/          # Server implementation modules
│   │   └── api/         # Modular API implementations
│   ├── tui/             # Interactive terminal UI modules
│   ├── run_jobs_cmd.rs  # Job runner command module
│   ├── tui_runner.rs    # TUI runner command module
│   ├── plot_resources_cmd.rs # Plot resources command module
│   ├── main.rs          # Unified CLI entry point
│   ├── lib.rs           # Library root
│   └── models.rs        # Shared data models
├── torc-server/         # Standalone server binary
├── torc-tui/            # Standalone TUI binary
├── torc-plot-resources/ # Standalone plotting binary
├── torc-slurm-job-runner/ # Slurm job runner binary
├── python_client/       # Python CLI client and library
│   ├── src/torc/        # Python package
│   └── pyproject.toml   # Python project configuration
└── examples/            # Example workflow specifications
```

## Component-Specific Guidance

**For server development**, see `server/CLAUDE.md` for:
- Server build, test, and run commands
- Database migration management
- API endpoint implementation patterns
- Job status lifecycle and critical operations
- Database schema and concurrency model

**For Rust client development**:
- All client code is in `src/client/`
- Unified CLI is built with: `cargo build --bin torc --features "client,tui,plot_resources"`
- Workflow specification system in `src/client/workflow_spec.rs` (JSON/JSON5/YAML formats)
- Workflow manager and job runner in `src/client/`
- API client integration patterns in `src/client/apis/`
- Resource management and job execution in `src/client/job_runner.rs`

**For Python client development**:
- Package is managed with setuptools and pyproject.toml
- CLI entry point: `torc` command
- Development setup: `pip install -e .[dev]` from python_client directory

## Quick Start Commands

### Server Operations
```bash
cd server

# Build and run server (requires DATABASE_URL in .env)
cargo build --release
cargo run --bin torc-server

# Run tests
cargo test

# Run specific test
cargo test test_get_ready_jobs -- --nocapture

# Database migrations
sqlx migrate run
sqlx migrate revert
```

### Unified CLI Operations
```bash
# Build unified torc CLI
cargo build --release --bin torc --features "client,tui,plot_resources"

# Set server URL (optional, defaults to localhost:8080)
export TORC_API_URL="http://localhost:8080/torc-service/v1"

# Quick workflow execution (convenience commands)
./target/release/torc run examples/sample_workflow.yaml    # Create and run locally
./target/release/torc submit examples/sample_workflow.yaml # Create and submit to scheduler

# Or use explicit workflow management
./target/release/torc workflows create examples/sample_workflow.yaml
./target/release/torc workflows submit <workflow_id>  # Submit to scheduler
./target/release/torc workflows run <workflow_id>     # Run locally

# Other commands
./target/release/torc tui                              # Launch interactive TUI
./target/release/torc plot-resources output/resource_metrics.db # Generate plots
./target/release/torc workflows list                   # List workflows
./target/release/torc jobs list <workflow_id>          # View job status

# Run tests
cargo test
```

### Standalone Binaries (for deployment)
```bash
# Build individual binaries
cargo build --release --bin torc
cargo build --release --bin torc-server

# Use standalone binaries
```

### Python Client Operations
```bash
cd python_client

# Setup development environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]

# Run CLI
torc --help

# Run tests
pytest
```

## Architecture Overview

### Server Architecture

The server uses a **modular API structure** where each resource type (workflows, jobs, files, events, etc.) has its own module in `server/src/bin/server/api/`. Key architectural decisions:

- **Async Tokio Runtime**: 8-worker-thread runtime handles concurrent HTTP requests
- **SQLite with Write Locks**: `BEGIN IMMEDIATE TRANSACTION` prevents race conditions in job selection
- **Foreign Key Cascades**: Deleting a workflow automatically removes all associated resources
- **OpenAPI-Generated Base**: Core types and routing generated from OpenAPI spec

**Critical Thread Safety**: The `claim_next_jobs` endpoint uses database-level write locks to prevent multiple workers from double-allocating jobs to different clients.

### Client Architecture

The Rust client provides a **unified CLI and library interface** with these key components:

1. **Workflow Specification System** (`src/client/workflow_spec.rs`): Declarative workflow definitions in JSON/JSON5/YAML with automatic dependency resolution and name-to-ID mapping

2. **Workflow Manager** (`src/client/workflow_manager.rs`): Handles workflow lifecycle (start, restart, initialization, validation)

3. **Job Runner** (`src/client/job_runner.rs`): Local parallel job execution with resource management (CPU, memory, GPU tracking) and polling-based status updates

4. **Async CLI Command** (`src/client/async_cli_command.rs`): Non-blocking subprocess execution for running jobs without blocking the runner

5. **Command Modules**: Binary-specific command modules (`src/run_jobs_cmd.rs`, `src/tui_runner.rs`, `src/plot_resources_cmd.rs`) that are re-used by both the unified CLI and standalone binaries

6. **Interactive TUI** (`src/tui/`): Terminal-based UI for workflow monitoring and management

### Data Flow

1. **Workflow Creation**: User creates workflow from spec file → Server creates workflow, files, jobs, dependencies → Returns workflow_id

2. **Initialization**: Client calls `initialize_jobs` → Server builds dependency graph from file/user_data relationships → Jobs with satisfied dependencies marked `ready`

3. **Execution**: Job runner polls server for ready jobs → Checks available resources → Submits jobs via AsyncCliCommand → Monitors completion → Updates server status → Triggers dependent jobs

## Testing Strategy

### Server Tests
- Integration tests in `server/tests/`
- Test database operations with actual SQLite
- Focus on job status transitions and workflow state management
- Run with: `cargo test` from server directory

### Rust Client Tests
- Integration tests in `rust-client/tests/`
- Use `serial_test` attribute for tests that modify shared state
- Test utilities in `tests/common/`
- Run with: `cargo test` from rust-client directory

### Python Client Tests
- Unit and integration tests in `python_client/tests/`
- Run with: `pytest` from python_client directory

## Important Notes

### Job Status as Integer
Job status values are stored as INTEGER (0-8) in the database, not strings:
- 0 = uninitialized
- 1 = ready
- 2 = scheduled
- 3 = pending
- 4 = running
- 5 = running
- 6 = completed
- 7 = failed
- 8 = canceled

### Resource Formats
- **Memory**: String format like "1m", "2g", "512k"
- **Runtime**: ISO8601 duration format (e.g., "PT30M" for 30 minutes, "PT2H" for 2 hours, "P0DT1M" for 1 minute)
- **Timestamps**: Unix timestamps as float64 for file modification times

### Dependencies
- **Explicit**: Defined in `job_blocked_by` table
- **Implicit**: Derived from file and user_data input/output relationships
- **Resolution**: Job specifications use names (`blocked_by`), which are resolved to IDs during creation

### Job and File Parameterization
JobSpec and FileSpec support **parameterization** to automatically generate multiple instances from a single specification:
- **Purpose**: Create parameter sweeps, hyperparameter tuning, or multi-dataset workflows without manual duplication
- **Syntax**: Add `parameters` field with parameter names and values (ranges, lists, or single values)
- **Expansion**: During `create_workflow_from_spec()`, parameterized specs are expanded via Cartesian product before creation
- **Template Substitution**: Use `{param_name}` or `{param_name:format}` in names, commands, paths, and dependencies
- **Format Specifiers**:
  - `{i:03d}` for zero-padded integers (e.g., 001, 042, 100)
  - `{lr:.4f}` for float precision (e.g., 0.0010, 0.1000)
- **Parameter Formats**:
  - Integer ranges: `"1:100"` (inclusive) or `"0:100:10"` (with step)
  - Float ranges: `"0.0:1.0:0.1"`
  - Lists: `"[1,5,10]"` or `"['train','test','validation']"`
- **Multi-dimensional**: Multiple parameters create Cartesian product (e.g., 3 learning rates × 3 batch sizes = 9 jobs)
- **Implementation**: `parameter_expansion.rs` module with `ParameterValue` enum and expansion functions
- **Examples**: See `examples/hundred_jobs_parameterized.yaml`, `hyperparameter_sweep.yaml`, and `data_pipeline_parameterized.yaml`

### Pagination
List endpoints support `offset` and `limit` query parameters:
- Default limit: 10,000 records
- Maximum limit: 10,000 records (enforced)

### OpenAPI Code Generation
- Server and client use OpenAPI-generated code for base types and routing
- **Do not modify** generated code directly
- Implement business logic in non-generated modules (e.g., `server/src/bin/server/api/*.rs`)

## Common Tasks

### Adding a New API Endpoint
1. Update OpenAPI spec (external to this repo)
2. Regenerate API code
3. Add implementation in appropriate `src/server/api/*.rs` module
4. Update client API in `src/client/apis/`
5. Add CLI command handler if needed in `src/client/commands/`

### Creating a Workflow from Specification
1. Write workflow spec file (JSON/JSON5/YAML) following `WorkflowSpec` format
2. See `examples/sample_workflow.json` for complete example
3. Run: `torc workflows create <spec_file>`
4. The command creates all components (workflow, jobs, files, user_data, schedulers) atomically
5. If any step fails, the entire workflow is rolled back

### Running a Workflow Locally
**Quick method:**
- `torc run <spec_file>` - Create from spec and run locally in one step
- `torc run <workflow_id>` - Run existing workflow locally

**Explicit method:**
1. Create workflow: `torc workflows create <spec_file>`
2. Run workflow: `torc workflows run <workflow_id>`
3. Monitor progress: `torc workflows status <workflow_id>`
4. View job results: `torc jobs list <workflow_id>`
5. Launch interactive UI: `torc tui`

### Submitting a Workflow to Scheduler
**Quick method:**
- `torc submit <spec_file>` - Create from spec and submit to scheduler (requires on_workflow_start/schedule_nodes action)
- `torc submit <workflow_id>` - Submit existing workflow to scheduler

**Explicit method:**
1. Create workflow: `torc workflows create <spec_file>`
2. Submit workflow: `torc workflows submit <workflow_id>`

### Debugging

**Server SQL Queries**:
```bash
RUST_LOG=sqlx=debug cargo run --bin torc-server
```

**Client Verbose Output**:
```bash
RUST_LOG=debug torc workflows list
```

**Database Inspection**:
```bash
sqlite3 server/db/sqlite/dev.db
```

## Configuration

### Server Configuration
- `DATABASE_URL`: SQLite database path (configured in `.env`)
- Default: `sqlite:db/sqlite/dev.db`

### Client Configuration
- `TORC_API_URL`: Torc service URL (env var or `--url` flag)
- Default: `http://localhost:8080/torc-service/v1`
- `USER` or `USERNAME`: Workflow owner (auto-detected from environment)

## Development Workflow

1. **Start Server** (standalone binary): `cargo run --bin torc-server`
2. **Build Unified CLI**: `cargo build --release --bin torc --features "client,tui,plot_resources"`
3. **Quick Execution**: `torc run examples/sample_workflow.yaml` OR `torc submit examples/sample_workflow.yaml`
4. **Or Explicit**: `torc workflows create examples/sample_workflow.yaml` → `torc workflows run <id>`
5. **Monitor**: `torc workflows status <id>` or `torc tui`

**Note**: The server is always run as a standalone binary (`torc-server`), not through the unified CLI.

## CLI Commands Quick Reference

**Quick Workflow Execution** (convenience commands):
- `torc run <spec_file|id>` - Create from spec and run locally, or run existing workflow
- `torc submit <spec_file|id>` - Create from spec and submit to scheduler, or submit existing workflow

**Workflow Management**:
- `torc workflows create <file>` - Create workflow from specification
- `torc workflows new` - Create empty workflow interactively
- `torc workflows list` - List all workflows
- `torc workflows submit <id>` - Submit workflow to scheduler (requires on_workflow_start/schedule_nodes action)
- `torc workflows run <id>` - Run workflow locally
- `torc workflows initialize <id>` - Initialize workflow (set up dependencies without execution)
- `torc workflows status <id>` - Check workflow status
- `torc workflows cancel <id>` - Cancel workflow

**Job Management**:
- `torc jobs list <workflow_id>` - List jobs for workflow
- `torc jobs get <job_id>` - Get job details
- `torc jobs update <job_id>` - Update job status

**Execution**:
- `torc run <workflow_spec_or_id>` - Run workflow locally (top-level command)
- `torc submit <workflow_spec_or_id>` - Submit workflow to scheduler (top-level command)
- `torc tui` - Interactive terminal UI

**Utilities**:
- `torc plot-resources <db>` - Generate resource plots
- `torc reports <subcommand>` - Generate reports

**Global Options** (available on all commands):
- `--url <URL>` - Torc server URL (can also use `TORC_API_URL` env var)
- `-f, --format <FORMAT>` - Output format (table or json)

## Additional Resources

- Example workflow specifications: `examples/`
- API documentation: Generated from OpenAPI spec
