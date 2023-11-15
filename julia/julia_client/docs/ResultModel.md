# ResultModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_key** | **String** | Database key for the job tied to this result | [default to nothing]
**run_id** | **Int64** | ID of the workflow run. Incremements on every start and restart. | [default to nothing]
**return_code** | **Int64** | Code returned by the job. Zero is success; non-zero is a failure. | [default to nothing]
**exec_time_minutes** | **Float64** | Job execution time in minutes | [default to nothing]
**completion_time** | **String** | Timestamp of when the job completed. | [default to nothing]
**status** | **String** | Status of the job; managed by torc. | [default to nothing]
**_key** | **String** | Unique database identifier for the result. Does not include collection name. | [optional] [default to nothing]
**_id** | **String** | Unique database identifier for the result. Includes collection name and _key. | [optional] [default to nothing]
**_rev** | **String** | Database revision of the result | [optional] [default to nothing]


[[Back to Model list]](../README.md#models) [[Back to API list]](../README.md#api-endpoints) [[Back to README]](../README.md)


