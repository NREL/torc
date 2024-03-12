.. _installation:

############
Installation
############

1. If running on NREL's HPC, contact Daniel Thom to procure a database for a trial period.
   Long-term options are available by requesting a virtual machine from the HPC Operations team.
   We can help you setup and manage the database. Other options are also under consideration.

.. note:: The test database does not enable authentication for the torc service API. The database
   itself enables authentication but all torc CLI and API commands are not authenticated. This can
   be customized for other databases.

2. If running on a local computer or cloud environment, install a database with ArangoDB. Refer to
   the links below.

3. Create a Python 3.10+ virtual environment (e.g., conda). If you are not familiar with Python
   virtual environments, install ``Miniconda`` (not ``Anaconda`` because it has unnecessary
   packages) by following instructions at
   https://conda.io/projects/conda/en/stable/user-guide/install/

.. code-block:: console

   $ conda create -y -n torc python=3.11
   $ conda activate torc

4. Install the Python package ``torc``.

.. code-block:: console

    $ pip install git+ssh://git@github.nrel.gov/viz/torc.git@v0.3.3#subdirectory=torc_package

5. Optionally install the Julia client package.

.. code-block:: console

    $ julia  # optionally specify an environment with --project
    $ using Pkg
    $ Pkg.add(PackageSpec(url="git@github.nrel.gov:viz/torc.git", rev="v0.3.3", subdir="julia/Torc"))

Note that you can also install the ``torc`` package from a clone of the repository. This will give
you the latest code from the ``main`` branch.

.. code-block:: console

   $ git clone https://github.nrel.gov/viz/torc.git
   $ pip install -e torc/torc_package

6. Optionally install ``jq`` from https://stedolan.github.io/jq/download/ for parsing JSON.
   This tool is very useful when sending API requests with ``curl`` or dumping torc output to
   JSON.

Refer to :ref:`building-torc` for developer instructions on how to build the torc packages.
