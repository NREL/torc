# WorkflowConfigModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**worker_startup_script** | **String** |  | [optional] [default to nothing]
**compute_node_resource_stats** | [***ComputeNodeResourceStatsModel**](ComputeNodeResourceStatsModel.md) |  | [optional] [default to nothing]
**compute_node_expiration_buffer_seconds** | **Int64** | Inform all compute nodes to shut down this number of seconds before the expiration time. This allows torc to send SIGTERM to all job processes and set all statuses to terminated. Increase the time in cases where the job processes handle SIGTERM and need more time to gracefully shut down. Set the value to 0 to maximize the time given to jobs. If not set, take the database&#39;s default value of 60 seconds. | [optional] [default to nothing]
**compute_node_wait_for_new_jobs_seconds** | **Int64** | Inform all compute nodes to wait for new jobs for this time period before exiting. Does not apply if the workflow is complete. | [optional] [default to nothing]
**compute_node_ignore_workflow_completion** | **Bool** | Inform all compute nodes to ignore workflow completions and hold onto allocations indefinitely. Useful for debugging failed jobs and possibly dynamic workflows where jobs get added after starting. | [optional] [default to false]
**compute_node_wait_for_healthy_database_minutes** | **Int64** | Inform all compute nodes to wait this number of minutes if the database becomes unresponsive. | [optional] [default to nothing]
**prepare_jobs_sort_method** | **String** | Inform all compute nodes to use this sort method when calling the prepare_jobs_for_submission command. | [optional] [default to "gpus_runtime_memory"]
**_key** | **String** |  | [optional] [default to nothing]
**_id** | **String** |  | [optional] [default to nothing]
**_rev** | **String** |  | [optional] [default to nothing]


[[Back to Model list]](../README.md#models) [[Back to API list]](../README.md#api-endpoints) [[Back to README]](../README.md)


