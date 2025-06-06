# Torc workflow management software

This software package orchestrates execution of a workflow of jobs on distributed computing
resources. It is optimized for use on HPCs with Slurm, but also can be used in the cloud and
on local computers.

Please refer to the documentation at https://github.com/NREL/pages/torc/

## Project Status
The software is well-tested and has been used in several projects at NREL. However, it is not
currently sponsored for active development. Unless user adoption changes significantly, we will
likely only make incremental feature updates, depending on project needs.

### Maintenance
We will attempt to fix any bugs reported as well as address updates to software dependencies.

### Future Development
Contributions to the development of Torc are welcome.

The main new feature of interest to current users is the removal of the need to run an external
database (ArangoDB). While that mode of operation has many benefits and will continue to be the
default, some users want to be able to run local workflows without having to manage a database
and a Docker/Podman container. The current Python and Julia application code would be unchanged
if the database and Torc API service running within it were replaced by a new server process.

We would like to see this happen and will look for opportunities to implement it.

Please post new ideas for Torc in the [discussions](https://github.com/NREL/torc/discussions).

## Why develop another workflow management tool?
Since there are so many open source workflow management tools available, some may ask, "why develop
another?" We evaluated many of them, including [Nextflow](https://www.nextflow.io/),
[Snakemake](https://snakemake.github.io/), and [Pegasus](https://pegasus.isi.edu/). Those are
excellent tools and we took inspiration from them. However, they did not fully meet our needs and it
wasn't difficult to create exactly what we wanted.

Here are the features of Torc that we think differentiate it from other tools:

- Node packing on HPC compute nodes

  A Torc worker can maintain a maximum queue depth of jobs on a compute node until the allocation
  runs out of time. Users can start workers on any number single-node or multi-node allocations.

- Torc API Server

  Torc provides a server that implements an API conforming to an [OpenAPI
  specification](https://swagger.io/specification/), providing automatic client library generation.
  We use both Python and Julia clients to build and manage workflows. Users can monitor workflows
  through Torc-provided CLI and TUI applications or develop their own scripts.

- Debugging errors

  We run large numbers of simulations on untested input data. Many of them fail. Torc provides
  automatic resource monitoring, log colletion, and detailed error reporting through raw text,
  tables, and formatted JSON. Torc makes it easy for users to rerun failed jobs after applying
  fixes.

- Traceability

  All workflows and results are stored in a database, tracked by user and other metadata.

## License
Torc is released under a BSD 3-Clause [license](https://github.com/NREL/torc/blob/main/LICENSE).

## Software Record
This package is developed under NREL Software Record SWR-24-127.
