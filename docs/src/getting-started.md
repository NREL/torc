# Getting Started

**Torc** is a distributed workflow orchestration system for managing complex computational pipelines with job dependencies, resource requirements, and distributed execution.

Torc uses a client-server architecture where a central server manages workflow state and coordination, while clients create workflows and job runners execute tasks on compute resources.

## Key Components

- **Server**: REST API service that manages workflow state via a SQLite database
- **Client**: CLI tool and library for creating and managing workflows
- **Job Runner**: Worker process that pulls ready jobs, executes them, and reports results
- **Database**: Central SQLite database that stores all workflow state and coordinates distributed execution

## Features

- **Declarative Workflow Specifications** - Define workflows in YAML, JSON5, JSON, or KDL
- **Automatic Dependency Resolution** - Dependencies inferred from file and data relationships
- **Job Parameterization** - Create parameter sweeps and grid searches with simple syntax
- **Distributed Execution** - Run jobs across multiple compute nodes with resource tracking
- **Slurm Integration** - Native support for HPC cluster job submission
- **Workflow Resumption** - Restart workflows after failures without losing progress
- **Change Detection** - Automatically detect input changes and re-run affected jobs
- **Resource Management** - Track CPU, memory, and GPU usage across all jobs
- **RESTful API** - Complete OpenAPI-specified REST API for integration
