using Torc
import Torc: APIClient

const TORC_SERVICE_URL = "http://localhost:8529/_db/test-workflows/torc-service"

function create_workflow(api)
    return send_api_command(
        api,
        APIClient.add_workflow,
        APIClient.WorkflowModel(
            name="manual_job_dependencies",
            description="Demo creation of a workflow with job dependencies specified manually.",
        ),
    )
end

function build_workflow(api, workflow)
    small = send_api_command(
        api,
        APIClient.add_resource_requirements,
        workflow._key,
        APIClient.ResourceRequirementsModel(
            name="small",
            num_cpus=1,
            memory="1g",
            runtime="P0DT1H",
        ),
    )
    medium = send_api_command(
        api,
        APIClient.add_resource_requirements,
        workflow._key,
        APIClient.ResourceRequirementsModel(
            name="small", num_cpus=1, memory="1g", runtime="P0DT45M"
        )
    )
    send_api_command(
        api,
        APIClient.add_slurm_schedulers,
        workflow._key,
        APIClient.SlurmSchedulerModel(
            name="short",
            account="my_account",
            nodes=1,
            walltime="04:00:00",
        ),
    )

    blocking_jobs = []
    for i in 1:3
        job = send_api_command(
            api,
            APIClient.add_job,
            workflow._key,
            APIClient.JobModel(
                name="job$(i)",
                command="echo hello",
                resource_requirements=medium._id,
               )
            )
        push!(blocking_jobs, job._id)
    end

    send_api_command(
        api,
        APIClient.add_job,
        workflow._key,
        job=APIClient.JobModel(
            name="postprocess",
            command="echo hello",
            resource_requirements=small._id,
            blocked_by = blocking_jobs,
       ))

    @info "Created workflow $(workflow._key)"
    return
end

function main()
    api = make_api(TORC_SERVICE_URL)
    workflow = create_workflow(api)
    try
        build_workflow(api, workflow)
    catch e
        APIClient.remove_workflow(api, workflow._key)
        rethrow()
    end
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
