# Torc Server Arguments in Workflow Actions

## Overview

When using workflow actions with `start_server_on_head_node = true`, you can now configure the torc-server instance that runs on the Slurm head node by providing `torc_server_args` in the action configuration.

## Configuration

Add the `torc_server_args` field to your `schedule_nodes` workflow action:

```json
{
  "action_type": "schedule_nodes",
  "action_config": {
    "scheduler_id": 1,
    "scheduler_type": "slurm",
    "num_allocations": 1,
    "start_server_on_head_node": true,
    "torc_server_args": {
      "log_level": "debug",
      "log_dir": "/scratch/torc-logs",
      "database": "/scratch/torc-workflow.db",
      "threads": 4,
      "json_logs": true,
      "auth_file": "/etc/torc/htpasswd",
      "require_auth": true
    }
  }
}
```

## Supported Fields

The `torc_server_args` object supports the following fields:

- **log_level** (string): Log verbosity level. Options: `error`, `warn`, `info`, `debug`, `trace`. Default: `info`
- **log_dir** (string): Directory for log files with automatic rotation. Default: `./torc-server-logs`
- **threads** (integer): Number of worker threads for the server. Default: `1`
- **port** (integer): Port number for the server. Default: `8080`
- **database** (string): Path to SQLite database file
- **auth_file** (string): Path to htpasswd file for authentication
- **require_auth** (boolean): Whether authentication is required for all requests. Default: `false`
- **json_logs** (boolean): Use JSON format for log files. Default: `false`

## Unsupported Fields

The following torc-server flags are **not supported** in the Slurm context:

- **daemon**: Not applicable when running under Slurm job control
- **pid_file**: Not applicable when running under Slurm job control

## Defaults

If `torc_server_args` is not provided or certain fields are omitted, the following defaults apply:

- `log_level`: `info`
- `log_dir`: `./torc-server-logs`
- `threads`: `1`
- `port`: `8080` (required for proper URL construction)

## File Path Considerations

**Important**: All file paths (`database`, `auth_file`, `log_dir`) must be accessible from the Slurm compute nodes. Consider the following:

1. **Shared filesystems**: Use paths on shared filesystems (e.g., `/scratch`, `/home`, NFS mounts)
2. **Permissions**: Ensure the job user has read/write access to the specified paths
3. **Database location**: If using a database file, ensure it's on a shared filesystem accessible from all compute nodes

### Database Path Validation

When a workflow is started or initialized, the system validates database paths specified in `torc_server_args`:

- If the database file **exists**: Verifies it is a regular file (not a directory)
- If the database file **does not exist**: Verifies the parent directory exists and is accessible
  - The parent directory **must exist** before starting the workflow
  - torc-server will create the database file automatically when it starts

**Example validation errors:**

```bash
# Parent directory doesn't exist
Error: Database parent directory '/nonexistent/path' does not exist for database path '/nonexistent/path/torc.db' (action ID: 1). Create the directory or use an existing path.

# Path exists but is not a file
Error: Database path '/scratch/logs' exists but is not a file (action ID: 1)
```

To avoid validation errors:
```bash
# Create the parent directory before starting the workflow
mkdir -p /scratch/torc-dbs
```

## Example Workflow

See `examples/workflow_with_custom_server_on_head_node.yaml` for a complete workflow example that demonstrates:
- Starting torc-server on the Slurm head node
- Custom logging configuration (debug level, JSON format, custom directory)
- Custom database location on shared filesystem
- Custom server performance settings (4 threads)
- Optional authentication configuration (commented out)

## Generated Submission Script

When `torc_server_args` is provided, the generated Slurm submission script will include a command like:

```bash
torc-server --url http://$(hostname):8080 --port 8080 --threads 4 --log-level debug --log-dir /scratch/dthom/torc-logs --database /scratch/dthom/torc-workflow.db --json-logs &
```

With authentication enabled, the command would also include:
```bash
--auth-file /etc/torc/htpasswd --require-auth
```

## Validation

The server validates `torc_server_args` during workflow action creation:

- Must be a JSON object
- Only recognized torc-server flags are allowed
- `daemon` and `pid_file` fields will be rejected with an error message
- Invalid field names will be rejected with a list of supported fields

## Migration

Existing workflow actions without `torc_server_args` will continue to work with default values:

```bash
torc-server --url http://$(hostname):8080 --port 8080 --threads 1 --log-level info --log-dir ./torc-server-logs &
```
