# Custom Invocation Environments

By default torc will run a job's `command` as a subprocess (and not in a shell). You may want to
alter the environment before invoking the actual work command. For example, you may want to load an
environment module or activate a conda environment.

Here are the steps to run a job in a conda environment that requires an HPC environment module.

1. Define your job's `command` as a CLI command that can run in a pre-defined conda environment
   with a custom invocation script. This example assumes that `custom_env.sh` is located in the
   current directory.

```JavaScript
command: "python work.py arg1 arg2"
invocation_script: "bash custom_env.sh"
```

2. Develop the `invocation_script`. Here is a script that activates a conda environment and the
   invokes the command and arguments (`$@` is a bash variable that includes all arguments passed
   on the command line).

```bash
#!/bin/bash
module load conda
conda activate my-env
$@
```

The command that torc will run is this:

```console
$ bash custom_env.sh python work.py arg1 arg2
```
