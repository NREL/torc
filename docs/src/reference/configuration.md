# Configuration

## Server Configuration

Set via environment variables or `.env` file:

### DATABASE_URL

SQLite database path.

**Default**: `sqlite:torc.db`

**Example**:
```bash
DATABASE_URL=sqlite:torc.db
```

### RUST_LOG

Logging level for server output.

**Default**: `info`

**Valid values**: `error`, `warn`, `info`, `debug`, `trace`

**Example**:
```bash
RUST_LOG=debug
```

### TORC_COMPLETION_CHECK_INTERVAL_SECS

Interval (in seconds) for the background task that processes job completions and unblocks downstream dependent jobs.

**Default**: `60.0`

**Recommended values**:
- **Production**: `60` - Efficient batching, minimal overhead
- **Development/Demos**: `1.0` to `5.0` - Faster feedback for short jobs
- **Testing**: `0.1` - Near-immediate unblocking for integration tests

**Example**:
```bash
TORC_COMPLETION_CHECK_INTERVAL_SECS=1.0
```

**Performance implications**:
- Shorter intervals provide faster downstream job propagation but increase database load
- Longer intervals batch more completions together for higher efficiency
- For HPC workflows with minute-to-hour long jobs, the default 60 seconds is negligible

### Server Port

Set via command-line flag:

```bash
torc-server --port 8080
```

**Default**: `8080`

## Client Configuration

### TORC_API_URL

Torc server URL endpoint.

**Default**: `http://localhost:8080/torc-service/v1`

**Example**:
```bash
export TORC_API_URL="http://my-server:8080/torc-service/v1"
```

Can also be set via `--url` flag:
```bash
torc --url "http://my-server:8080/torc-service/v1" workflows list
```

### USER / USERNAME

Workflow owner username.

**Default**: Auto-detected from environment

**Example**:
```bash
export USER=alice
```

## Database Configuration

### WAL Mode

Torc uses SQLite in WAL (Write-Ahead Logging) mode for better concurrency.

This is configured automatically in the migrations.

### Pragma Settings

The following SQLite pragmas are set:
- `journal_mode = WAL`
- `foreign_keys = ON`
- `busy_timeout = 5000`

## Job Runner Configuration

### Job Allocation Strategy

The job runner supports two allocation strategies controlled by the `--max-parallel-jobs` flag:

#### Resource-Based Allocation (Default)

**When**: `--max-parallel-jobs` is NOT set

```bash
torc run $WORKFLOW_ID \
  --num-cpus 32 \
  --memory-gb 256 \
  --num-gpus 8
```

Uses the server's `claim_jobs_based_on_resources` endpoint which filters jobs based on available compute resources. Jobs must have resource requirements defined.

#### Simple Queue-Based Allocation

**When**: `--max-parallel-jobs` IS set

```bash
torc run $WORKFLOW_ID \
  --max-parallel-jobs 10
```

Uses the server's `claim_next_jobs` endpoint which returns the next N ready jobs from the queue, ignoring resource requirements. Useful for homogeneous workloads or simple parallelism control.

### Resource Limits

Configure via compute node registration or command-line flags:

**Via CLI**:
```bash
torc run $WORKFLOW_ID \
  --num-cpus 32 \
  --memory-gb 256 \
  --num-gpus 8 \
  --num-nodes 1
```

**Via compute node registration**:
```bash
torc compute-nodes create \
  --workflow-id $WORKFLOW_ID \
  --hostname $(hostname) \
  --num-cpus 32 \
  --memory "256g" \
  --num-gpus 8 \
  --is-active true
```

### Polling Interval

Job runners poll the server for ready jobs. Configure via `--poll-interval`:

**Default**: 60 seconds

**Example**:
```bash
torc run $WORKFLOW_ID --poll-interval 30.0
```

Shorter intervals provide faster job pickup but increase server load.
