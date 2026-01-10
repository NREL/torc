# Architecture

## Overview

Torc uses a client-server architecture where a central server manages workflow state and
coordination, while clients create workflows and job runners execute tasks on compute resources.

```mermaid
flowchart TB
    subgraph ui["User Interfaces"]
        DASH["torc-dash<br/>(web)"]
        TUI["torc tui<br/>(terminal)"]
        CLI["torc CLI"]
    end

    subgraph server["Server (torc-server)"]
        API["HTTP API"]
        DB[(SQLite)]
        API <--> DB
    end

    subgraph workers["Job Runners"]
        W1["Runner 1"]
        W2["Runner 2"]
        WN["Runner N"]
    end

    DASH -->|"HTTP"| API
    DASH -->|"executes"| CLI
    TUI -->|"HTTP"| API
    TUI -->|"executes"| CLI
    CLI -->|"HTTP"| API
    W1 -->|"claim jobs"| API
    W2 -->|"claim jobs"| API
    WN -->|"claim jobs"| API

    style DASH fill:#17a2b8,color:#fff
    style TUI fill:#17a2b8,color:#fff
    style CLI fill:#4a9eff,color:#fff
    style API fill:#28a745,color:#fff
    style DB fill:#28a745,color:#fff
    style W1 fill:#ffc107,color:#000
    style W2 fill:#ffc107,color:#000
    style WN fill:#ffc107,color:#000
```

**Key Components:**

| Component      | Description                                                                  |
| -------------- | ---------------------------------------------------------------------------- |
| **torc-dash**  | Web dashboard for visual workflow management                                 |
| **torc tui**   | Terminal UI for monitoring in SSH environments                               |
| **torc CLI**   | Command-line tool for all workflow operations                                |
| **Server**     | HTTP API service that manages workflow state via SQLite                      |
| **Job Runner** | Worker process that polls for ready jobs, executes them, and reports results |
