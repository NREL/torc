# How to Check Resource Utilization

Compare actual resource usage against specified requirements to identify jobs that exceeded their
limits.

## Quick Start

```bash
torc reports check-resource-utilization <workflow_id>
```

Example output:

```
⚠ Found 2 resource over-utilization violations:

Job ID | Job Name    | Resource | Specified | Peak Used | Over-Utilization
-------|-------------|----------|-----------|-----------|------------------
15     | train_model | Memory   | 8.00 GB   | 10.50 GB  | +31.3%
15     | train_model | Runtime  | 2h 0m 0s  | 2h 45m 0s | +37.5%
```

## Show All Jobs

Include jobs that stayed within limits:

```bash
torc reports check-resource-utilization <workflow_id> --all
```

## Check a Specific Run

For workflows that have been reinitialized multiple times:

```bash
torc reports check-resource-utilization <workflow_id> --run-id 2
```

## Adjusting Requirements

When jobs exceed their limits, update your workflow specification with a buffer:

```yaml
resource_requirements:
  - name: training
    memory: 12g       # 10.5 GB peak + 15% buffer
    runtime: PT3H     # 2h 45m actual + buffer
```

**Guidelines:**

- Memory: Add 10-20% above peak usage
- Runtime: Add 15-30% above actual duration
- CPU: Round up to next core count

## See Also

- [Resource Monitoring](../monitoring/resource-monitoring.md) — Enable and configure monitoring
- [Resource Requirements Reference](../reference/resources.md) — Specification format
