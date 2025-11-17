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

Note that the file `.env` designates the database URL as `./db/sqlite/dev.db`
Change as desired or set the environment variable `DATABASE_URL`.

**Initialize the database**

```bash
# Install sqlx-cli if needed
cargo install sqlx-cli --no-default-features --features sqlite
sqlx database setup
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
cargo build --release --bin torc

# Local job runner
cargo build --release -p torc

# Slurm job runner
cargo build --release --bin torc-slurm-job-runner

Binaries will be in `target/release/`. We recommend adding this directory
to your system path so that run all binaries without using the path.

## For Developers

### Running Tests

```bash
# Run all tests
cargo test -- --test-threads=1

# Run specific test
cargo test test_workflow_manager -- --nocapture

# Run with debug logging
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
