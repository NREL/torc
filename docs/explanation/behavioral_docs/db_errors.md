# Database Errors

Torc attempts to provide resiliency against some database errors. The workflow config defines
the parameter `compute_node_wait_for_healthy_database_minutes` with a default value of `20`.

## Database access on compute node acquisition

If the first API command issued by the torc worker application running on a compute node fails, it
will wait that number of minutes, polling once a minute. If the database becomes responsive, it
will continue as normal. If the database is still unavailable, it will exit (and release the
allocation if torc scheduled it).

## Database access while running jobs

Similarly, if an API command issued by the torc worker application fails while it is in its run
loop, it will wait that number of minutes. If the database is still unavailable it will terminate
all jobs and exit.

All other API commands issued by the torc worker application are not protected and will cause it to
exit.

## Customization

You can change the value of `compute_node_wait_for_healthy_database_minutes` in the `config`
section of a workflow specification file (JSON), through the Python and Julia `WorkflowBuilder`
scripts, or through the torc CLI command `torc workflows set-compute-node-parameters`.

% TODO: make how to page for managing all compute node params
