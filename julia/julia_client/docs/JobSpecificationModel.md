# JobSpecificationModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **String** | Name of the job; must be unique within the workflow specification. | [optional] [default to nothing]
**key** | **String** | Optional database identifier for the job. If set, must be unique. It is recommended to let the database create the identifier. | [optional] [default to nothing]
**command** | **String** | CLI command to execute. Will not be executed in a shell and so must not include shell characters. | [default to nothing]
**invocation_script** | **String** | Wrapper script for command in case the environment needs customization. | [optional] [default to nothing]
**cancel_on_blocking_job_failure** | **Bool** | Cancel this job if any of its blocking jobs fails. | [optional] [default to true]
**supports_termination** | **Bool** | Informs torc that the job can be terminated gracefully before a wall-time timeout. | [optional] [default to false]
**scheduler** | **String** | Optional name of scheduler needed by this job | [optional] [default to nothing]
**schedule_compute_nodes** | [***ComputeNodeScheduleParams**](ComputeNodeScheduleParams.md) |  | [optional] [default to nothing]
**input_user_data** | **Vector{String}** | Names of user-data objects that this job needs | [optional] [default to nothing]
**output_user_data** | **Vector{String}** | Names of user-data objects that this job produces | [optional] [default to nothing]
**resource_requirements** | **String** | Optional name of resources required by this job | [optional] [default to nothing]
**input_files** | **Vector{String}** | Names of files that this job needs | [optional] [default to nothing]
**output_files** | **Vector{String}** | Names of files that this job produces | [optional] [default to nothing]
**blocked_by** | **Vector{String}** | Names of jobs that block this job | [optional] [default to nothing]


[[Back to Model list]](../README.md#models) [[Back to API list]](../README.md#api-endpoints) [[Back to README]](../README.md)


