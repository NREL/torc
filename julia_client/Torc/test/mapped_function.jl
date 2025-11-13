using Torc

"""
Function to be mapped across workers.
"""
function run_job_function(params::Dict)
    @assert "val" in keys(params)
    return Dict(
        "params" => params,
        "result" => 5,
        "output_data_path" => "/projects/my-project/run1",
    )
end

"""
Collect the results of workers.
"""
function run_postprocess_function(results::Vector{<:Dict})
    total = 0
    paths = String[]
    for result in results
        @assert "result" in keys(result)
        @assert "output_data_path" in keys(result)
        total += result["result"]
        push!(paths, result["output_data_path"])
    end
    return Dict("total" => total, "output_data_paths" => paths)
end

if abspath(PROGRAM_FILE) == @__FILE__
    process_mapped_function_cli_args(run_job_function, run_postprocess_function)
end
