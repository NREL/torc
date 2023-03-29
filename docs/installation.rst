############
Installation
############

1. If running on NREL's HPC, contact Daniel Thom to procure a database. We are currently
   beta-testing and so only a limited number are available. You will be able to reach the database
   from any login or compute node. You can also install a database on a compute node, but obviously,
   it will only survive one compute node allocation. That can be sufficient for testing purposes.

2. If running on a local computer or cloud environment, install a database with ArangoDB. Refer to
   the links below.

3. Clone the ``torc`` repository to computer where you will submit and run jobs.

.. code-block:: console

   $ git clone https://github.nrel.gov/viz/wms.git

4. Create a Python 3.10 virtual environment (e.g., conda).

.. code-block:: console

   $ conda create -n torc python=3.10
   $ conda activate torc

5. Install the Python package ``torc`` into that environment. It is in the ``torc`` directory of
   this repository.

.. code-block:: console

   $ pip install -e wms/torc

6. Install the pre-built Python client into the virutal environment. Location is TBD.

.. todo:: Figure out where to store the python client where users can access it.

.. code-block:: console

   $ pip install -e python_client

Refer to :ref:`generate_client_apis` to generate a new API after changing the API endpoint.

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   db_installation_local
   db_installation_eagle
   generate_client_apis
