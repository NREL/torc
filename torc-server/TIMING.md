# Timing Instrumentation Guide

The Torc server has been instrumented with `tracing-timing` to collect performance metrics for key
operations.

## How to View Timing Stats

**Quick Answer:** Set the `TORC_TIMING_ENABLED` environment variable and run the server with DEBUG
logging:

```bash
TORC_TIMING_ENABLED=1 RUST_LOG=debug cargo run -p torc-server -- run
```

Look for log lines that show timing information after each instrumented function completes.

**Note:**

- Timing instrumentation is disabled by default to reduce log noise. Set `TORC_TIMING_ENABLED=1` or
  `TORC_TIMING_ENABLED=true` to enable it.
- The instrumented functions emit logs at DEBUG level, so you must use `RUST_LOG=debug` or
  `RUST_LOG=trace` to see them.
- Without `TORC_TIMING_ENABLED=1`, you'll only see explicit INFO-level log messages, not span/timing
  data.

## Instrumented Functions

### Server API (`torc-server/src/server.rs`)

- `get_pending_actions` - Get pending workflow actions
- `claim_action` - Atomically claim a workflow action
- `get_ready_job_requirements` - Get resource requirements for ready jobs
- `is_workflow_complete` - Check if workflow is complete
- `claim_jobs_based_on_resources` - Claim jobs matching resource requirements
- `claim_next_jobs` - Claim next available jobs
- `process_changed_job_inputs` - Check and update jobs with changed inputs
- `manage_status_change` - Manage job status transitions
- `start_job` - Start a job
- `complete_job` - Complete a job
- **`prepare_ready_jobs`** - **CRITICAL** - Select jobs from database with write locks

### Jobs API (`src/server/api/jobs.rs`)

- `create_job` - Create single job
- `create_jobs` - Bulk job creation
- `get_job` - Retrieve job with relationships
- `list_jobs` - List/filter jobs
- `update_job_status` - Update job status
- `claim_next_jobs` - Claim jobs for execution
- `process_changed_job_inputs` - Process changed inputs

### Workflows API (`src/server/api/workflows.rs`)

- `create_workflow` - Create workflow
- `cancel_workflow` - Cancel workflow
- `get_workflow_status` - Get workflow status
- `is_workflow_complete` - Check workflow completion
- `list_workflows` - List workflows
- `reset_workflow_status` - Reset workflow status

## Viewing Timing Data

### Option 1: RUST_LOG with TORC_TIMING_ENABLED (Simplest)

Enable timing instrumentation and run the server with DEBUG or TRACE logging:

```bash
TORC_TIMING_ENABLED=1 RUST_LOG=debug cargo run -p torc-server -- run 2>&1 | tee server.log
```

You'll see output like:

```
DEBUG prepare_ready_jobs{workflow_id=1 limit=10}: close time.busy=15.2ms time.idle=0.1ms
```

Note: Without `TORC_TIMING_ENABLED=1`, instrumented functions don't produce any log output, even at
DEBUG level.

Filter for timing data:

```bash
grep "close time" server.log
```

### Option 2: tokio-console (Best for Real-Time Monitoring)

For real-time performance monitoring with a nice TUI:

1. **One-time setup:**
   ```bash
   cargo install tokio-console
   ```

2. **Add console-subscriber to dependencies:**
   ```toml
   # In torc-server/Cargo.toml
   [dependencies]
   console-subscriber = "0.2"
   ```

3. **Initialize console subscriber in main.rs:**
   ```rust
   console_subscriber::init();
   ```

4. **Run server:**
   ```bash
   RUSTFLAGS="--cfg tokio_unstable" cargo run -p torc-server -- run
   ```

5. **View in separate terminal:**
   ```bash
   tokio-console
   ```

### Option 3: OpenTelemetry/Jaeger (Production-Ready)

For production monitoring, export to Jaeger or another OpenTelemetry backend:

1. **Add dependencies:**
   ```toml
   opentelemetry = "0.20"
   opentelemetry-jaeger = "0.19"
   tracing-opentelemetry = "0.21"
   ```

2. **Run Jaeger:**
   ```bash
   docker run -d -p16686:16686 -p6831:6831/udp jaegertracing/all-in-one:latest
   ```

3. **Configure tracer in code** and visit `http://localhost:16686` to view traces

## Performance Testing Workflow

1. **Start the server with timing enabled:**
   ```bash
   TORC_TIMING_ENABLED=1 RUST_LOG=debug cargo run -p torc-server -- run 2>&1 | tee server.log
   ```

2. **Run your workflow with many jobs:**
   ```bash
   # Create workflow
   torc workflows create examples/hundred_jobs.yaml

   # Get workflow ID from output
   WORKFLOW_ID=<id>

   # Start workflow
   torc workflows start $WORKFLOW_ID

   # Run multiple workers
   for i in {1..10}; do
       torc run http://localhost:8080/torc-service/v1 run $WORKFLOW_ID --output-dir ./output_$i &
   done
   ```

3. **Monitor the logs** to see timing information for each instrumented function call

4. **Analyze results:**
   ```bash
   # See all timing data
   grep "close time" server.log

   # Count calls to specific functions
   grep "prepare_ready_jobs.*close" server.log | wc -l

   # Extract timing values
   grep "prepare_ready_jobs.*close" server.log | grep -oP 'time\.busy=\K[0-9.]+ms'
   ```

## What Gets Measured

For each instrumented function, `tracing-timing` records:

- **Entry/exit times** - Total duration of function execution
- **Nested spans** - If an instrumented function calls another, the hierarchy is tracked
- **Span attributes** - Key parameters like workflow_id, job_id, etc.

## Critical Performance Functions

Pay special attention to these functions in multi-worker scenarios:

- **`prepare_ready_jobs`** - Uses SQLite `BEGIN IMMEDIATE TRANSACTION` to prevent race conditions.
  This is likely your bottleneck with many workers.
- **`claim_jobs_based_on_resources`** - Main job claiming endpoint, calls `prepare_ready_jobs`
- **`complete_job`** - Triggers dependent jobs, can cascade
- **`manage_status_change`** - Updates job status and manages side effects
- **`create_jobs`** - Bulk job creation, critical for workflow initialization

## Why No Built-in Timing Report Endpoint?

Due to Rust's ownership model and the `tracing-timing` API design, the timing layer must be moved
into the tracing subscriber and cannot be easily accessed afterward. The cleanest solutions are:

1. **Use trace logging** (shown above) - Simple and always works
2. **Use `tokio-console`** - Best for development
3. **Use OpenTelemetry** - Best for production

These external tools provide richer visualizations and better analysis capabilities than a simple
HTTP endpoint would.

## Example Analysis

After running a workflow with 100 jobs and 10 workers:

```bash
# Extract all prepare_ready_jobs timings
grep "prepare_ready_jobs.*close" server.log | grep -oP 'time\.busy=\K[0-9.]+' > timings.txt

# Calculate statistics
cat timings.txt | awk '{sum+=$1; sumsq+=$1*$1} END {
  print "Count:", NR;
  print "Mean:", sum/NR "ms";
  print "StdDev:", sqrt(sumsq/NR - (sum/NR)^2) "ms"
}'
```

This will show you the average time spent in the critical `prepare_ready_jobs` function and help
identify performance bottlenecks.
