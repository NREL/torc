# Design

This section covers Torc's internal design and implementation details. These topics are intended for developers who want to understand how Torc works internally, contribute to the project, or debug complex issues.

## Contents

- **Server API Handler** - Multi-threaded async web service architecture and key endpoints
- **Central Database** - SQLite schema, concurrency model, and coordination mechanisms
- **Web Dashboard** - Browser-based UI gateway architecture and CLI integration
- **Workflow Recovery** - Recovery mechanisms for preempted or failed Slurm allocations
- **Workflow Graph** - DAG representation for dependency analysis and scheduler planning

For user-facing concepts and guides, see the other Explanation chapters.
