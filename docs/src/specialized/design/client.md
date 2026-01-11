# Client

Torc provides client libraries in multiple languages for workflow management.

## Rust Client (Primary)

The Rust client provides both CLI and library interfaces:

### Workflow Creation

- Parse workflow specification files (JSON, JSON5, YAML, KDL)
- Expand parameterized job/file specifications
- Create all workflow components atomically via API calls
- Handle name-to-ID resolution for dependencies

### Workflow Manager

- Start/restart/reinitialize workflow execution
- Track file changes and update database
- Detect changed user_data inputs
- Validate workflow state before initialization

### API Integration

- Auto-generated client from OpenAPI spec
- Pagination support for large result sets
- Retry logic and error handling

### Client Modes

The Rust client operates in multiple modes:

1. **CLI Mode** - Command-line interface for interactive use
2. **Library Mode** - Programmatic API for integration with other tools
3. **Specification Parser** - Reads and expands workflow specifications
4. **API Client** - HTTP client for communicating with the server

## Python Client

The Python client (`torc` package) provides programmatic workflow management for Python users:

- OpenAPI-generated client for full API access
- `make_api()` helper for easy server connection
- `map_function_to_jobs()` for mapping Python functions across parameters
- Integration with Python data science and ML pipelines

See [Creating Workflows](../../core/workflows/creating-workflows.md#using-the-python-api) for usage
examples.

## Julia Client

The Julia client (`Torc.jl` package) provides programmatic workflow management for Julia users:

- OpenAPI-generated client for full API access
- `make_api()` helper for easy server connection
- `send_api_command()` wrapper with error handling
- `add_jobs()` for batch job creation
- `map_function_to_jobs()` for mapping Julia functions across parameters

See [Creating Workflows](../../core/workflows/creating-workflows.md#using-the-julia-api) for usage
examples.
