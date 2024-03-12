module Torc

include("api/APIClient.jl")
include("workflow_builder.jl")
import OpenAPI
import .APIClient

function make_api(database_url::AbstractString)
    """Instantiate an OpenAPI object from a database URL."""
    return APIClient.DefaultApi(OpenAPI.Clients.Client(database_url))
end

"""
Send a request through the client and throw an exception if it fails.
"""
function send_api_command(api::APIClient.DefaultApi, func, args...; kwargs...)
    data, response = func(api, args...; kwargs...)

    if response.status != 200
        error("Failed to send_api_command: $(response)")
    end

    return data
end

"""
Add an iterable of jobs to the workflow.
"""
function add_jobs(
    api::APIClient.DefaultApi,
    workflow_key::String,
    jobs,
    max_transfer_size = 10_000,
)
    added_jobs = []
    batch = []
    for job in jobs
        push!(batch, job)
        if length(batch) > max_transfer_size
            res = send_api_command(
                api,
                APIClient.add_jobs,
                workflow_key,
                APIClient.JobsModel(; jobs = batch),
            )
            added_jobs = vcat(added_jobs, res.items)
            added_jobs += res.items
            empty!(batch)
        end
    end

    if length(batch) > 0
        res = send_api_command(
            api,
            APIClient.add_jobs,
            workflow_key,
            APIClient.JobsModel(; jobs = batch),
        )
        added_jobs = vcat(added_jobs, res.items)
    end

    return added_jobs
end

"""
Add one job to the workflow for each set of parameters.

# Arguments
- `api::APIClient.DefaultApi`: API instance
- `workflow_key::AbstractString`: Workflow key,
- `file_path::AbstractString`: Path to script that Torc will execute.
- `params::Vector`: Torc will create one job for each set of parameters.
- `project_path = nothing`: If set, will pas this path to julia --project=X when running the
   script.
- `has_postprocess = false`: Set to true if the script defines a postprocess function.
- `resource_requirements = nothing`: If set, Torc will use these resource requirements.
- `scheduler = nothing`: If set, Torc will use this scheduler.
- `start_index = 1`: Torc will use this index for job names.
- `name_prefix = "": Torc will use this prefix for job names.
- `job_names = []: Use these names for jobs. Mutually exclusive with "name_prefix."
- `blocked_by::Union{Nothing, Vector{String}} = nothing`: Set these job IDs as blocking
   the jobs created by this function.
- `cancel_on_blocking_job_failure::Bool = true`: Cancel each job if a blocking job fails.
"""
function map_function_to_jobs(
    api::APIClient.DefaultApi,
    workflow_key::AbstractString,
    file_path::AbstractString,
    params::Vector;
    project_path = nothing,
    has_postprocess = false,
    resource_requirements = nothing,
    scheduler = nothing,
    start_index = 1,
    name_prefix = "",
    job_names::Vector{String} = String[],
    blocked_by::Union{Nothing, Vector{String}} = nothing,
    cancel_on_blocking_job_failure = true,
)
    !isfile(file_path) && error("$file_path does not exist")
    if !isempty(job_names) && length(job_names) != length(params)
        error("If job_names is provided, it must be the same length as params.")
    end
    jobs = Vector{APIClient.JobModel}()
    output_data_ids = Vector{String}()
    ppath = isnothing(project_path) ? "" : "--project=$(project_path)"
    url = api.client.root
    command = "julia $ppath $(file_path) $(url)"

    for (i, job_params) in enumerate(params)
        if !isempty(job_names)
            job_name = job_names[i]
        else
            job_name = "$(name_prefix)$(start_index + i)"
        end
        input_ud = send_api_command(
            api,
            APIClient.add_user_data,
            workflow_key,
            APIClient.UserDataModel(;
                name = "input_$(job_name)",
                data = Dict{String, Any}("params" => job_params)),
        )
        output_ud = send_api_command(
            api,
            APIClient.add_user_data,
            workflow_key,
            APIClient.UserDataModel(;
                name = "output_$(job_name)",
                data = Dict{String, Any}(),
            ),
        )
        @assert !isnothing(input_ud._id)
        @assert !isnothing(output_ud._id)
        push!(output_data_ids, output_ud._id)
        job = APIClient.JobModel(;
            name = job_name,
            command = command * " run",
            input_user_data = [input_ud._id],
            output_user_data = [output_ud._id],
            resource_requirements = resource_requirements,
            scheduler = scheduler,
            blocked_by = blocked_by,
            cancel_on_blocking_job_failure = cancel_on_blocking_job_failure,
        )
        push!(jobs, job)
    end

    if has_postprocess
        output_ud = send_api_command(
            api,
            APIClient.add_user_data,
            workflow_key,
            APIClient.UserDataModel(;
                name = "postprocess_result",
                data = Dict{String, Any}(),
            ),
        )
        @assert !isnothing(output_ud._id)
        push!(jobs,
            APIClient.JobModel(;
                name = "postprocess",
                command = command * " postprocess",
                input_user_data = output_data_ids,
                output_user_data = [output_ud._id],
                resource_requirements = resource_requirements,
                scheduler = scheduler,
            ),
        )
    end

    return add_jobs(api, workflow_key, jobs)
end

include("map_function.jl")

export make_api
export send_api_command
export WorkflowBuilder
export add_file!
export add_jobs
export add_job!
export add_aws_scheduler!
export add_local_scheduler!
export add_slurm_scheduler!
export add_resource_requirements!
export add_user_data!
export configure_resource_monitoring!
export build!
export map_function_to_jobs
export process_mapped_function_cli_args

end # module Torc
