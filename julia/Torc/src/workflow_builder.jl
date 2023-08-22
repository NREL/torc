"""
Helper struct to build a workflow dynamically
"""
mutable struct WorkflowBuilder
    files::Vector{APIClient.WorkflowFilesModel}
    jobs::Vector{APIClient.WorkflowJobSpecificationsModel}
    resource_requirements::Vector{APIClient.WorkflowResourceRequirementsModel}
    aws_schedulers::Vector{APIClient.WorkflowAwsSchedulersModel}
    local_schedulers::Vector{APIClient.WorkflowLocalSchedulersModel}
    slurm_schedulers::Vector{APIClient.WorkflowSlurmSchedulersModel}
    user_data::Vector{APIClient.WorkflowUserDataModel}
    resource_monitor_config::Union{
        Nothing,
        APIClient.ComputeNodeResourceStatsModel,
    }
    compute_node_wait_for_new_jobs_seconds::Int
    compute_node_wait_for_healthy_database_minutes::Union{Int, Nothing}
    compute_node_expiration_buffer_seconds::Union{Int, Nothing}
    compute_node_ignore_workflow_completion::Bool
end

function WorkflowBuilder()
    WorkflowBuilder(
        Vector{APIClient.WorkflowFilesModel}(),
        Vector{APIClient.WorkflowJobSpecificationsModel}(),
        Vector{APIClient.WorkflowResourceRequirementsModel}(),
        Vector{APIClient.WorkflowAwsSchedulersModel}(),
        Vector{APIClient.WorkflowLocalSchedulersModel}(),
        Vector{APIClient.WorkflowSlurmSchedulersModel}(),
        Vector{APIClient.WorkflowUserDataModel}(),
        APIClient.ComputeNodeResourceStatsModel(),
        0,
        nothing,
        nothing,
        false,
    )
end

"""
Add a file and return it.
"""
function add_file!(builder::WorkflowBuilder, args...; kwargs...)
    push!(builder.files, APIClient.WorkflowFilesModel(args...; kwargs...))
    return builder.files[end]
end

"""
Add a job and return it.
"""
function add_job!(builder::WorkflowBuilder, args...; kwargs...)
    push!(builder.jobs, APIClient.WorkflowJobSpecificationsModel(args...; kwargs...))
    return builder.jobs[end]
end

"""
Add a resource requirements object and return it.
"""
function add_resource_requirements!(builder::WorkflowBuilder, args...; kwargs...)
    push!(
        builder.resource_requirements,
        APIClient.WorkflowResourceRequirementsModel(args...; kwargs...),
    )
    return builder.resource_requirements[end]
end

"""
Add an AWS scheduler and return it.
"""
function add_aws_scheduler!(builder::WorkflowBuilder, args...; kwargs...)
    push!(builder.aws_schedulers, APIClient.WorkflowAwsSchedulersModel(args...; kwargs...))
    return builder.aws_schedulers[end]
end

"""
Add a local scheduler and return it.
"""
function add_local_scheduler!(builder::WorkflowBuilder, args...; kwargs...)
    push!(
        builder.local_schedulers,
        APIClient.WorkflowLocalSchedulersModel(args...; kwargs...),
    )
    return builder.local_schedulers[end]
end

"""
Add a local scheduler and return it.
"""
function add_slurm_scheduler!(builder::WorkflowBuilder, args...; kwargs...)
    push!(
        builder.slurm_schedulers,
        APIClient.WorkflowSlurmSchedulersModel(args...; kwargs...),
    )
    return builder.slurm_schedulers[end]
end

"""
Add a user data object and return it.
"""
function add_user_data!(builder::WorkflowBuilder, args...; kwargs...)
    push!(builder.user_data, APIClient.WorkflowUserDataModel(args...; kwargs...))
    return builder.user_data[end]
end

"""
Configure resource monitoring for the workflow. Refer to
ComputeNodeResourceStatsModel for input parameters.
"""
function configure_resource_monitoring!(builder::WorkflowBuilder, args...; kwargs...)
    builder.resource_monitor_config =
        APIClient.ComputeNodeResourceStatsModel(args...; kwargs...)
end

"""
Inform all compute nodes to wait for new jobs for this time period before exiting.
Does not apply if the workflow is complete.
"""
function set_compute_node_wait_for_new_jobs_seconds!(builder::WorkflowBuilder, val::Int)
    builder.compute_node_wait_for_new_jobs_seconds = val
end

"""
Inform all compute nodes to wait for this time period if the database becomes unresponsive.
"""
function set_compute_node_wait_for_healthy_database!(builder::WorkflowBuilder, val::Int)
    builder.compute_node_wait_for_healthy_database_minutes = val
end

"""
Inform all compute nodes to ignore workflow completions and hold onto allocations
indefinitely. Useful for debugging failed jobs and possibly dynamic workflows where jobs
get added after starting.
"""
function set_compute_node_ignore_workflow_completion!(builder::WorkflowBuilder, val::Bool)
    builder.compute_node_ignore_workflow_completion = val
end

"""
Inform all compute nodes to shut down this number of seconds before the
expiration time. This allows torc to send SIGTERM to all job processes and set all
statuses to terminated. Increase the time in cases where the job processes handle SIGTERM
and need more time to gracefully shut down. Set the value to 0 to maximize the time given
to jobs. If not set, take the database's default value of 30 seconds.
"""
function set_compute_node_expiration_buffer_seconds!(builder::WorkflowBuilder, val::Int)
    builder.compute_node_expiration_buffer_seconds = val
end

"""
Build a workflow specification from the stored parameters.
"""
function build!(builder::WorkflowBuilder, args...; kwargs...)
    config = APIClient.WorkflowConfigModel(;
        compute_node_resource_stats = builder.resource_monitor_config,
        compute_node_wait_for_new_jobs_seconds = builder.compute_node_wait_for_new_jobs_seconds,
        compute_node_wait_for_healthy_database_minutes = builder.compute_node_wait_for_healthy_database_minutes,
        compute_node_ignore_workflow_completion = builder.compute_node_ignore_workflow_completion,
        compute_node_expiration_buffer_seconds = builder.compute_node_expiration_buffer_seconds,
    )
    return APIClient.WorkflowSpecificationsModel(
        args...;
        config = config,
        files = isempty(builder.files) ? nothing : builder.files,
        jobs = isempty(builder.jobs) ? nothing : builder.jobs,
        resource_requirements = if isempty(builder.resource_requirements)
            nothing
        else
            builder.resource_requirements
        end,
        schedulers = APIClient.WorkflowSpecificationsSchedulers(;
            aws_schedulers = if isempty(builder.aws_schedulers)
                nothing
            else
                builder.aws_schedulers
            end,
            local_schedulers = if isempty(builder.local_schedulers)
                nothing
            else
                builder.local_schedulers
            end,
            slurm_schedulers = if isempty(builder.slurm_schedulers)
                nothing
            else
                builder.slurm_schedulers
            end,
        ),
        user_data = isempty(builder.user_data) ? nothing : builder.user_data,
        kwargs...,
    )
end
