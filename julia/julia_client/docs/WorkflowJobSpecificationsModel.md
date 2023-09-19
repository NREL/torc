# WorkflowJobSpecificationsModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **String** |  | [optional] [default to nothing]
**key** | **String** |  | [optional] [default to nothing]
**command** | **String** |  | [default to nothing]
**invocation_script** | **String** |  | [optional] [default to nothing]
**cancel_on_blocking_job_failure** | **Bool** |  | [optional] [default to true]
**supports_termination** | **Bool** |  | [optional] [default to false]
**scheduler** | **String** |  | [optional] [default to nothing]
**needs_compute_node_schedule** | **Bool** |  | [optional] [default to false]
**input_user_data** | **Vector{String}** |  | [optional] [default to nothing]
**output_user_data** | **Vector{String}** |  | [optional] [default to nothing]
**resource_requirements** | **String** |  | [optional] [default to nothing]
**input_files** | **Vector{String}** |  | [optional] [default to nothing]
**output_files** | **Vector{String}** |  | [optional] [default to nothing]
**blocked_by** | **Vector{String}** |  | [optional] [default to nothing]


[[Back to Model list]](../README.md#models) [[Back to API list]](../README.md#api-endpoints) [[Back to README]](../README.md)


