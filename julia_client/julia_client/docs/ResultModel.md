# ResultModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **Int64** |  | [optional] [default to nothing]
**job_id** | **Int64** | Database ID for the job tied to this result | [default to nothing]
**workflow_id** | **Int64** | Database ID for the workflow tied to this result | [default to nothing]
**run_id** | **Int64** | ID of the workflow run. Incremements on every start and restart. | [default to nothing]
**compute_node_id** | **Int64** | Database ID for the compute node that ran this job | [default to nothing]
**return_code** | **Int64** | Code returned by the job. Zero is success; non-zero is a failure. | [default to nothing]
**exec_time_minutes** | **Float64** | Job execution time in minutes | [default to nothing]
**completion_time** | **String** | Timestamp of when the job completed. | [default to nothing]
**status** | **Any** |  | [default to nothing]


[[Back to Model list]](../README.md#models) [[Back to API list]](../README.md#api-endpoints) [[Back to README]](../README.md)


