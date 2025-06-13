(tutorials)=

# Tutorials

This section provides working examples that you can follow to learn how to use torc. The examples
are stored in the torc repository at https://github.com/NREL/torc/tree/main/examples. You can either
copy them or clone the repository as described below.

1. Clone the torc repository.

```console
$ git clone https://github.com/NREL/torc.git
```

2. Change to the `torc` directory so that you have access to the torc test scripts.

```console
$ cd torc/torc_client
```

3. Create a torc runtime configuration file. We will use it shorten the commands that we type
   below. Change `<hostname>` and `<database-name>` to correct values for your database
   (without the `<>`).

```console
$ torc config create -u http://<hostname>:8529/_db/<database-name>/torc-service
Wrote torc config to /Users/dthom/.torc_settings.toml
```

```{toctree}
:maxdepth: 4

diamond_workflow
slurm_diamond_workflow
node_packing_workflow
manual_job_dependencies
cpu_affinity_workflow
map_python_function
map_julia_function
large_workflow
```
