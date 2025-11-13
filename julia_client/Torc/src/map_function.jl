using Torc
import Torc: APIClient

function process_mapped_function_cli_args(
    run_job_function::Function,
    run_postprocess_function::Union{Function, Nothing},
)
    if length(ARGS) != 2
        error("Usage: $(PROGRAM_FILE) URL run|postprocess")
    end

    # These environment variables get set by the torc job runner.
    for key in ("TORC_WORKFLOW_KEY", "TORC_JOB_KEY")
        !haskey(ENV, key) && error("Bug: environment variable $key is not defined")
    end
    workflow_key = ENV["TORC_WORKFLOW_KEY"]
    job_key = ENV["TORC_JOB_KEY"]

    url = ARGS[1]
    command = ARGS[2]
    api = make_api(url)
    response = send_api_command(
        api,
        APIClient.list_job_user_data_consumes,
        workflow_key,
        job_key,
    )
    items = response.items

    if command == "run"
        result = _run_function(items, run_job_function)
    elseif command == "postprocess"
        result = _postprocess_function(items, run_postprocess_function)
    end

    if !isnothing(result)
        _store_result(api, workflow_key, job_key, result)
    end
end

function _run_function(input_items::Vector, run_job_function::Function)
    length(input_items) != 1 && error("Bug: unexpected input data: $(input_items)")
    return run_job_function(input_items[1].data["params"])
end

function _postprocess_function(input_items::Vector, run_postprocess_function::Function)
    isempty(input_items) && error("Bug: no results were passed to run_postprocess_function")
    return run_postprocess_function([x.data for x in input_items])
end

function _store_result(api, workflow_key, job_key, result::Dict)
    resp = send_api_command(
        api,
        APIClient.list_job_user_data_stores,
        workflow_key,
        job_key,
    )
    if length(resp.items) != 1
        error(
            "Received unexpected output data placeholder from database: " *
            "job_key = $(job_key) response = $(resp)",
        )
    end

    output = resp.items[1]
    output.data = result
    send_api_command(
        api,
        APIClient.modify_user_data,
        workflow_key,
        output._key,
        output,
    )
    @info "Stored result for $(job_key)"
end
