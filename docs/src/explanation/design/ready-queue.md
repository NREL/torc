# Ready Queue

The `ready_queue` table is an optimization for large workflows.

## Problem

In large workflows, repeatedly querying the `job` table to find ready jobs is expensive:

```sql
SELECT * FROM job
WHERE workflow_id = ?
  AND status = 'ready'
ORDER BY priority DESC
```

This query scans many rows even when few jobs are ready.

## Solution

Maintain a separate `ready_queue` table that only contains ready job IDs:


## Maintenance

- When a job becomes `ready`, insert into `ready_queue`
- When a job is allocated to a worker (`pending` status), delete from `ready_queue`

## Benefits

- Fast queries for ready jobs (small table, indexed)
- Supports priority-based scheduling
- Enables efficient polling by multiple workers
- Scales to very large workflows

The `claim_next_jobs` endpoint uses the ready queue with database-level write locks to prevent race conditions when multiple workers request jobs simultaneously.

## Performance Impact

Without ready queue:
- Query time grows with total job count
- 10,000 jobs: ~100ms per query
- Multiple workers cause lock contention

With ready queue:
- Query time constant regardless of total jobs
- 10,000 jobs: ~5ms per query
- Better concurrent worker performance
