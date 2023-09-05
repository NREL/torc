.. _managing-workflow:

##################
Managing Workflows
##################
This section provides step-by-step instructions for specific tasks.

The ``torc`` CLI toolkit provides the simplest mechanism to build and manage workflows. It
provides most functionality and this section describes it.

Torc provides a terminal-based management console (run ``torc tui``). Use it view the workflow
configurations and check status.

If you need or want more control, you
are welcome to use the API through OpenAPI-generated libaries or API tools like ``curl``, `Postman
<https://www.postman.com/>`_, and `Insomnia <https://insomnia.rest/>`_. You can also use Arango
tools to manage data directly in the database.

.. toctree::
   :maxdepth: 3

   configure_workflow
   run_workflow
   check_status
   cancel
   restart
   automated_scheduling
   gracefully_shutdown_jobs
   debugging
   passing_data_between_jobs
   plot_graphs
   backups
