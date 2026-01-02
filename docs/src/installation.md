# Installation

## Precompiled Binaries (Recommended)

Download precompiled binaries from the [releases page](https://github.com/NREL/torc/releases).

TODO DT: add hpc-specific links so that we can point to /scratch/dthom/torc/latest

**macOS users**: The precompiled binaries are not signed with an Apple Developer certificate. macOS
Gatekeeper will block them by default. To allow the binaries to run, remove the quarantine attribute
after downloading:

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

Note that the file `.env` designates the database URL as `./db/sqlite/dev.db` Change as desired or
set the environment variable `DATABASE_URL`.

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
TODO DT: system path is required for dash and tui

Binaries will be in `target/release/`. We recommend adding this directory to your system path so
that you can run all binaries without specifying the full path.

## Python Client

The Python client provides programmatic workflow management for Python users.

### Prerequisites

- Python 3.11 or later

### Installation

TODO DT: update pypi

```bash
pip install "torc @ git+https://github.com/NREL/torc.git#subdirectory=python_client"
```

The `pytorc` command will be available after installation.

## Julia Client

The Julia client provides programmatic workflow management for Julia users.

### Prerequisites

TODO DT: register on Julia package registry
TODO DT: add Sienna automation

- Julia 1.10 or later

### Installation

Since the package is not yet registered in the Julia General registry, install it directly from
GitHub:

```julia
using Pkg
Pkg.add(url="https://github.com/NREL/torc.git", subdir="julia_client/Torc")
```

Then use it in your code:

```julia
using Torc
```

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
option so that the server detects job completions faster than the default value of 30 seconds.

```bash
./target/release/torc-server run --completion-check-interval-secs 5
```
