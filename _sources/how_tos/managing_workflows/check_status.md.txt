(check-status)=

# Check workflow status

## TUI

The torc terminal-based management console provides views of job status and results.

```console
$ torc tui
```

## Monitor events

The torc worker app posts events to the database whenever compute nodes start and stop and jobs
start and complete. Monitor these events dynamically with this command:

```console
$ torc events monitor
```

## Job status

Monitor progress with torc or squeue.

```console
$ watch -n 10 squeue -u $USER
```

```console
$ torc jobs list
```

After a job completes its status will be be `done`. You can filter the jobs to see how many
are ready, in progress, and done

```console
$ torc jobs list -f status=ready
```

```console
$ torc jobs list -f status=submitted
```

```console
$ torc jobs list -f status=done
```

## Return codes

This commmand will show the job results. A `return_code` of 0 is successful. Non-zero is a
failure.

```console
$ torc results list
```

You can filter the output to see only passes or only failures.

```console
$ torc results list -f return_code=0
```

```console
$ torc results list -f return_code=1
```
