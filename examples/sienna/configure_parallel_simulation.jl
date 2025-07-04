using PowerSimulations

using Torc
import Torc: APIClient

const TORC_SERVICE_URL = "http://dsgrid-registry.hpc.nrel.gov:8529/_db/workflows/torc-service"

function configure_parallel_simulation(
    script::AbstractString,
    num_steps::Integer,
    num_period_steps::Integer,
    output_dir::AbstractString;
    num_overlap_steps::Integer=0,
    project_path=nothing,
    simulation_name="simulation",
)
    api = make_api(TORC_SERVICE_URL)
    workflow = create_workflow(api)
    try
        build_workflow(
            api,
            workflow,
            script,
            num_steps,
            num_period_steps,
            output_dir,
            num_overlap_steps = num_overlap_steps,
            project_path = project_path,
            simulation_name = simulation_name,
        )
    catch e
        APIClient.remove_workflow(api, workflow._key)
        rethrow()
    end
end

function create_workflow(api)
    return send_api_command(
        api,
        APIClient.add_workflow,
        APIClient.WorkflowModel(
            user = get_user(),
            name="partitioned_simulation",
            description="Run a partitioned simulation.",
        ),
    )
end

function build_workflow(
    api,
    workflow::APIClient.WorkflowModel,
    script::AbstractString,
    num_steps::Integer,
    num_period_steps::Integer,
    output_dir::AbstractString;
    num_overlap_steps::Integer=0,
    project_path=nothing,
    simulation_name="simulation",
)
    mkpath(output_dir)
    partitions = SimulationPartitions(num_steps, num_period_steps, num_overlap_steps)
    julia_cmd = isnothing(project_path) ? "julia" : "julia --project=$project_path"
    setup_command = "$julia_cmd $script setup --simulation-name=$simulation_name " *
    "--num-steps=$num_steps --num-period-steps=$num_period_steps " *
    "--num-overlap-steps=$num_overlap_steps --output-dir=$output_dir"
    teardown_command = "$julia_cmd $script join --simulation-name=$simulation_name --output-dir=$output_dir"

    small = send_api_command(
        api,
        APIClient.add_resource_requirements,
        workflow._key,
        APIClient.ResourceRequirementsModel(
            name="small",
            num_cpus=1,
            memory="10g",
            runtime="P0DT30M",
        ),
    )
    medium = send_api_command(
        api,
        APIClient.add_resource_requirements,
        workflow._key,
        APIClient.ResourceRequirementsModel(
            name="medium",
            num_cpus=1,
            memory="40g",
            runtime="P0DT2H",
        ),
    )
    send_api_command(
        api,
        APIClient.add_slurm_scheduler,
        workflow._key,
        APIClient.SlurmSchedulerModel(
            name="debug",
            account="my_account",
            nodes=1,
            walltime="01:00:00",
            partition="debug",
        ),
    )
    short = send_api_command(
        api,
        APIClient.add_slurm_scheduler,
        workflow._key,
        APIClient.SlurmSchedulerModel(
            name="short",
            account="my_account",
            nodes=1,
            walltime="04:00:00",
        ),
    )

    setup = send_api_command(
        api,
        APIClient.add_job,
        workflow._key,
        APIClient.JobModel(
            name="setup",
            command=setup_command,
            resource_requirements=small._id,
            invocation_script="bash julia_env.sh",
       ))

    work_jobs = String[]
    for i in 1:get_num_partitions(partitions)
        cmd = "$julia_cmd $script execute --simulation-name=$simulation_name --index=$i --output-dir=$output_dir"
        job = APIClient.JobModel(
            name="execute-$i",
            command=cmd,
            resource_requirements=medium._id,
            blocked_by=[setup._id],
            invocation_script="bash julia_env.sh",
       )
        if i == 1
            # Only one job needs to ask for scheduling.
            job.schedule_compute_nodes=APIClient.ComputeNodeScheduleParams(
                num_jobs=20,
                scheduler_id=short._id,
            )
        end
        job = send_api_command(api, APIClient.add_job, workflow._key, job)
            push!(work_jobs, job._id)
    end

    send_api_command(
        api,
        APIClient.add_job,
        workflow._key,
        APIClient.JobModel(
            name="teardown",
            command=teardown_command,
            resource_requirements=small._id,
            blocked_by=work_jobs,
            invocation_script="bash julia_env.sh",
       ),
    )

    println("Created Torc workflow key = $(workflow._key)")
end
