# Installation

## Precompiled Binaries (Recommended)

Download precompiled binaries from the [releases page](https://github.com/NREL/torc/releases).

**macOS users**: The precompiled binaries are not signed with an Apple Developer certificate. macOS Gatekeeper will block them by default. To allow the binaries to run, remove the quarantine attribute after downloading:

```bash
xattr -cr /path/to/torc*
```

Alternatively, you can right-click each binary and select "Open" to add a security exception.

## Building from Source

### Prerequisites

- Rust 1.70 or later
- SQLite 3.35 or later (usually included with Rust via sqlx)

### Clone the Repository

```bash
git clone https://github.com/NREL/torc.git
cd torc
```

## Building All Components

Note that the file `.env` designates the database URL as `./db/sqlite/dev.db`
Change as desired or set the environment variable `DATABASE_URL`.

**Initialize the database**

```bash
# Install sqlx-cli if needed
cargo install sqlx-cli --no-default-features --features sqlite
sqlx database setup
```

**Build everything (server, client, dashboard, job runners):**

```bash
# Development build
cargo build --workspace

# Release build (optimized, recommended)
cargo build --workspace --release
```

**Build individual components:**

```bash
# Server
cargo build --release -p torc-server

# Client CLI
cargo build --release -p torc

# Web Dashboard
cargo build --release -p torc-dash

# Slurm job runner
cargo build --release -p torc-slurm-job-runner
```

Binaries will be in `target/release/`. We recommend adding this directory
to your system path so that you can run all binaries without specifying the full path.

## For Developers

### Running Tests

# Run all tests
```bash
cargo test -- --test-threads=1

# Run specific test
cargo test --test test_workflow_manager test_initialize_files_with_updated_files

# Run with debug logging
RUST_LOG=debug cargo test -- --nocapture
```

### Setting Up the Server

**Start the server:**

```bash
# Development mode
cargo run -p torc-server -- run

# Production mode (release build)
./target/release/torc-server run

# Custom port
./target/release/torc-server run --port 8080
```

Server will start on `http://localhost:8080`.

When running small workflows for testing and demonstration purposes, we recommend setting this
option so that the server detects job completions faster than the default value of 60 seconds.

```bash
./target/release/torc-server run --completion-check-interval-secs 5
```
