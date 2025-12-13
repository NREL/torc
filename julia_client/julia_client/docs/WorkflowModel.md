# WorkflowModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **Int64** |  | [optional] [default to nothing]
**name** | **String** | Name of the workflow | [default to nothing]
**user** | **String** | User that created the workflow | [default to nothing]
**description** | **String** | Description of the workflow | [optional] [default to nothing]
**timestamp** | **String** | Timestamp of workflow creation | [optional] [default to nothing]
**compute_node_expiration_buffer_seconds** | **Int64** | Inform all compute nodes to shut down this number of seconds before the expiration time. This allows torc to send SIGTERM to all job processes and set all statuses to terminated. Increase the time in cases where the job processes handle SIGTERM and need more time to gracefully shut down. Set the value to 0 to maximize the time given to jobs. If not set, take the database&#39;s default value of 60 seconds. | [optional] [default to 60]
**compute_node_wait_for_new_jobs_seconds** | **Int64** | Inform all compute nodes to wait for new jobs for this time period before exiting. Does not apply if the workflow is complete. | [optional] [default to 60]
**compute_node_ignore_workflow_completion** | **Bool** | Inform all compute nodes to ignore workflow completions and hold onto allocations indefinitely. Useful for debugging failed jobs and possibly dynamic workflows where jobs get added after starting. | [optional] [default to false]
**compute_node_wait_for_healthy_database_minutes** | **Int64** | Inform all compute nodes to wait this number of minutes if the database becomes unresponsive. | [optional] [default to 20]
**jobs_sort_method** | [***JobsSortMethod**](JobsSortMethod.md) |  | [optional] [default to nothing]
**status_id** | **Int64** |  | [optional] [default to nothing]


[[Back to Model list]](../README.md#models) [[Back to API list]](../README.md#api-endpoints) [[Back to README]](../README.md)


