################
CLI Fundamentals
################
The CLI toolkit contains some nuances that users should understand in order to have a good
experience.

General Usage
=============
The torc CLI commands are hierarchical with help at every level. For example:

.. code-block:: console

   $ torc
   $ torc --help

   $ torc workflows
   $ torc workflows --help

   $ torc hpc slurm --help

Shell Completion
================
The torc CLI uses the Python package `Click <https://click.palletsprojects.com/en/8.1.x>`_ to
process CLI options and arguments. Click supports shell completion for commands and subcommands for
Bash, Zsh, and Fish. We highly recommend that you configure your shell for this.

To demonstrate the value let's suppose that you want to see the commands available. Type ``torc``,
a space, and then ``tab``. This is the result:

.. code-block:: console

    $ torc collections
    collections            -- Collections commands
    compute-nodes          -- Compute node commands
    config                 -- Config commands
    events                 -- Event commands
    export                 -- Export commands
    files                  -- File commands
    graphs                 -- Graph commands
    hpc                    -- HPC commands
    jobs                   -- Job commands
    local                  -- Local compute node commands
    resource-requirements  -- Job resource requirements commands
    results                -- Result commands
    stats                  -- Stats commands
    user-data              -- User data commands
    workflows              -- Workflow commands

Press ``tab`` to cycle through the options. The same principle works for subcommands (e.g., ``torc
jobs <tab>``).

After running the steps below restart your shell in order for the changes to take effect.

Bash Instructions
-----------------

.. code-block:: console

    $ _TORC_COMPLETE=bash_source torc > ~/.torc-complete.bash

Add this line to your ``~/.bashrc`` file::

   . ~/.torc-complete.bash

Zsh Instructions
----------------

.. code-block:: console

    $ _TORC_COMPLETE=zsh_source torc > ~/.torc-complete.zsh

Add this line to your ``~/.zshrc`` file::

   . ~/.torc-complete.zsh

Fish Instructions
-----------------

.. code-block:: console

   $ _TORC_COMPLETE=fish_source torc > ~/.config/fish/completions/torc.fish

Database Connection
===================

All of the commands described here require connecting to the database. We recommend that you use
a torc-provided shortcut to avoid having to type it in every command.

Torc RC file
------------
Torc allows you to store common configuration settings in a config file in your home directory.
Here's how to create it with a database on the local computer. Change the hostname (``localhost``)
and database name (``workflows``) as needed.

.. code-block:: console

   $ torc config create -u http://localhost:8529/_db/workflows/torc-service
   Wrote torc config to /Users/dthom/.torc.json5

Environment variable
--------------------
You can also set this environment variable.

.. code-block:: console

   $ export TORC_DATABASE_URL=http://localhost:8529/_db/workflows/torc-service

The final option is to pass the URL to every command.

.. code-block:: console

   $ torc -u http://localhost:8529/_db/workflows/torc-service workflows list

.. _workflow_key_shortcuts:

Workflow Key Shortcuts
======================
Most commands are tied to one workflow in the database, and so the workflow identifier is critical.
There are four ways to set it:

1. Set it in every command with the ``-k`` or ``--workflow-key`` options.

.. code-block:: console

   $ torc -k 247827 jobs list

2. Set the ``workflow_key`` field in ``~/.torc.json5``. Note that the ``torc workflows create*``
   commands support the option ``-U`` that automatically updates the config file with the
   newly-created key.

3. Set an environment variable to apply it globally in one environment.

.. code-block:: console

   $ export TORC_WORKFLOW_KEY=247827

.. code-block:: console

   $ torc jobs list

4. Let the tool prompt you to pick.

.. code-block:: console

   $ torc jobs list
   This command requires a workflow key and one was not provided. Please choose one from below.

   +-----------------------------------------------------------+
   |                             workflow                      |
   +-------+--------------+-------+-----------------+----------+
   | index |  name        |  user | description     |   key    |
   +-------+--------------+-------+-----------------+----------+
   |   1   | workflow1    | user1 | My workflow 1   | 92181686 |
   |   2   | workflow2    | user2 | My workflow 2   | 92181834 |
   +-------+--------------+-------+-----------------+----------+
   workflow key is required. Select an index from above: >>> 2

Output Format
=============
Many commands support output options of raw text as well as JSON. The JSON option is useful for
scripting purposes. The following example will create a new workflow, detect the key, and then
start it. (This requires that you install ``jq``, discussed on the :ref:`installation` page.)

.. code-block:: console

   $ key=$(torc -F json workflows create-from-json-file my-workflow.json5 | jq -r '.key')

.. code-block:: console

   $ torc -k $key workflows start

All of the torc list commands support raw-text tables as well as JSON arrays. You should always
be able to pipe the stdout of a command to ``jq`` for pretty-printing or further processing.

.. code-block:: console

   $ torc -F json -k 94954625 jobs list | jq .
