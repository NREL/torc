.. _map-julia-function-tutorial:

#####################################
Map a Julia function to compute nodes
#####################################
This tutorial will teach you how to build a workflow from Julia functions instead of CLI
executables and run on it on an HPC with ``Slurm``.

Workflow Description
====================
Let's suppose that your code is in a module called ``simulation.jl`` and looks something like this:

.. code-block:: julia

    """
    Run one simulation on a set of input parameters. Return results in a Dict.
    """
    function run(input_params::Dict):
        job_name = input_params["job_name"]
        return Dict{String, Any}(
            "inputs" => input_params,
            "result" => 5,
            "output_data_path" => "/projects/my-project/$(job_name)",
        )
    end

    """
    Collect the results of the workers and perform postprocessing.
    Return the final result in a Dict.
    """
    function postprocess(results::Vector{<:Dict})
        total = 0
        paths = String[]
        for result in results:
            assert "result" in keys(result)
            assert "output_data_path" in keys(result)
            total += result["result"]
            push!(paths, result["output_data_path"])
        end
        return Dict{String, Any}(
            "total" => total,
            "output_data_paths" => paths,
        )
    end


You need to run this function on hundreds of sets of input parameters and want torc to help you
scale this work on an HPC.

The recommended procedure for this task is torc's Julia API as shown below.

Resource Constraints
--------------------

- Each function call needs 4 CPUs and 20 GiB of memory.
- The function call takes 1 hour to run.

On Eagle the 92 GiB nodes are easiest to acquire but would only be able to run 4 jobs at a time.
The 180 GiB nodes are fewer in number but would use fewer AUs because they would be able to run 8
jobs at a time.

Torc Overview
=============
Here is what torc does to solve this problem:

- User creates a workflow in Julia.
- User passes a runnable function as well as a list of all input parameters that need to be mapped
  to the function.
- For each set of input parameters torc creates an object in the ``user-data`` collection in the
  database, creates a job with a relationship (edge) to that object as an input, and creates a
  placeholder for data to be created by that job.
- When torc runs each job it reads the correct input parameters from the database, imports the
  user's function, and then calls it with the input parameters.
- When the function completes, torc stores any returned data in the database.
- When all workers complete torc collectgs all result data from the database into a list and passes
  that to the postprocess function. It also stores any returned data from that function into the
  database.

Build the workflow
==================
1. Modify your script as necessary to match Torc's requirements. It may be easier to create a
   wrapper script that forwards to your actual code.

   - The run and postprocess functions must match the signatures above. The function names do not
     have to match.
   - The script must call the Torc function ``process_mapped_function_cli_args`` as shown below
     where ``run`` and ``postprocess`` are your actual functions.

    .. code-block:: julia

        if abspath(PROGRAM_FILE) == @__FILE__
            process_mapped_function_cli_args(run, postprocess)
        end

   - If you don't have a postprocess function, pass ``nothing`` instead.

2. Write a script to create the workflow. Note that you need to correct the ``api`` URL and the
   Slurm ``account``. Refer to the docstring of ``map_function_to_jobs`` to see all available
   options.

.. code-block:: julia

    using Torc
    import Torc: APIClient

    api = make_api("http://localhost:8529/_db/workflows/torc-service")
    params = [
        Dict{String, Any}("input1" => 1, "input2" => 2, "input3" => 3),
        Dict{String, Any}("input1" => 4, "input2" => 5, "input3" => 6),
        Dict{String, Any}("input1" => 7, "input2" => 8, "input3" => 9),
    ]
    workflow = send_api_command(
        api,
        APIClient.add_workflow,
        APIClient.WorkflowModel(
            name = "example_mapped_function_workflow",
            description = "Example mapped function workflow",
        ),
    )

    rr = send_api_command(
        api,
        APIClient.add_resource_requirements,
        workflow._key,
        APIClient.ResourceRequirementsModel(
            name = "medium",
            num_cpus = 4,
            memory = "20g",
            runtime = "P0DT1H",
        ),
    )

    jobs = map_function_to_jobs(
        api,
        workflow._key,
        "simulation.jl",
        params;
        project_path = dirname(dirname(Base.find_package("Torc"))),
        # Set this to false if you do not have a postprocess function.
        has_postprocess = true,
    )
    scheduler = api.add_slurm_scheduler(
        workflow.key,
        SlurmSchedulerModel(
            name="short",
            account="my_account",
            mem="180224",
            walltime="04:00:00",
        ),
    )
    # This is optional, but can be useful to look at actual resource utilization.
    config = send_api_command(api, APIClient.get_workflow_config, workflow._key)
    config.compute_node_resource_stats = APIClient.ComputeNodeResourceStatsModel(
        cpu = true,
        memory = true,
        process = true,
        interval = 5,
        monitor_type="periodic",
        make_plots = true,
    )
    send_api_command(api, APIClient.modify_workflow_config, workflow._key, config)

    println("Created workflow with key $(workflow._key) $(length(jobs)) jobs.")


**Requirements**:

- Your run function should raise an exception if there is a failure. If that happens, torc will
  record a non-zero return code for the job.
- If you want torc to store result data in the database, return it from your run function.
  **Note**: this result data must not be large - the database is not designed for that. If you have
  large result data, return a pointer (i.e., file path) to its location here.
- If you choose to define a postprocess function and want torc to store the final data in the
  database, return it from that function.
- The ``params`` must be serializable in JSON format because they will be stored in the database.
  Basic types like numbers and strings and lists and dictionaries of those will work fine. If you
  need to store complex, custom types, consider these options:

  - Use the `Serialization` library in Julia's standard library to serialize your data and store
    the result as a string. Your run function would need to understand how to de-serialize it.
    Note that this has portability limitations. (Please contact the developers if you would like
    to see this happen automatically.)

2. Create the workflow.

.. code-block:: console

    $ julia --project=<path-to-env-that-includes-torc> <your-script>
    Created workflow 3141686 with 3 jobs.

3. Optional: Save the workflow key in the environment to save typing.

.. code-block:: console

    $ export TORC_WORKFLOW_KEY=3141686

4. Optional: save the workflow specification. This illustrates how torc orchestrates this workflow
   by creating relationships between jobs and the ``user_data`` collection. You may also want to
   edit the input parameters for future runs.

.. code-block:: console

    $ torc workflows show

5. Initialize the workflow.

.. code-block:: console

    $ torc workflows start
    2023-08-07 11:51:03,891 - INFO [torc.workflow_manager workflow_manager.py:156] : Changed all uninitialized jobs to ready or blocked.
    2023-08-05 11:51:03,894 - INFO [torc.workflow_manager workflow_manager.py:82] : Started workflow

6. Schedule compute nodes with ``Slurm``. This example only needs one compute node. You will need
   to make some estimation for your jobs.

   The computes nodes in this example can run eight jobs at a time and can complete four rounds of
   work (32 jobs per allocation). So, the number of required compute nodes is ``num_jobs / 32``.

.. code-block:: console

    $ torc hpc slurm schedule-nodes -n1

7. The jobs will run whenever Slurm allocates compute nodes. Monitor status as discussed in
   :ref:`check-status`.

8. View the result data overall or by job (if your run and postprocess functions return something).
   Note that listing all user-data will return input parameters.

.. code-block:: console

    $ torc list user-data

.. code-block:: console

    $ torc jobs list-user-data --stores 788309
    $ torc jobs list-user-data --stores 788323
    $ torc jobs list-user-data --stores 788337
    $ torc jobs list-user-data --stores 788389

Other jobs
==========
You could add "normal" jobs to the workflow as well. For example, you might have preprocessing and
postprocessing work to do. You can add those jobs through the API. You could also add multiple
rounds of mapped functions. ``map_function_to_jobs`` provides a ``blocked_by`` parameter to specify
ordering. You could also define job-job relationships through files or user-data as discussed
elsewhere in this documentation.
