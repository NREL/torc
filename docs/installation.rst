############
Installation
############

1. Install a database with ArangoDB. Refer to the links below for a local computer vs Eagle.
2. Install the pre-built Python client into a Python 3.10 conda environment.
3. Install the Python package ``torc`` in the ``worker`` directory into that environment.

.. todo:: Figure out where to store the python client.

.. code-block:: console

   $ conda activate torc
   $ pip install -e python_client
   $ pip install -e worker

Refer to :ref:`generate_client_apis` to generate a new API after changing the API endpoint.

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   db_installation_local
   db_installation_eagle
   generate_client_apis
