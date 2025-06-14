(archive-workflow)=

# Archive a Workflow

When you are done with a workflow you may want to keep the results in the database but stop
seeing it show up in the `torc workflows list` command. You can `archive` the workflow.

```console
$ torc workflows modify --archive=true 123456
```

That workflow will no longer show up in workflow lists. You will also not be able to run it.

If you would like to view the archived workflows, run this command:

```console
$ torc workflows list --only-archived
```

If you would like to enable the workflow, run this command:

```console
$ torc workflows modify --archive=false 123456
```
