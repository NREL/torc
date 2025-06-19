(installation)=

# Installation
This page describes how to install `torc-client` and its dependencies. `torc-client` is a
Python package that provides a command-line interface (CLI), a terminal user interface (TUI), and
a Python library for interacting with the Torc API server. It also provides a Torc worker that can
run jobs on local or HPC compute nodes.

1. Create a Python 3.11+ virtual environment. This example uses the `venv` module in the standard
   library to create a virtual environment in your home directory.

   You may prefer `conda` or `mamba`.

   If you are running on NREL's HPC, you may need to `module load python` first.

   ```console
   $ python -m venv ~/python-envs/torc
   ```

2. Activate the virtual environment.

   ```console
   $ source ~/python-envs/torc/bin/activate
   ```

   Whenever you are done using torc, you can deactivate the environment by running `deactivate`.

3. Install the Python package `torc`.

   ```console
   $ pip install torc-client
   ```

4) Optionally install the Julia client package.

   ```console
   $ julia  # optionally specify an environment with --project
   $ using Pkg
   $ Pkg.add(PackageSpec(url="git@github.com:NREL/torc.git", rev="v0.6.4", subdir="julia/Torc"))
   ```

5. Optionally install `jq` from <https://stedolan.github.io/jq/download/> for parsing JSON.
   This tool is very useful when sending API requests with `curl` or dumping torc output to
   JSON.
