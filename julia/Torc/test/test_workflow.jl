const BASE_DIR = dirname(dirname(Base.find_package("Torc")))
const SLEEP = joinpath(BASE_DIR, "..", "..", "torc_package", "tests", "scripts", "sleep.py")

function create_workflow(api)
    return send_api_command(
        api,
        APIClient.add_workflow,
        APIClient.WorkflowModel(;
            user = "user",
            name = "test",
            description = "test workflow",
        ),
    )
end

function build_workflow(api, workflow)
    small = send_api_command(
        api,
        APIClient.add_resource_requirements,
        workflow._key,
        APIClient.ResourceRequirementsModel(;
            name = "small",
            num_cpus = 1,
            memory = "1g",
            runtime = "P0DT1H",
        ),
    )
    medium = send_api_command(
        api,
        APIClient.add_resource_requirements,
        workflow._key,
        APIClient.ResourceRequirementsModel(;
            name = "medium",
            num_cpus = 4,
            memory = "8g",
            runtime = "P0DT8H",
        ),
    )
    large = send_api_command(
        api,
        APIClient.add_resource_requirements,
        workflow._key,
        APIClient.ResourceRequirementsModel(;
            name = "large",
            num_cpus = 8,
            memory = "16g",
            runtime = "P0DT12H",
        ),
    )
    ud1 = send_api_command(
        api,
        APIClient.add_user_data,
        workflow._key,
        APIClient.UserDataModel(;
            name = "my_val1",
            is_ephemeral = false,
            data = Dict("key1" => "val1"),
        ),
    )
    ud2 = send_api_command(
        api,
        APIClient.add_user_data,
        workflow._key,
        APIClient.UserDataModel(;
            name = "my_val2",
            is_ephemeral = false,
            data = Dict("key2" => "val2"),
        ),
    )
    jobs = [
        APIClient.JobModel(;
            name = "sleep1",
            command = "python $SLEEP 1",
            resource_requirements = small._id,
        ),
        APIClient.JobModel(;
            name = "sleep2",
            command = "python $SLEEP 1",
            input_user_data = [ud1._id],
            resource_requirements = medium._id,
        ),
        APIClient.JobModel(;
            name = "sleep2",
            command = "python $SLEEP 1",
            input_user_data = [ud1._id],
            resource_requirements = medium._id,
        ),
        APIClient.JobModel(;
            name = "sleep3",
            command = "python $SLEEP 1",
            input_user_data = [ud2._id],
            resource_requirements = large._id,
        ),
    ]
    add_jobs(api, workflow._key, jobs)
end

function get_url()
    return get(
        ENV,
        "TORC_DATABASE_URL",
        "http://localhost:8529/_db/test-workflows/torc-service",
    )
end

@testset "Test workflow" begin
    url = get_url()
    api = make_api(url)
    workflow = create_workflow(api)
    output_dir = mktempdir()
    try
        build_workflow(api, workflow)
        result = run(`torc -u $url -k $(workflow._key) workflows start`)
        @test result.exitcode == 0
        result = run(`torc -u $url -k $(workflow._key) jobs run -p 1 -o $output_dir`)
        @test result.exitcode == 0
        results, response = APIClient.list_results(api, workflow._key)
        @test response.status == 200
        for result in results.items
            @test result.return_code == 0
        end
    finally
        rm(output_dir; recursive = true)
        APIClient.remove_workflow(api, workflow._key)
    end
end

@testset "Test mapped function workflow" begin
    url = get_url()
    api = make_api(url)
    workflow = create_workflow(api)
    output_dir = mktempdir()
    params = [Dict("val" => i) for i in 1:5]
    project_path = BASE_DIR
    try
        jobs = map_function_to_jobs(
            api,
            workflow._key,
            joinpath(BASE_DIR, "test", "mapped_function.jl"),
            params;
            project_path = BASE_DIR,
            has_postprocess = true,
        )
        @test !isempty(jobs)
        result = run(`torc -u $url -k $(workflow._key) workflows start`)
        @test result.exitcode == 0
        result = run(`torc -u $url -k $(workflow._key) jobs run -p 1 -o $output_dir`)
        @test result.exitcode == 0
        results, response = APIClient.list_results(api, workflow._key)
        @test response.status == 200
        for result in results.items
            @test result.return_code == 0
        end

        postprocess_job = jobs[end]
        result_ud = send_api_command(
            api,
            APIClient.list_job_user_data_stores,
            workflow._key,
            postprocess_job._key,
        )
        @test length(result_ud.items) == 1
        @test result_ud.items[1].data["total"] == 25
        @test "output_data_paths" in keys(result_ud.items[1].data)
    finally
        rm(output_dir; recursive = true)
        APIClient.remove_workflow(api, workflow._key)
    end
end
