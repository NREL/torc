const BASE_DIR = dirname(dirname(Base.find_package("Torc")))
const SLEEP = joinpath(BASE_DIR, "..", "..", "torc_package", "tests", "scripts", "sleep.py")

@testset "Test workflow builder" begin
    url = "http://localhost:8529/_db/test-workflows/torc-service"
    api = make_api(url)

    builder = WorkflowBuilder()

    small = add_resource_requirements!(builder;
        name = "small", num_cpus = 1, memory = "1g", runtime = "P0DT1H",
    )
    medium = add_resource_requirements!(builder;
        name = "medium", num_cpus = 4, memory = "8g", runtime = "P0DT8H",
    )
    large = add_resource_requirements!(builder;
        name = "large", num_cpus = 8, memory = "16g", runtime = "P0DT12H",
    )
    scheduler = add_local_scheduler!(builder; name = "test")
    add_user_data!(
        builder;
        name = "my_val1",
        is_ephemeral = false,
        data = Dict("key1" => "val1"),
    )
    add_user_data!(
        builder;
        name = "my_val2",
        is_ephemeral = false,
        data = Dict("key2" => "val2"),
    )
    add_job!(
        builder;
        name = "sleep1",
        command = "python $SLEEP 1",
        resource_requirements = small.name,
        scheduler = "local_schedulers/test",
    )
    add_job!(
        builder;
        name = "sleep2",
        command = "python $SLEEP 1",
        input_user_data = ["my_val1"],
        resource_requirements = medium.name,
        scheduler = "local_schedulers/test",
    )
    add_job!(
        builder;
        name = "sleep3",
        command = "python $SLEEP 1",
        input_user_data = ["my_val2"],
        resource_requirements = large.name,
        scheduler = "local_schedulers/test",
    )

    spec = build!(builder)
    workflow, response = APIClient.post_workflow_specifications(api, spec)
    @test response.status == 200
    if response.status != 200
        error("test cannot continue")
    end

    output_dir = mktempdir()
    try
        result = run(`torc -u $url -k $(workflow._key) workflows start`)
        @test result.exitcode == 0
        result = run(`torc -u $url -k $(workflow._key) jobs run -p 1 -o $output_dir`)
        @test result.exitcode == 0
        results, response = APIClient.get_workflows_workflow_results(api, workflow._key)
        @test response.status == 200
        for result in results.items
            @test result.return_code == 0
        end
    finally
        rm(output_dir, recursive = true)
        APIClient.delete_workflows_key(api, workflow._key)
    end
end
