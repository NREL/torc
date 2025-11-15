# Installation

## Prerequisites

- Rust 1.70 or later
- SQLite 3.35 or later (usually included with Rust via sqlx)

## Clone the Repository

```bash
git clone https://github.com/NREL/torc.git
cd torc
```

## Building All Components

**Create environment configuration:**

Update `.env` file in repository root:

```bash
DATABASE_URL=sqlite:torc.db
```

Alternatively, set the `DATABASE_URL` environment variable in your shell.

**Initialize the database**

```bash
# Install sqlx-cli if needed
cargo install sqlx-cli --no-default-features --features sqlite
sqlx migrate create
sqlx database reset
```

**Build everything (server, client, job runners):**

```bash
# Development build
cargo build --workspace

# Release build (optimized, recommended)
cargo build --workspace --release
```

**Build individual components:**

```bash
# Server
cargo build --release --bin torc-server

# Client CLI
cargo build --release --bin torc-client

# Local job runner
cargo build --release -p torc

# Slurm job runner
cargo build --release --bin torc-slurm-job-runner

# TUI (Terminal UI)
cargo build --release --bin torc-tui
```

Binaries will be in `target/release/`. We recommend adding this directory
to your system path so that run all binaries without using the path.

We also recommend setting the environment variable RUST_LOG=info so that server
and client logs are displayed in the console.

## For Developers

### Running Tests

```bash
# Run all tests
cargo test

# Run specific test
cargo test test_workflow_manager -- --nocapture

# Run with logging
RUST_LOG=info cargo test -- --nocapture
```

### Setting Up the Server

**Start the server:**

```bash
# Development mode
cargo run -p torc-server

# Production mode (release build)
./target/release/torc-server

# Custom port
./target/release/torc-server --port 8080
```

Server will start on `http://localhost:8080`.
