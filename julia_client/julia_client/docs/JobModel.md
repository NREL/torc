# JobModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **Int64** |  | [optional] [default to nothing]
**workflow_id** | **Int64** |  | [default to nothing]
**name** | **String** | Name of the job; no requirements on uniqueness | [default to nothing]
**command** | **String** | CLI command to execute. Will not be executed in a shell and so must not include shell characters. | [default to nothing]
**invocation_script** | **String** | Wrapper script for command in case the environment needs customization. | [optional] [default to nothing]
**status** | **Any** |  | [optional] [default to nothing]
**cancel_on_blocking_job_failure** | **Bool** | Cancel this job if any of its blocking jobs fails. | [optional] [default to true]
**supports_termination** | **Bool** | Informs torc that the job can be terminated gracefully before a wall-time timeout. | [optional] [default to false]
**blocked_by_job_ids** | **Vector{Int64}** | Database IDs of jobs that block this job | [optional] [default to nothing]
**input_file_ids** | **Vector{Int64}** | Database IDs of files that this job needs | [optional] [default to nothing]
**output_file_ids** | **Vector{Int64}** | Database IDs of files that this job produces | [optional] [default to nothing]
**input_user_data_ids** | **Vector{Int64}** | Database IDs of user-data objects that this job needs | [optional] [default to nothing]
**output_user_data_ids** | **Vector{Int64}** | Database IDs of user-data objects that this job produces | [optional] [default to nothing]
**resource_requirements_id** | **Int64** | Optional database ID of resources required by this job | [optional] [default to nothing]
**scheduler_id** | **Int64** | Optional database ID of scheduler needed by this job | [optional] [default to nothing]


[[Back to Model list]](../README.md#models) [[Back to API list]](../README.md#api-endpoints) [[Back to README]](../README.md)


