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
        error("Failed to create workflow: $(response)")
    end

    return data
end

"""
Add an iterable of jobs to the workflow.
"""
function add_jobs(api::APIClient.DefaultApi, workflow_key::String, jobs, max_transfer_size=10_000)
    added_jobs = []
    batch = []
    for job in jobs
        push!(batch, job)
        if length(batch) > max_transfer_size
            res = send_api_command(api, APIClient.add_jobs, workflow_key, APIClient.JobsModel(jobs=batch))
            added_jobs = vcat(added_jobs, res.items)
            added_jobs += res.items
            empty!(batch)
        end
    end

    if length(batch) > 0
        res = send_api_command(api, APIClient.add_jobs, workflow_key, APIClient.JobsModel(jobs=batch))
        added_jobs = vcat(added_jobs, res.items)
    end

    return added_jobs
end

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

end # module Torc
