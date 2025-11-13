# Client

The Rust client provides both CLI and library interfaces for workflow management:

## Workflow Creation

- Parse workflow specification files (JSON, JSON5, YAML, KDL)
- Expand parameterized job/file specifications
- Create all workflow components atomically via API calls
- Handle name-to-ID resolution for dependencies

## Workflow Manager

- Start/restart/reinitialize workflow execution
- Track file changes and update database
- Detect changed user_data inputs
- Validate workflow state before initialization

## API Integration

- Auto-generated client from OpenAPI spec
- Pagination support for large result sets
- Retry logic and error handling

## Client Modes

The client operates in multiple modes:

1. **CLI Mode** - Command-line interface for interactive use
2. **Library Mode** - Programmatic API for integration with other tools
3. **Specification Parser** - Reads and expands workflow specifications
4. **API Client** - HTTP client for communicating with the server
