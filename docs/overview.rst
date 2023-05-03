.. _overview:

#################
Workflow Overview
#################

This page illustrates the objectives of torc with an example workflow.

The workflow has four jobs:

- ``preprocess``: Reads an input file and produces two output files.
- ``work1``: Performs work on one output file from stage 1.
- ``work2``: Performs work on one output file from stage 1.
- ``postprocess``: Reads the output files from the work stage and produces final results.

Dependencies
============
The work scripts can only be run after the preprocess stage and can be run in parallel. The
postprocess stage can only be run when the work scripts are done.

These dependencies can be defined indirectly through job-file relationships or directly by the
user.

.. raw:: html

   <hr>

Job-File Relationships
----------------------
.. graphviz::

   digraph job_file_graph {
      "preprocess" -> "inputs.json" [label="needs"];
      "preprocess" -> "f1.json" [label="produces"];
      "work1" -> "f1.json" [label="needs"];
      "work2" -> "f1.json" [label="needs"];
      "work1" -> "f2.json" [label="produces"];
      "work2" -> "f3.json" [label="produces"];
      "postprocess" -> "f2.json" [label="needs"];
      "postprocess" -> "f3.json" [label="needs"];
      "postprocess" -> "f4.json" [label="produces"];
   }

.. raw:: html

   <hr>

Job-Job Relationships
---------------------
.. graphviz::

   digraph job_job_graph {
      "preprocess" -> "work1" [label="blocks"];
      "preprocess" -> "work2" [label="blocks"];
      "work1" -> "postprocess" [label="blocks"];
      "work2" -> "postprocess" [label="blocks"];
   }

.. raw:: html

   <hr>


Resource Requirements
=====================
The work scripts require much more compute and time than the other stages.

.. graphviz::

   digraph job_job_graph {
      "preprocess" -> "small (1 CPU, 10 minutes)" [label="requires"];
      "work1" -> "large (18 CPUs, 24 hours)" [label="requires"];
      "work2" -> "large (18 CPUs, 24 hours)" [label="requires"];
      "postprocess" -> "medium (4 CPUs, 1 hour)" [label="requires"];
   }

.. raw:: html

   <hr>


Compute Node Efficiency
=======================
Run jobs in parallel on a single compute node if the requirements allow for it.

.. raw:: html

   <hr>

Intelligent Restarts
====================
The orchestrator can rerun jobs as needed.

- If the user finds a bug in the inputs file, all jobs must be rerun.
  rerun.
- If ``work2`` used more memory than expected and failed, only ``work1`` and ``postprocess``
  need to be rerun.
- If ``postprocess`` took more time than expected and timed out, only it needs to be rerun.

.. raw:: html

   <hr>

Resource Utilization Metrics
============================
Compute nodes record actual CPU/GPU/memory utilization statistics.

.. raw:: html

   <hr>

User-Defined Data
=================
Jobs can store user-defined input or output data.

.. graphviz::

   digraph user_data_graph {
      "postprocess" -> "{key1: 'value1', key1: 'value2'}" [label="stores"];
   }

.. raw:: html

   <hr>

User-Defined Events
===================
Jobs can post events with structured data to aid analysis and debug.

.. graphviz::

   digraph event_graph {
      "work1" -> "{timestamp: '2/1/2023 12:00:00', error: 'Something bad happened'}";
   }

Or store result data.

.. graphviz::

   digraph event_graph {
      "work2" -> "{timestamp: '2/1/2023 12:00:00', result: 2.158}";
   }
