using Torc
import Torc: APIClient

const TORC_SERVICE_URL = "http://localhost:8529/_db/test-workflows/torc-service"
const PREPROCESS = joinpath("tests", "scripts", "preprocess.py")
const POSTPROCESS = joinpath("tests", "scripts", "postprocess.py")
const WORK = joinpath("tests", "scripts", "work.py")

function create_workflow(api)
    return send_api_command(
        api,
        APIClient.add_workflow,
        APIClient.WorkflowModel(
            user = "user",
            name = "diamond_workflow",
            description = "Example diamond workflow",
        ),
    )
end

function build_workflow(api, workflow)
    output_dir = mktempdir()
    inputs_file = joinpath(output_dir, "inputs.json")
    open(inputs_file, "w") do io
        write(io, "{\"val\": 5}")
    end

    config = send_api_command(api, APIClient.get_workflow_config, workflow._key)
    config.compute_node_resource_stats = APIClient.ComputeNodeResourceStatsModel(
        cpu=true,
        memory=true,
        process=true,
        interval=5,
        monitor_type="aggregation",
    )
    send_api_command(api, APIClient.modify_workflow_config, workflow._key, config)

    inputs = send_api_command(
        api,
        APIClient.add_file,
        workflow._key,
        APIClient.FileModel(name="inputs", path=inputs_file),
    )
    f1 = send_api_command(
        api,
        APIClient.add_file,
        workflow._key,
        APIClient.FileModel(name="files1", path=joinpath(output_dir, "f1.json")),
    )
    f2 = send_api_command(
        api,
        APIClient.add_file,
        workflow._key,
        APIClient.FileModel(name="files2", path=joinpath(output_dir, "f2.json")),
    )
    f3 = send_api_command(
        api,
        APIClient.add_file,
        workflow._key,
        APIClient.FileModel(name="files3", path=joinpath(output_dir, "f3.json")),
    )
    f4 = send_api_command(
        api,
        APIClient.add_file,
        workflow._key,
        APIClient.FileModel(name="files4", path=joinpath(output_dir, "f4.json")),
    )

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
            name="medium",
            num_cpus=4,
            memory="8g",
            runtime="P0DT8H",
        )
    )
    large = send_api_command(
        api,
        APIClient.add_resource_requirements,
        workflow._key,
        APIClient.ResourceRequirementsModel(
            name="large",
            num_cpus=8,
            memory="16g",
            runtime="P0DT12H",
        ),
    )

    send_api_command(
        api,
        APIClient.add_slurm_schedulers,
        workflow._key,
        APIClient.SlurmSchedulerModel(
            name="debug",
            account="my_account",
            nodes=1,
            partition="debug",
            walltime="01:00:00",
        ),
    )

    jobs = [
        APIClient.JobModel(
            name="preprocess",
            command="python $PREPROCESS -i $(inputs.path) -o $(f1.path)",
            input_files=[inputs._id],
            output_files=[f1._id],
            resource_requirements=small._id,
        ),
        APIClient.JobModel(
            name="work1",
            command="python $WORK -i $(f1.path) -o $(f2.path)",
            input_files=[f1._id],
            output_files=[f2._id],
            resource_requirements=medium._id,
        ),
        APIClient.JobModel(
            name="work2",
            command="python $WORK -i $(f1.path) -o $(f3.path)",
            input_files=[f1._id],
            output_files=[f3._id],
            resource_requirements=large._id,
        ),
        APIClient.JobModel(
            name="postprocess",
            command="python $POSTPROCESS -i $(f2.path) -i $(f3.path) -o $(f4.path)",
            input_files=[f2._id, f3._id],
            output_files=[f4._id],
            resource_requirements=small._id,
            ),
        ),
    ]
    add_jobs(api, workflow._key, jobs)

    @info "Created workflow" workflow
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
