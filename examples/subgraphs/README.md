# Sub-graph Workflow Example

This directory contains example workflow specifications demonstrating **2 independent sub-graphs**
with **4 execution stages**. The same workflow is provided in all supported formats:

- `subgraphs_workflow.json5` - JSON5 format (with comments)
- `subgraphs_workflow.yaml` - YAML format
- `subgraphs_workflow.kdl` - KDL format

## Workflow Structure

```
                    ┌─────────────────────────────────────────┐
                    │            STAGE 1 (prep)               │
                    │         1 Slurm node (shared)           │
                    │                                         │
                    │   ┌─────────┐       ┌─────────┐         │
    input_a.txt ───>│   │ prep_a  │       │ prep_b  │<───── input_b.txt
                    │   └────┬────┘       └────┬────┘         │
                    └────────┼─────────────────┼──────────────┘
                             │                 │
                     prep_a_out.txt    prep_b_out.txt
                             │                 │
         ┌───────────────────┴──┐           ┌──┴───────────────────┐
         │                      │           │                      │
         ▼                      │           │                      ▼
┌────────────────────┐          │           │          ┌────────────────────┐
│  STAGE 2 (work_a)  │          │           │          │  STAGE 2 (work_b)  │
│   3 Slurm nodes    │          │           │          │   2 GPU nodes      │
│                    │          │           │          │                    │
│  ┌──────────────┐  │          │           │          │  ┌──────────────┐  │
│  │ work_a_1..5  │  │          │           │          │  │ work_b_1..5  │  │
│  │  (5 jobs)    │  │          │           │          │  │  (5 jobs)    │  │
│  └──────┬───────┘  │          │           │          │  └──────┬───────┘  │
└─────────┼──────────┘          │           │          └─────────┼──────────┘
          │                     │           │                    │
   work_a_*_out.txt             │           │            work_b_*_out.txt
          │                     │           │                    │
          ▼                     │           │                    ▼
┌────────────────────┐          │           │          ┌────────────────────┐
│  STAGE 3 (post_a)  │          │           │          │  STAGE 3 (post_b)  │
│   1 Slurm node     │          │           │          │   1 Slurm node     │
│                    │          │           │          │                    │
│    ┌────────┐      │          │           │          │      ┌────────┐    │
│    │ post_a │      │          │           │          │      │ post_b │    │
│    └───┬────┘      │          │           │          │      └───┬────┘    │
└────────┼───────────┘          │           │          └──────────┼─────────┘
         │                      │           │                     │
    post_a_out.txt              │           │               post_b_out.txt
         │                      │           │                     │
         └──────────────────────┼───────────┼─────────────────────┘
                                │           │
                                ▼           ▼
                    ┌─────────────────────────────────────────┐
                    │            STAGE 4 (final)              │
                    │            1 Slurm node                 │
                    │                                         │
                    │              ┌───────┐                  │
                    │              │ final │                  │
                    │              └───┬───┘                  │
                    └──────────────────┼──────────────────────┘
                                       │
                                  final_out.txt
```

## Key Features Demonstrated

### 1. Implicit File Dependencies

All job dependencies are defined through `input_files` and `output_files` rather than explicit
`depends_on`:

- `prep_a` reads `input_a.txt` and writes `prep_a_out.txt`
- `work_a_*` jobs read `prep_a_out.txt` (implicit dependency on `prep_a`)
- `post_a` reads all `work_a_*_out.txt` files (implicit dependency on all work_a jobs)

### 2. Two Independent Sub-graphs

The workflow splits into two parallel processing pipelines:

- **Sub-graph A**: `prep_a` → `work_a_1..5` → `post_a` (CPU-intensive)
- **Sub-graph B**: `prep_b` → `work_b_1..5` → `post_b` (GPU-accelerated)

These sub-graphs run completely independently until they merge at `final`.

### 3. Parameterized Jobs

Work jobs use parameters to generate multiple instances:

```yaml
name: "work_a_{i}"
parameters:
  i: "1:5"  # Creates work_a_1, work_a_2, ..., work_a_5
```

### 4. Parameterized Files

Output files also use parameters:

```yaml
name: "work_a_{i}_out"
path: "output/work_a_{i}.txt"
parameters:
  i: "1:5"  # Creates work_a_1_out, work_a_2_out, ..., work_a_5_out
```

### 5. Different Resource Requirements

Jobs have different resource profiles:

- `small`: 1 CPU, 2GB RAM (prep jobs)
- `work_large`: 8 CPUs, 32GB RAM (CPU work jobs)
- `work_gpu`: 4 CPUs, 16GB RAM, 1 GPU (GPU work jobs)
- `medium`: 2 CPUs, 8GB RAM (post jobs)
- `large`: 4 CPUs, 16GB RAM (final job)

### 6. Stage-aware Slurm Scheduling

Each stage has its own scheduler action:

- **Stage 1**: `on_workflow_start` triggers `prep_sched` (1 node for both prep jobs)
- **Stage 2**: `on_jobs_ready` triggers `work_a_sched` (3 nodes) AND `work_b_sched` (2 GPU nodes)
  simultaneously
- **Stage 3**: `on_jobs_ready` triggers separate schedulers for `post_a` and `post_b`
- **Stage 4**: `on_jobs_ready` triggers `final_sched` (1 node)

## Running the Example

### With pre-defined schedulers

View the execution plan:

```bash
torc workflows execution-plan examples/subgraphs/subgraphs_workflow.yaml
```

Output:

```
Workflow: two_subgraph_pipeline
Total Jobs: 15

▶ Stage 1: Workflow Start
  Scheduler Allocations:
    • prep_sched (slurm) - 1 allocation(s)
  Jobs Becoming Ready:
    • prep_a
    • prep_b

→ Stage 2: When jobs 'prep_a', 'prep_b' complete
  Scheduler Allocations:
    • work_a_sched (slurm) - 1 allocation(s)
    • work_b_sched (slurm) - 1 allocation(s)
  Jobs Becoming Ready:
    • work_a_{1..5}
    • work_b_{1..5}

→ Stage 3: When 10 jobs complete
  Scheduler Allocations:
    • post_a_sched (slurm) - 1 allocation(s)
    • post_b_sched (slurm) - 1 allocation(s)
  Jobs Becoming Ready:
    • post_a
    • post_b

→ Stage 4: When jobs 'post_a', 'post_b' complete
  Scheduler Allocations:
    • final_sched (slurm) - 1 allocation(s)
  Jobs Becoming Ready:
    • final

Total Stages: 4
```

### Auto-generating Slurm schedulers

The `*_no_slurm.*` files contain the same workflow without Slurm schedulers or actions. Use
`torc slurm generate` to auto-generate them:

```bash
torc slurm generate --account myproject --profile kestrel examples/subgraphs/subgraphs_workflow_no_slurm.yaml
```

This will:

1. Expand parameterized jobs and files
2. Analyze the workflow graph for dependencies
3. Group jobs by (resource_requirements, has_dependencies)
4. Generate appropriate schedulers and `on_workflow_start`/`on_jobs_ready` actions

Output shows 5 schedulers created:

- `small_scheduler` (prep jobs, `on_workflow_start`)
- `work_large_deferred_scheduler` (work_a jobs, `on_jobs_ready`)
- `work_gpu_deferred_scheduler` (work_b jobs, `on_jobs_ready`)
- `medium_deferred_scheduler` (post jobs, `on_jobs_ready`)
- `large_deferred_scheduler` (final job, `on_jobs_ready`)

## Total Resources

| Stage     | Scheduler    | Nodes | Partition | Purpose                  |
| --------- | ------------ | ----- | --------- | ------------------------ |
| 1         | prep_sched   | 1     | standard  | Run both prep jobs       |
| 2         | work_a_sched | 3     | standard  | Run 5 CPU work jobs      |
| 2         | work_b_sched | 2     | gpu       | Run 5 GPU work jobs      |
| 3         | post_a_sched | 1     | standard  | Post-process sub-graph A |
| 3         | post_b_sched | 1     | standard  | Post-process sub-graph B |
| 4         | final_sched  | 1     | standard  | Aggregate results        |
| **Total** |              | **9** |           |                          |
