.. torc documentation master file, created by
   sphinx-quickstart on Sat Feb 11 11:41:31 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Torc User Guide
===============
The torc workflow management system orchestrates execution of user jobs on distributed computing
resources, including HPC and cloud environments.

Torc provides these features:

- Manage dependencies between jobs and resources.
- Auto-tune resource requirements.
- Track resource utilization.
- Support workflow restarts, accounting for job failures, compute node timeouts, and program and
  data file files.
- Persistent store for user input and output data.


Refer to :ref:`overview` for an illustration of its capabilities.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   overview
   getting_started
   usage
   architecture
   reference


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
