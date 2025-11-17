# Architecture

## Overview

Torc uses a client-server architecture where a central server manages workflow state and coordination, while clients create workflows and job runners execute tasks on compute resources.

**Key Components:**

- **Server**: REST API service that manages workflow state via a SQLite database
- **Client**: CLI tool and library for creating and managing workflows
- **Job Runner**: Worker process that pulls ready jobs, executes them, and reports results
- **Database**: Central SQLite database that stores all workflow state and coordinates distributed execution

## System Diagram

```mermaid
graph TB
    subgraph Server["Torc Server"]
        API["REST API (Tokio 1-thread)<br/>/workflows /jobs /files<br/>/user_data /results"]
        DB["SQLite Database (WAL)<br/>• Workflow state<br/>• Job dependencies<br/>• Resource tracking<br/>• Execution results"]
        API --> DB
    end

    Client["Torc Client<br/>• Create workflows<br/>• Submit specs<br/>• Monitor"]
    Runner1["Job Runner 1<br/>(compute-01)<br/>• Poll for jobs<br/>• Execute tasks<br/>• Report results"]
    RunnerN["Job Runner N<br/>(compute-nn)<br/>• Poll for jobs<br/>• Execute tasks<br/>• Report results"]

    Client -.HTTP/REST.-> API
    Runner1 -.HTTP/REST.-> API
    RunnerN -.HTTP/REST.-> API
```
