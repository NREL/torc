# Cancel a workflow

This CLI command will cancel a workflow as well as all active jobs. It may take 1-2 minutes for
compute nodes to kill their jobs and exit.

```console
$ torc workflows cancel <workflow_key>
```
