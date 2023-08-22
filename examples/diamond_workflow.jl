using Torc
import Torc: APIClient

const PREPROCESS = joinpath("tests", "scripts", "preprocess.py")
const POSTPROCESS = joinpath("tests", "scripts", "postprocess.py")
const WORK = joinpath("tests", "scripts", "work.py")

function main()
    url = "http://localhost:8529/_db/test-workflows/torc-service"
    api = make_api(url)
    output_dir = mktempdir()
    inputs_file = joinpath(output_dir, "inputs.json")
    open(inputs_file, "w") do io
        write(io, "{\"val\": 5}")
    end

    builder = WorkflowBuilder()
    inputs = add_file!(builder, name="inputs", path=inputs_file)
    f1 = add_file!(builder, name="file1", path=joinpath(output_dir, "f1.json"))
    f2 = add_file!(builder, name="file2", path=joinpath(output_dir, "f2.json"))
    f3 = add_file!(builder, name="file3", path=joinpath(output_dir, "f3.json"))
    f4 = add_file!(builder, name="file4", path=joinpath(output_dir, "f4.json"))

    small = add_resource_requirements!(builder,
        name="small", num_cpus=1, memory="1g", runtime="P0DT1H"
    )
    medium = add_resource_requirements!(builder,
        name="medium", num_cpus=4, memory="8g", runtime="P0DT8H"
    )
    large = add_resource_requirements!(builder,
        name="large", num_cpus=8, memory="16g", runtime="P0DT12H"
    )

    add_slurm_scheduler!(
        builder,
        name="debug",
        account="my_account",
        nodes=1,
        partition="debug",
        walltime="01:00:00",
    )
    add_job!(
        builder,
        name="preprocess",
        command="python $PREPROCESS -i $(inputs.path) -o $(f1.path)",
        input_files=[inputs.name],
        output_files=[f1.name],
        resource_requirements=small.name,
        scheduler="slurm_schedulers/debug",
    )
    add_job!(
        builder,
        name="work1",
        command="python $WORK -i $(f1.path) -o $(f2.path)",
        input_files=[f1.name],
        output_files=[f2.name],
        resource_requirements=medium.name,
        scheduler="slurm_schedulers/debug",
    )
    add_job!(
        builder,
        name="work2",
        command="python $WORK -i $(f1.path) -o $(f3.path)",
        input_files=[f1.name],
        output_files=[f3.name],
        resource_requirements=large.name,
        scheduler="slurm_schedulers/debug",
    )
    add_job!(
        builder,
        name="postprocess",
        command="python $POSTPROCESS -i $(f2.path) -i $(f3.path) -o $(f4.path)",
        input_files=[f2.name, f3.name],
        output_files=[f4.name],
        resource_requirements=small.name,
        scheduler="slurm_schedulers/debug",
    )
    configure_resource_monitoring!(
        builder,
        cpu=true,
        memory=true,
        process=true,
        interval=5,
        monitor_type="aggregation",
    )

    spec = build!(
        builder,
        user = "user",
        name = "diamond_workflow",
        description = "Example diamond workflow",
    )
    workflow, response = APIClient.post_workflow_specifications(api, spec)
    if response.status != 200
        error("Failed to create workflow: $(response)")
    end

    @info "Created workflow" workflow
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
