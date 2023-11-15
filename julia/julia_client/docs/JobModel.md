# JobModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **String** | Name of the job; no requirements on uniqueness | [optional] [default to nothing]
**command** | **String** | CLI command to execute. Will not be executed in a shell and so must not include shell characters. | [default to nothing]
**invocation_script** | **String** | Wrapper script for command in case the environment needs customization. | [optional] [default to nothing]
**status** | **String** | Status of job; managed by torc. | [optional] [default to nothing]
**needs_compute_node_schedule** | **Bool** | Informs torc to schedule a compute node to start this job. | [optional] [default to false]
**cancel_on_blocking_job_failure** | **Bool** | Cancel this job if any of its blocking jobs fails. | [optional] [default to true]
**supports_termination** | **Bool** | Informs torc that the job can be terminated gracefully before a wall-time timeout. | [optional] [default to false]
**blocked_by** | **Vector{String}** | Database IDs of jobs that block this job | [optional] [default to nothing]
**input_files** | **Vector{String}** | Database IDs of files that this job needs | [optional] [default to nothing]
**output_files** | **Vector{String}** | Database IDs of files that this job produces | [optional] [default to nothing]
**input_user_data** | **Vector{String}** | Database IDs of user-data objects that this job needs | [optional] [default to nothing]
**output_user_data** | **Vector{String}** | Database IDs of user-data objects that this job produces | [optional] [default to nothing]
**resource_requirements** | **String** | Optional database ID of resources required by this job | [optional] [default to nothing]
**scheduler** | **String** | Optional database ID of scheduler needed by this job | [optional] [default to nothing]
**internal** | [***JobsInternal**](JobsInternal.md) |  | [optional] [default to nothing]
**_key** | **String** | Unique database identifier for the job. Does not include collection name. | [optional] [default to nothing]
**_id** | **String** | Unique database identifier for the job. Includes collection name and _key. | [optional] [default to nothing]
**_rev** | **String** | Database revision of the job | [optional] [default to nothing]


[[Back to Model list]](../README.md#models) [[Back to API list]](../README.md#api-endpoints) [[Back to README]](../README.md)


