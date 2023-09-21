# DefaultApi

All URIs are relative to *http://localhost/_db/test-workflows/torc-service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_workflows_key**](DefaultApi.md#delete_workflows_key) | **DELETE** /workflows/{key} | Delete a workflow
[**delete_workflows_workflow_aws_schedulers**](DefaultApi.md#delete_workflows_workflow_aws_schedulers) | **DELETE** /workflows/{workflow}/aws_schedulers | Delete all documents of type AWS compute node configuration for a workflow
[**delete_workflows_workflow_aws_schedulers_key**](DefaultApi.md#delete_workflows_workflow_aws_schedulers_key) | **DELETE** /workflows/{workflow}/aws_schedulers/{key} | Delete a document of type AWS compute node configuration
[**delete_workflows_workflow_compute_node_stats**](DefaultApi.md#delete_workflows_workflow_compute_node_stats) | **DELETE** /workflows/{workflow}/compute_node_stats | Delete all documents of type compute node statistics for a workflow
[**delete_workflows_workflow_compute_node_stats_key**](DefaultApi.md#delete_workflows_workflow_compute_node_stats_key) | **DELETE** /workflows/{workflow}/compute_node_stats/{key} | Delete a document of type compute node statistics
[**delete_workflows_workflow_compute_nodes**](DefaultApi.md#delete_workflows_workflow_compute_nodes) | **DELETE** /workflows/{workflow}/compute_nodes | Delete all documents of type compute node for a workflow
[**delete_workflows_workflow_compute_nodes_key**](DefaultApi.md#delete_workflows_workflow_compute_nodes_key) | **DELETE** /workflows/{workflow}/compute_nodes/{key} | Delete a document of type compute node
[**delete_workflows_workflow_edges_name**](DefaultApi.md#delete_workflows_workflow_edges_name) | **DELETE** /workflows/{workflow}/edges/{name} | Delete all edges from the designated collection
[**delete_workflows_workflow_edges_name_key**](DefaultApi.md#delete_workflows_workflow_edges_name_key) | **DELETE** /workflows/{workflow}/edges/{name}/{key} | Delete an edge
[**delete_workflows_workflow_events**](DefaultApi.md#delete_workflows_workflow_events) | **DELETE** /workflows/{workflow}/events | Delete all documents of type event for a workflow
[**delete_workflows_workflow_events_key**](DefaultApi.md#delete_workflows_workflow_events_key) | **DELETE** /workflows/{workflow}/events/{key} | Delete a document of type event
[**delete_workflows_workflow_files**](DefaultApi.md#delete_workflows_workflow_files) | **DELETE** /workflows/{workflow}/files | Delete all documents of type file for a workflow
[**delete_workflows_workflow_files_key**](DefaultApi.md#delete_workflows_workflow_files_key) | **DELETE** /workflows/{workflow}/files/{key} | Delete a document of type file
[**delete_workflows_workflow_job_process_stats**](DefaultApi.md#delete_workflows_workflow_job_process_stats) | **DELETE** /workflows/{workflow}/job_process_stats | Delete all documents of type job process statistics for a workflow
[**delete_workflows_workflow_job_process_stats_key**](DefaultApi.md#delete_workflows_workflow_job_process_stats_key) | **DELETE** /workflows/{workflow}/job_process_stats/{key} | Delete a document of type job process statistics
[**delete_workflows_workflow_jobs**](DefaultApi.md#delete_workflows_workflow_jobs) | **DELETE** /workflows/{workflow}/jobs | Delete all documents of type job for a workflow
[**delete_workflows_workflow_jobs_key**](DefaultApi.md#delete_workflows_workflow_jobs_key) | **DELETE** /workflows/{workflow}/jobs/{key} | Delete a document of type job
[**delete_workflows_workflow_local_schedulers**](DefaultApi.md#delete_workflows_workflow_local_schedulers) | **DELETE** /workflows/{workflow}/local_schedulers | Delete all documents of type local compute node configuration for a workflow
[**delete_workflows_workflow_local_schedulers_key**](DefaultApi.md#delete_workflows_workflow_local_schedulers_key) | **DELETE** /workflows/{workflow}/local_schedulers/{key} | Delete a document of type local compute node configuration
[**delete_workflows_workflow_resource_requirements**](DefaultApi.md#delete_workflows_workflow_resource_requirements) | **DELETE** /workflows/{workflow}/resource_requirements | Delete all documents of type resource requirements for a workflow
[**delete_workflows_workflow_resource_requirements_key**](DefaultApi.md#delete_workflows_workflow_resource_requirements_key) | **DELETE** /workflows/{workflow}/resource_requirements/{key} | Delete a document of type resource requirements
[**delete_workflows_workflow_results**](DefaultApi.md#delete_workflows_workflow_results) | **DELETE** /workflows/{workflow}/results | Delete all documents of type result for a workflow
[**delete_workflows_workflow_results_key**](DefaultApi.md#delete_workflows_workflow_results_key) | **DELETE** /workflows/{workflow}/results/{key} | Delete a document of type result
[**delete_workflows_workflow_scheduled_compute_nodes**](DefaultApi.md#delete_workflows_workflow_scheduled_compute_nodes) | **DELETE** /workflows/{workflow}/scheduled_compute_nodes | Delete all documents of type scheduled compute node for a workflow
[**delete_workflows_workflow_scheduled_compute_nodes_key**](DefaultApi.md#delete_workflows_workflow_scheduled_compute_nodes_key) | **DELETE** /workflows/{workflow}/scheduled_compute_nodes/{key} | Delete a document of type scheduled compute node
[**delete_workflows_workflow_slurm_schedulers**](DefaultApi.md#delete_workflows_workflow_slurm_schedulers) | **DELETE** /workflows/{workflow}/slurm_schedulers | Delete all documents of type Slurm compute node configuration for a workflow
[**delete_workflows_workflow_slurm_schedulers_key**](DefaultApi.md#delete_workflows_workflow_slurm_schedulers_key) | **DELETE** /workflows/{workflow}/slurm_schedulers/{key} | Delete a document of type Slurm compute node configuration
[**delete_workflows_workflow_user_data**](DefaultApi.md#delete_workflows_workflow_user_data) | **DELETE** /workflows/{workflow}/user_data | Delete all documents of type user data for a workflow
[**delete_workflows_workflow_user_data_key**](DefaultApi.md#delete_workflows_workflow_user_data_key) | **DELETE** /workflows/{workflow}/user_data/{key} | Delete a document of type user data
[**get_aws_schedulers**](DefaultApi.md#get_aws_schedulers) | **GET** /workflows/{workflow}/aws_schedulers | Retrieve all AWS compute node configuration documents
[**get_aws_schedulers_key**](DefaultApi.md#get_aws_schedulers_key) | **GET** /workflows/{workflow}/aws_schedulers/{key} | Retrieve the AWS compute node configuration for a key.
[**get_compute_node_stats**](DefaultApi.md#get_compute_node_stats) | **GET** /workflows/{workflow}/compute_node_stats | Retrieve all compute node statistics documents
[**get_compute_node_stats_key**](DefaultApi.md#get_compute_node_stats_key) | **GET** /workflows/{workflow}/compute_node_stats/{key} | Retrieve the compute node statistics for a key.
[**get_compute_nodes**](DefaultApi.md#get_compute_nodes) | **GET** /workflows/{workflow}/compute_nodes | Retrieve all compute node documents
[**get_compute_nodes_key**](DefaultApi.md#get_compute_nodes_key) | **GET** /workflows/{workflow}/compute_nodes/{key} | Retrieve the compute node for a key.
[**get_edges_name**](DefaultApi.md#get_edges_name) | **GET** /workflows/{workflow}/edges/{name} | Retrieve all edges from the designated collection.
[**get_edges_name_key**](DefaultApi.md#get_edges_name_key) | **GET** /workflows/{workflow}/edges/{name}/{key} | Retrieve an edge
[**get_events**](DefaultApi.md#get_events) | **GET** /workflows/{workflow}/events | Retrieve all event documents
[**get_events_after_key**](DefaultApi.md#get_events_after_key) | **GET** /workflows/{key}/events_after_key/{event_key} | Return all events newer than the event with event_key.
[**get_events_key**](DefaultApi.md#get_events_key) | **GET** /workflows/{workflow}/events/{key} | Retrieve the event for a key.
[**get_files**](DefaultApi.md#get_files) | **GET** /workflows/{workflow}/files | Retrieve all file documents
[**get_files_key**](DefaultApi.md#get_files_key) | **GET** /workflows/{workflow}/files/{key} | Retrieve the file for a key.
[**get_files_produced_by_job_key**](DefaultApi.md#get_files_produced_by_job_key) | **GET** /workflows/{workflow}/files/produced_by_job/{key} | Retrieve files produced by a job
[**get_job_keys**](DefaultApi.md#get_job_keys) | **GET** /workflows/{workflow}/job_keys | Retrieve all job keys for a workflow.
[**get_job_process_stats**](DefaultApi.md#get_job_process_stats) | **GET** /workflows/{workflow}/job_process_stats | Retrieve all job process statistics documents
[**get_job_process_stats_key**](DefaultApi.md#get_job_process_stats_key) | **GET** /workflows/{workflow}/job_process_stats/{key} | Retrieve the job process statistics for a key.
[**get_job_specifications**](DefaultApi.md#get_job_specifications) | **GET** /workflows/{workflow}/job_specifications | Retrieve all job definitions
[**get_job_specifications_key**](DefaultApi.md#get_job_specifications_key) | **GET** /workflows/{workflow}/job_specifications/{key} | Retrieve a job
[**get_jobs**](DefaultApi.md#get_jobs) | **GET** /workflows/{workflow}/jobs | Retrieve all job documents
[**get_jobs_find_by_needs_file_key**](DefaultApi.md#get_jobs_find_by_needs_file_key) | **GET** /workflows/{workflow}/jobs/find_by_needs_file/{key} | Retrieve all jobs that need a file
[**get_jobs_find_by_status_status**](DefaultApi.md#get_jobs_find_by_status_status) | **GET** /workflows/{workflow}/jobs/find_by_status/{status} | Retrieve all jobs with a specific status
[**get_jobs_key**](DefaultApi.md#get_jobs_key) | **GET** /workflows/{workflow}/jobs/{key} | Retrieve the job for a key.
[**get_jobs_key_process_stats**](DefaultApi.md#get_jobs_key_process_stats) | **GET** /workflows/{workflow}/jobs/{key}/process_stats | Retrieve the job process stats for a job.
[**get_jobs_key_resource_requirements**](DefaultApi.md#get_jobs_key_resource_requirements) | **GET** /workflows/{workflow}/jobs/{key}/resource_requirements | Retrieve the resource requirements for a job.
[**get_jobs_key_user_data_consumes**](DefaultApi.md#get_jobs_key_user_data_consumes) | **GET** /workflows/{workflow}/jobs/{key}/user_data_consumes | Retrieve all user data consumed by a job.
[**get_jobs_key_user_data_stores**](DefaultApi.md#get_jobs_key_user_data_stores) | **GET** /workflows/{workflow}/jobs/{key}/user_data_stores | Retrieve all user data for a job.
[**get_latest_event_key**](DefaultApi.md#get_latest_event_key) | **GET** /workflows/{key}/latest_event_key | Return the key of the latest event.
[**get_local_schedulers**](DefaultApi.md#get_local_schedulers) | **GET** /workflows/{workflow}/local_schedulers | Retrieve all local compute node configuration documents
[**get_local_schedulers_key**](DefaultApi.md#get_local_schedulers_key) | **GET** /workflows/{workflow}/local_schedulers/{key} | Retrieve the local compute node configuration for a key.
[**get_ping**](DefaultApi.md#get_ping) | **GET** /ping | Check if the service is running.
[**get_resource_requirements**](DefaultApi.md#get_resource_requirements) | **GET** /workflows/{workflow}/resource_requirements | Retrieve all resource requirements documents
[**get_resource_requirements_key**](DefaultApi.md#get_resource_requirements_key) | **GET** /workflows/{workflow}/resource_requirements/{key} | Retrieve the resource requirements for a key.
[**get_results**](DefaultApi.md#get_results) | **GET** /workflows/{workflow}/results | Retrieve all result documents
[**get_results_find_by_job_key**](DefaultApi.md#get_results_find_by_job_key) | **GET** /workflows/{workflow}/results/find_by_job/{key} | Retrieve the latest result for a job
[**get_results_key**](DefaultApi.md#get_results_key) | **GET** /workflows/{workflow}/results/{key} | Retrieve the result for a key.
[**get_scheduled_compute_nodes**](DefaultApi.md#get_scheduled_compute_nodes) | **GET** /workflows/{workflow}/scheduled_compute_nodes | Retrieve all scheduled compute node documents
[**get_scheduled_compute_nodes_key**](DefaultApi.md#get_scheduled_compute_nodes_key) | **GET** /workflows/{workflow}/scheduled_compute_nodes/{key} | Retrieve the scheduled compute node for a key.
[**get_slurm_schedulers**](DefaultApi.md#get_slurm_schedulers) | **GET** /workflows/{workflow}/slurm_schedulers | Retrieve all Slurm compute node configuration documents
[**get_slurm_schedulers_key**](DefaultApi.md#get_slurm_schedulers_key) | **GET** /workflows/{workflow}/slurm_schedulers/{key} | Retrieve the Slurm compute node configuration for a key.
[**get_user_data**](DefaultApi.md#get_user_data) | **GET** /workflows/{workflow}/user_data | Retrieve all user data documents
[**get_user_data_key**](DefaultApi.md#get_user_data_key) | **GET** /workflows/{workflow}/user_data/{key} | Retrieve the user data for a key.
[**get_version**](DefaultApi.md#get_version) | **GET** /version | Return the version of the service.
[**get_workflow_specifications_example**](DefaultApi.md#get_workflow_specifications_example) | **GET** /workflow_specifications/example | Retrieve an example workflow specification
[**get_workflow_specifications_key**](DefaultApi.md#get_workflow_specifications_key) | **GET** /workflow_specifications/{key} | Retrieve the current workflow
[**get_workflow_specifications_template**](DefaultApi.md#get_workflow_specifications_template) | **GET** /workflow_specifications/template | Retrieve the workflow specification template
[**get_workflows**](DefaultApi.md#get_workflows) | **GET** /workflows | Retrieve all workflows
[**get_workflows_key**](DefaultApi.md#get_workflows_key) | **GET** /workflows/{key} | Retrieve the workflow for an key.
[**get_workflows_key_collection_names**](DefaultApi.md#get_workflows_key_collection_names) | **GET** /workflows/{key}/collection_names | Retrieve all collection names for one workflow.
[**get_workflows_key_config**](DefaultApi.md#get_workflows_key_config) | **GET** /workflows/{key}/config | Returns the workflow config.
[**get_workflows_key_dot_graph_name**](DefaultApi.md#get_workflows_key_dot_graph_name) | **GET** /workflows/{key}/dot_graph/{name} | Build a string for a DOT graph.
[**get_workflows_key_is_complete**](DefaultApi.md#get_workflows_key_is_complete) | **GET** /workflows/{key}/is_complete | Report whether the workflow is complete
[**get_workflows_key_missing_user_data**](DefaultApi.md#get_workflows_key_missing_user_data) | **GET** /workflows/{key}/missing_user_data | List missing user data that should exist.
[**get_workflows_key_ready_job_requirements**](DefaultApi.md#get_workflows_key_ready_job_requirements) | **GET** /workflows/{key}/ready_job_requirements | Return the resource requirements for ready jobs.
[**get_workflows_key_required_existing_files**](DefaultApi.md#get_workflows_key_required_existing_files) | **GET** /workflows/{key}/required_existing_files | List files that must exist.
[**get_workflows_key_status**](DefaultApi.md#get_workflows_key_status) | **GET** /workflows/{key}/status | Reports the workflow status.
[**post_aws_schedulers**](DefaultApi.md#post_aws_schedulers) | **POST** /workflows/{workflow}/aws_schedulers | Store a AWS compute node configuration.
[**post_bulk_jobs**](DefaultApi.md#post_bulk_jobs) | **POST** /workflows/{workflow}/bulk_jobs | Add jobs in bulk with edge definitions.
[**post_compute_node_stats**](DefaultApi.md#post_compute_node_stats) | **POST** /workflows/{workflow}/compute_node_stats | Store a compute node statistics.
[**post_compute_nodes**](DefaultApi.md#post_compute_nodes) | **POST** /workflows/{workflow}/compute_nodes | Store a compute node.
[**post_edges_name**](DefaultApi.md#post_edges_name) | **POST** /workflows/{workflow}/edges/{name} | Store an edge between two vertexes.
[**post_events**](DefaultApi.md#post_events) | **POST** /workflows/{workflow}/events | Store a event.
[**post_files**](DefaultApi.md#post_files) | **POST** /workflows/{workflow}/files | Store a file.
[**post_job_process_stats**](DefaultApi.md#post_job_process_stats) | **POST** /workflows/{workflow}/job_process_stats | Store a job process statistics.
[**post_job_specifications**](DefaultApi.md#post_job_specifications) | **POST** /workflows/{workflow}/job_specifications | Store a job and create edges.
[**post_jobs**](DefaultApi.md#post_jobs) | **POST** /workflows/{workflow}/jobs | Store a job.
[**post_jobs_key_complete_job_status_rev_run_id**](DefaultApi.md#post_jobs_key_complete_job_status_rev_run_id) | **POST** /workflows/{workflow}/jobs/{key}/complete_job/{status}/{rev}/{run_id} | Complete a job and add a result.
[**post_jobs_key_user_data**](DefaultApi.md#post_jobs_key_user_data) | **POST** /workflows/{workflow}/jobs/{key}/user_data | Store user data for a job.
[**post_local_schedulers**](DefaultApi.md#post_local_schedulers) | **POST** /workflows/{workflow}/local_schedulers | Store a local compute node configuration.
[**post_resource_requirements**](DefaultApi.md#post_resource_requirements) | **POST** /workflows/{workflow}/resource_requirements | Store a resource requirements.
[**post_results**](DefaultApi.md#post_results) | **POST** /workflows/{workflow}/results | Store a result.
[**post_scheduled_compute_nodes**](DefaultApi.md#post_scheduled_compute_nodes) | **POST** /workflows/{workflow}/scheduled_compute_nodes | Store a scheduled compute node.
[**post_slurm_schedulers**](DefaultApi.md#post_slurm_schedulers) | **POST** /workflows/{workflow}/slurm_schedulers | Store a Slurm compute node configuration.
[**post_user_data**](DefaultApi.md#post_user_data) | **POST** /workflows/{workflow}/user_data | Store a user data.
[**post_workflow_specifications**](DefaultApi.md#post_workflow_specifications) | **POST** /workflow_specifications | Store a workflow.
[**post_workflows**](DefaultApi.md#post_workflows) | **POST** /workflows | Store a workflow.
[**post_workflows_key_auto_tune_resource_requirements**](DefaultApi.md#post_workflows_key_auto_tune_resource_requirements) | **POST** /workflows/{key}/auto_tune_resource_requirements | Enable workflow for auto-tuning resource requirements.
[**post_workflows_key_initialize_jobs**](DefaultApi.md#post_workflows_key_initialize_jobs) | **POST** /workflows/{key}/initialize_jobs | Initialize job relationships.
[**post_workflows_key_join_by_inbound_edge_collection_edge**](DefaultApi.md#post_workflows_key_join_by_inbound_edge_collection_edge) | **POST** /workflows/{key}/join_by_inbound_edge/{collection}/{edge} | Retrieve a joined table of two collections.
[**post_workflows_key_join_by_outbound_edge_collection_edge**](DefaultApi.md#post_workflows_key_join_by_outbound_edge_collection_edge) | **POST** /workflows/{key}/join_by_outbound_edge/{collection}/{edge} | Retrieve a joined table of two collections.
[**post_workflows_key_prepare_jobs_for_scheduling**](DefaultApi.md#post_workflows_key_prepare_jobs_for_scheduling) | **POST** /workflows/{key}/prepare_jobs_for_scheduling | Return scheduler IDs that need to be activated.
[**post_workflows_key_prepare_jobs_for_submission**](DefaultApi.md#post_workflows_key_prepare_jobs_for_submission) | **POST** /workflows/{key}/prepare_jobs_for_submission | Return ready jobs, accounting for resource requirements.
[**post_workflows_key_prepare_next_jobs_for_submission**](DefaultApi.md#post_workflows_key_prepare_next_jobs_for_submission) | **POST** /workflows/{key}/prepare_next_jobs_for_submission | Return user-requested number of ready jobs.
[**post_workflows_key_process_auto_tune_resource_requirements_results**](DefaultApi.md#post_workflows_key_process_auto_tune_resource_requirements_results) | **POST** /workflows/{key}/process_auto_tune_resource_requirements_results | Process the results of auto-tuning resource requirements.
[**post_workflows_key_process_changed_job_inputs**](DefaultApi.md#post_workflows_key_process_changed_job_inputs) | **POST** /workflows/{key}/process_changed_job_inputs | Check for changed job inputs and update status accordingly.
[**post_workflows_key_reset_job_status**](DefaultApi.md#post_workflows_key_reset_job_status) | **POST** /workflows/{key}/reset_job_status | Reset job status.
[**post_workflows_key_reset_status**](DefaultApi.md#post_workflows_key_reset_status) | **POST** /workflows/{key}/reset_status | Reset worklow status.
[**put_aws_schedulers_key**](DefaultApi.md#put_aws_schedulers_key) | **PUT** /workflows/{workflow}/aws_schedulers/{key} | Update AWS compute node configuration
[**put_compute_node_stats_key**](DefaultApi.md#put_compute_node_stats_key) | **PUT** /workflows/{workflow}/compute_node_stats/{key} | Update compute node statistics
[**put_compute_nodes_key**](DefaultApi.md#put_compute_nodes_key) | **PUT** /workflows/{workflow}/compute_nodes/{key} | Update compute node
[**put_events_key**](DefaultApi.md#put_events_key) | **PUT** /workflows/{workflow}/events/{key} | Update event
[**put_files_key**](DefaultApi.md#put_files_key) | **PUT** /workflows/{workflow}/files/{key} | Update file
[**put_job_process_stats_key**](DefaultApi.md#put_job_process_stats_key) | **PUT** /workflows/{workflow}/job_process_stats/{key} | Update job process statistics
[**put_jobs_key**](DefaultApi.md#put_jobs_key) | **PUT** /workflows/{workflow}/jobs/{key} | Update job
[**put_jobs_key_manage_status_change_status_rev_run_id**](DefaultApi.md#put_jobs_key_manage_status_change_status_rev_run_id) | **PUT** /workflows/{workflow}/jobs/{key}/manage_status_change/{status}/{rev}/{run_id} | Change the status of a job and manage side effects.
[**put_jobs_key_resource_requirements_rr_key**](DefaultApi.md#put_jobs_key_resource_requirements_rr_key) | **PUT** /workflows/{workflow}/jobs/{key}/resource_requirements/{rr_key} | Set the resource requirements for a job.
[**put_local_schedulers_key**](DefaultApi.md#put_local_schedulers_key) | **PUT** /workflows/{workflow}/local_schedulers/{key} | Update local compute node configuration
[**put_resource_requirements_key**](DefaultApi.md#put_resource_requirements_key) | **PUT** /workflows/{workflow}/resource_requirements/{key} | Update resource requirements
[**put_results_key**](DefaultApi.md#put_results_key) | **PUT** /workflows/{workflow}/results/{key} | Update result
[**put_scheduled_compute_nodes_key**](DefaultApi.md#put_scheduled_compute_nodes_key) | **PUT** /workflows/{workflow}/scheduled_compute_nodes/{key} | Update scheduled compute node
[**put_slurm_schedulers_key**](DefaultApi.md#put_slurm_schedulers_key) | **PUT** /workflows/{workflow}/slurm_schedulers/{key} | Update Slurm compute node configuration
[**put_user_data_key**](DefaultApi.md#put_user_data_key) | **PUT** /workflows/{workflow}/user_data/{key} | Update user data
[**put_workflows_key**](DefaultApi.md#put_workflows_key) | **PUT** /workflows/{key} | Update workflow
[**put_workflows_key_cancel**](DefaultApi.md#put_workflows_key_cancel) | **PUT** /workflows/{key}/cancel | Cancel workflow.
[**put_workflows_key_config**](DefaultApi.md#put_workflows_key_config) | **PUT** /workflows/{key}/config | Updates the workflow config.
[**put_workflows_key_status**](DefaultApi.md#put_workflows_key_status) | **PUT** /workflows/{key}/status | Reports the workflow status.


# **delete_workflows_key**
> delete_workflows_key(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> WorkflowsModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_key(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ WorkflowsModel }, OpenAPI.Clients.ApiResponse

Delete a workflow

Deletes a document from the \"workflows\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**WorkflowsModel**](WorkflowsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_aws_schedulers**
> delete_workflows_workflow_aws_schedulers(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_aws_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type AWS compute node configuration for a workflow

Delete all documents from the \"aws_schedulers\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_aws_schedulers_key**
> delete_workflows_workflow_aws_schedulers_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> AwsSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_aws_schedulers_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ AwsSchedulersModel }, OpenAPI.Clients.ApiResponse

Delete a document of type AWS compute node configuration

Deletes a document from the \"aws_schedulers\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the AWS compute node configuration document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**AwsSchedulersModel**](AwsSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_compute_node_stats**
> delete_workflows_workflow_compute_node_stats(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_compute_node_stats(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type compute node statistics for a workflow

Delete all documents from the \"compute_node_stats\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_compute_node_stats_key**
> delete_workflows_workflow_compute_node_stats_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> ComputeNodeStatsModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_compute_node_stats_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ ComputeNodeStatsModel }, OpenAPI.Clients.ApiResponse

Delete a document of type compute node statistics

Deletes a document from the \"compute_node_stats\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the compute node statistics document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**ComputeNodeStatsModel**](ComputeNodeStatsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_compute_nodes**
> delete_workflows_workflow_compute_nodes(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_compute_nodes(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type compute node for a workflow

Delete all documents from the \"compute_nodes\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_compute_nodes_key**
> delete_workflows_workflow_compute_nodes_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> ComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_compute_nodes_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ ComputeNodesModel }, OpenAPI.Clients.ApiResponse

Delete a document of type compute node

Deletes a document from the \"compute_nodes\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the compute node document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**ComputeNodesModel**](ComputeNodesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_edges_name**
> delete_workflows_workflow_edges_name(_api::DefaultApi, workflow::String, name::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_edges_name(_api::DefaultApi, response_stream::Channel, workflow::String, name::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all edges from the designated collection

Deletes all edges from the designated collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**name** | **String**| Edge collection name | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_edges_name_key**
> delete_workflows_workflow_edges_name_key(_api::DefaultApi, workflow::String, name::String, key::String; body=nothing, _mediaType=nothing) -> EdgesNameModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_edges_name_key(_api::DefaultApi, response_stream::Channel, workflow::String, name::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ EdgesNameModel }, OpenAPI.Clients.ApiResponse

Delete an edge

Deletes an edge from the designated collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**name** | **String**| Edge name. | [default to nothing]
**key** | **String**| Edge key. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**EdgesNameModel**](EdgesNameModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_events**
> delete_workflows_workflow_events(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_events(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type event for a workflow

Delete all documents from the \"events\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_events_key**
> delete_workflows_workflow_events_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_events_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete a document of type event

Deletes a document from the \"events\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the event document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_files**
> delete_workflows_workflow_files(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_files(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type file for a workflow

Delete all documents from the \"files\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_files_key**
> delete_workflows_workflow_files_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> FilesModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_files_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ FilesModel }, OpenAPI.Clients.ApiResponse

Delete a document of type file

Deletes a document from the \"files\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the file document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**FilesModel**](FilesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_job_process_stats**
> delete_workflows_workflow_job_process_stats(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_job_process_stats(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type job process statistics for a workflow

Delete all documents from the \"job_process_stats\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_job_process_stats_key**
> delete_workflows_workflow_job_process_stats_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> JobProcessStatsModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_job_process_stats_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ JobProcessStatsModel }, OpenAPI.Clients.ApiResponse

Delete a document of type job process statistics

Deletes a document from the \"job_process_stats\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the job process statistics document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**JobProcessStatsModel**](JobProcessStatsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_jobs**
> delete_workflows_workflow_jobs(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_jobs(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type job for a workflow

Delete all documents from the \"jobs\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_jobs_key**
> delete_workflows_workflow_jobs_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_jobs_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

Delete a document of type job

Deletes a document from the \"jobs\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the job document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**JobsModel**](JobsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_local_schedulers**
> delete_workflows_workflow_local_schedulers(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_local_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type local compute node configuration for a workflow

Delete all documents from the \"local_schedulers\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_local_schedulers_key**
> delete_workflows_workflow_local_schedulers_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> LocalSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_local_schedulers_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ LocalSchedulersModel }, OpenAPI.Clients.ApiResponse

Delete a document of type local compute node configuration

Deletes a document from the \"local_schedulers\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the local compute node configuration document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**LocalSchedulersModel**](LocalSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_resource_requirements**
> delete_workflows_workflow_resource_requirements(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type resource requirements for a workflow

Delete all documents from the \"resource_requirements\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_resource_requirements_key**
> delete_workflows_workflow_resource_requirements_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> ResourceRequirementsModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_resource_requirements_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ ResourceRequirementsModel }, OpenAPI.Clients.ApiResponse

Delete a document of type resource requirements

Deletes a document from the \"resource_requirements\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the resource requirements document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**ResourceRequirementsModel**](ResourceRequirementsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_results**
> delete_workflows_workflow_results(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_results(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type result for a workflow

Delete all documents from the \"results\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_results_key**
> delete_workflows_workflow_results_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> ResultsModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_results_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ ResultsModel }, OpenAPI.Clients.ApiResponse

Delete a document of type result

Deletes a document from the \"results\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the result document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**ResultsModel**](ResultsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_scheduled_compute_nodes**
> delete_workflows_workflow_scheduled_compute_nodes(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_scheduled_compute_nodes(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type scheduled compute node for a workflow

Delete all documents from the \"scheduled_compute_nodes\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_scheduled_compute_nodes_key**
> delete_workflows_workflow_scheduled_compute_nodes_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> ScheduledComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_scheduled_compute_nodes_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ ScheduledComputeNodesModel }, OpenAPI.Clients.ApiResponse

Delete a document of type scheduled compute node

Deletes a document from the \"scheduled_compute_nodes\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the scheduled compute node document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**ScheduledComputeNodesModel**](ScheduledComputeNodesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_slurm_schedulers**
> delete_workflows_workflow_slurm_schedulers(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_slurm_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type Slurm compute node configuration for a workflow

Delete all documents from the \"slurm_schedulers\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_slurm_schedulers_key**
> delete_workflows_workflow_slurm_schedulers_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> SlurmSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_slurm_schedulers_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ SlurmSchedulersModel }, OpenAPI.Clients.ApiResponse

Delete a document of type Slurm compute node configuration

Deletes a document from the \"slurm_schedulers\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the Slurm compute node configuration document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**SlurmSchedulersModel**](SlurmSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_user_data**
> delete_workflows_workflow_user_data(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_user_data(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Delete all documents of type user data for a workflow

Delete all documents from the \"user_data\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **delete_workflows_workflow_user_data_key**
> delete_workflows_workflow_user_data_key(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> UserDataModel, OpenAPI.Clients.ApiResponse <br/>
> delete_workflows_workflow_user_data_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ UserDataModel }, OpenAPI.Clients.ApiResponse

Delete a document of type user data

Deletes a document from the \"user_data\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the user data document. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**UserDataModel**](UserDataModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_aws_schedulers**
> get_aws_schedulers(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, _mediaType=nothing) -> GetAwsSchedulersResponse, OpenAPI.Clients.ApiResponse <br/>
> get_aws_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, _mediaType=nothing) -> Channel{ GetAwsSchedulersResponse }, OpenAPI.Clients.ApiResponse

Retrieve all AWS compute node configuration documents

Retrieve all documents from the \"aws_schedulers\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **name** | **String**|  | [default to nothing]

### Return type

[**GetAwsSchedulersResponse**](GetAwsSchedulersResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_aws_schedulers_key**
> get_aws_schedulers_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> AwsSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> get_aws_schedulers_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ AwsSchedulersModel }, OpenAPI.Clients.ApiResponse

Retrieve the AWS compute node configuration for a key.

Retrieve the document from the \"aws_schedulers\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the aws_schedulers document | [default to nothing]

### Return type

[**AwsSchedulersModel**](AwsSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_compute_node_stats**
> get_compute_node_stats(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, hostname=nothing, _mediaType=nothing) -> GetComputeNodeStatsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_compute_node_stats(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, hostname=nothing, _mediaType=nothing) -> Channel{ GetComputeNodeStatsResponse }, OpenAPI.Clients.ApiResponse

Retrieve all compute node statistics documents

Retrieve all documents from the \"compute_node_stats\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **hostname** | **String**|  | [default to nothing]

### Return type

[**GetComputeNodeStatsResponse**](GetComputeNodeStatsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_compute_node_stats_key**
> get_compute_node_stats_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ComputeNodeStatsModel, OpenAPI.Clients.ApiResponse <br/>
> get_compute_node_stats_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ComputeNodeStatsModel }, OpenAPI.Clients.ApiResponse

Retrieve the compute node statistics for a key.

Retrieve the document from the \"compute_node_stats\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the compute_node_stats document | [default to nothing]

### Return type

[**ComputeNodeStatsModel**](ComputeNodeStatsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_compute_nodes**
> get_compute_nodes(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, hostname=nothing, is_active=nothing, _mediaType=nothing) -> GetComputeNodesResponse, OpenAPI.Clients.ApiResponse <br/>
> get_compute_nodes(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, hostname=nothing, is_active=nothing, _mediaType=nothing) -> Channel{ GetComputeNodesResponse }, OpenAPI.Clients.ApiResponse

Retrieve all compute node documents

Retrieve all documents from the \"compute_nodes\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **hostname** | **String**|  | [default to nothing]
 **is_active** | **Bool**|  | [default to nothing]

### Return type

[**GetComputeNodesResponse**](GetComputeNodesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_compute_nodes_key**
> get_compute_nodes_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> get_compute_nodes_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ComputeNodesModel }, OpenAPI.Clients.ApiResponse

Retrieve the compute node for a key.

Retrieve the document from the \"compute_nodes\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the compute_nodes document | [default to nothing]

### Return type

[**ComputeNodesModel**](ComputeNodesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_edges_name**
> get_edges_name(_api::DefaultApi, workflow::String, name::String; skip=nothing, limit=nothing, _mediaType=nothing) -> GetEdgesNameResponse, OpenAPI.Clients.ApiResponse <br/>
> get_edges_name(_api::DefaultApi, response_stream::Channel, workflow::String, name::String; skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetEdgesNameResponse }, OpenAPI.Clients.ApiResponse

Retrieve all edges from the designated collection.

Retrieve all edges from the designated collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**name** | **String**| Edge collection name | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]

### Return type

[**GetEdgesNameResponse**](GetEdgesNameResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_edges_name_key**
> get_edges_name_key(_api::DefaultApi, workflow::String, name::String, key::String; _mediaType=nothing) -> EdgesNameModel, OpenAPI.Clients.ApiResponse <br/>
> get_edges_name_key(_api::DefaultApi, response_stream::Channel, workflow::String, name::String, key::String; _mediaType=nothing) -> Channel{ EdgesNameModel }, OpenAPI.Clients.ApiResponse

Retrieve an edge

Retrieves an edge from the designated collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**name** | **String**| Edge collection name | [default to nothing]
**key** | **String**| Edge key | [default to nothing]

### Return type

[**EdgesNameModel**](EdgesNameModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_events**
> get_events(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, category=nothing, _mediaType=nothing) -> GetEventsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_events(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, category=nothing, _mediaType=nothing) -> Channel{ GetEventsResponse }, OpenAPI.Clients.ApiResponse

Retrieve all event documents

Retrieve all documents from the \"events\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **category** | **String**|  | [default to nothing]

### Return type

[**GetEventsResponse**](GetEventsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_events_after_key**
> get_events_after_key(_api::DefaultApi, key::String, event_key::String; category=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> GetEventsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_events_after_key(_api::DefaultApi, response_stream::Channel, key::String, event_key::String; category=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetEventsResponse }, OpenAPI.Clients.ApiResponse

Return all events newer than the event with event_key.

Return all events newer than the event with event_key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]
**event_key** | **String**| Event key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category** | **String**|  | [default to &quot;null&quot;]
 **skip** | **Float64**| Ignored | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]

### Return type

[**GetEventsResponse**](GetEventsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_events_key**
> get_events_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> get_events_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Retrieve the event for a key.

Retrieve the document from the \"events\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the events document | [default to nothing]

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_files**
> get_files(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, path=nothing, _mediaType=nothing) -> GetFilesResponse, OpenAPI.Clients.ApiResponse <br/>
> get_files(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, path=nothing, _mediaType=nothing) -> Channel{ GetFilesResponse }, OpenAPI.Clients.ApiResponse

Retrieve all file documents

Retrieve all documents from the \"files\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **name** | **String**|  | [default to nothing]
 **path** | **String**|  | [default to nothing]

### Return type

[**GetFilesResponse**](GetFilesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_files_key**
> get_files_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> FilesModel, OpenAPI.Clients.ApiResponse <br/>
> get_files_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ FilesModel }, OpenAPI.Clients.ApiResponse

Retrieve the file for a key.

Retrieve the document from the \"files\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the files document | [default to nothing]

### Return type

[**FilesModel**](FilesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_files_produced_by_job_key**
> get_files_produced_by_job_key(_api::DefaultApi, workflow::String, key::String; skip=nothing, limit=nothing, _mediaType=nothing) -> GetFilesProducedByJobKeyResponse, OpenAPI.Clients.ApiResponse <br/>
> get_files_produced_by_job_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetFilesProducedByJobKeyResponse }, OpenAPI.Clients.ApiResponse

Retrieve files produced by a job

Retrieves files from the \"files\" collection produced by a job.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]

### Return type

[**GetFilesProducedByJobKeyResponse**](GetFilesProducedByJobKeyResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_job_keys**
> get_job_keys(_api::DefaultApi, workflow::String; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> get_job_keys(_api::DefaultApi, response_stream::Channel, workflow::String; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Retrieve all job keys for a workflow.

Retrieves all job keys from the \"jobs\" collection for a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_job_process_stats**
> get_job_process_stats(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, job_key=nothing, run_id=nothing, _mediaType=nothing) -> GetJobProcessStatsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_job_process_stats(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, job_key=nothing, run_id=nothing, _mediaType=nothing) -> Channel{ GetJobProcessStatsResponse }, OpenAPI.Clients.ApiResponse

Retrieve all job process statistics documents

Retrieve all documents from the \"job_process_stats\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **job_key** | **String**|  | [default to nothing]
 **run_id** | **Int64**|  | [default to nothing]

### Return type

[**GetJobProcessStatsResponse**](GetJobProcessStatsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_job_process_stats_key**
> get_job_process_stats_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> JobProcessStatsModel, OpenAPI.Clients.ApiResponse <br/>
> get_job_process_stats_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ JobProcessStatsModel }, OpenAPI.Clients.ApiResponse

Retrieve the job process statistics for a key.

Retrieve the document from the \"job_process_stats\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the job_process_stats document | [default to nothing]

### Return type

[**JobProcessStatsModel**](JobProcessStatsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_job_specifications**
> get_job_specifications(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, _mediaType=nothing) -> GetJobSpecificationsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_job_specifications(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetJobSpecificationsResponse }, OpenAPI.Clients.ApiResponse

Retrieve all job definitions

Retrieves all job definitions. Limit output with skip and limit.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]

### Return type

[**GetJobSpecificationsResponse**](GetJobSpecificationsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_job_specifications_key**
> get_job_specifications_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> JobSpecificationsModel, OpenAPI.Clients.ApiResponse <br/>
> get_job_specifications_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ JobSpecificationsModel }, OpenAPI.Clients.ApiResponse

Retrieve a job

Retrieves a job from the \"jobs\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]

### Return type

[**JobSpecificationsModel**](JobSpecificationsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_jobs**
> get_jobs(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, command=nothing, status=nothing, cancel_on_blocking_job_failure=nothing, supports_termination=nothing, _mediaType=nothing) -> GetJobsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_jobs(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, command=nothing, status=nothing, cancel_on_blocking_job_failure=nothing, supports_termination=nothing, _mediaType=nothing) -> Channel{ GetJobsResponse }, OpenAPI.Clients.ApiResponse

Retrieve all job documents

Retrieve all documents from the \"jobs\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **name** | **String**|  | [default to nothing]
 **command** | **String**|  | [default to nothing]
 **status** | **String**|  | [default to nothing]
 **cancel_on_blocking_job_failure** | **Bool**|  | [default to nothing]
 **supports_termination** | **Bool**|  | [default to nothing]

### Return type

[**GetJobsResponse**](GetJobsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_jobs_find_by_needs_file_key**
> get_jobs_find_by_needs_file_key(_api::DefaultApi, workflow::String, key::String; skip=nothing, limit=nothing, _mediaType=nothing) -> GetJobsFindByNeedsFileKeyResponse, OpenAPI.Clients.ApiResponse <br/>
> get_jobs_find_by_needs_file_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetJobsFindByNeedsFileKeyResponse }, OpenAPI.Clients.ApiResponse

Retrieve all jobs that need a file

Retrieves all jobs connected to a file by the needs edge.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| File key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]

### Return type

[**GetJobsFindByNeedsFileKeyResponse**](GetJobsFindByNeedsFileKeyResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_jobs_find_by_status_status**
> get_jobs_find_by_status_status(_api::DefaultApi, workflow::String, status::String; skip=nothing, limit=nothing, _mediaType=nothing) -> GetJobsFindByStatusStatusResponse, OpenAPI.Clients.ApiResponse <br/>
> get_jobs_find_by_status_status(_api::DefaultApi, response_stream::Channel, workflow::String, status::String; skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetJobsFindByStatusStatusResponse }, OpenAPI.Clients.ApiResponse

Retrieve all jobs with a specific status

Retrieves all jobs from the \"jobs\" collection with a specific status.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**status** | **String**| Job status. | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]

### Return type

[**GetJobsFindByStatusStatusResponse**](GetJobsFindByStatusStatusResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_jobs_key**
> get_jobs_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> get_jobs_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

Retrieve the job for a key.

Retrieve the document from the \"jobs\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the jobs document | [default to nothing]

### Return type

[**JobsModel**](JobsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_jobs_key_process_stats**
> get_jobs_key_process_stats(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> Vector{JobProcessStatsModel}, OpenAPI.Clients.ApiResponse <br/>
> get_jobs_key_process_stats(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ Vector{JobProcessStatsModel} }, OpenAPI.Clients.ApiResponse

Retrieve the job process stats for a job.

Retrieve the job process stats for a job by its key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]

### Return type

[**Vector{JobProcessStatsModel}**](JobProcessStatsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_jobs_key_resource_requirements**
> get_jobs_key_resource_requirements(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ResourceRequirementsModel, OpenAPI.Clients.ApiResponse <br/>
> get_jobs_key_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ResourceRequirementsModel }, OpenAPI.Clients.ApiResponse

Retrieve the resource requirements for a job.

Retrieve the resource requirements for a job by its key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]

### Return type

[**ResourceRequirementsModel**](ResourceRequirementsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_jobs_key_user_data_consumes**
> get_jobs_key_user_data_consumes(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> GetJobsKeyUserDataConsumesResponse, OpenAPI.Clients.ApiResponse <br/>
> get_jobs_key_user_data_consumes(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ GetJobsKeyUserDataConsumesResponse }, OpenAPI.Clients.ApiResponse

Retrieve all user data consumed by a job.

Retrieve all user data consumed by a job.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]

### Return type

[**GetJobsKeyUserDataConsumesResponse**](GetJobsKeyUserDataConsumesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_jobs_key_user_data_stores**
> get_jobs_key_user_data_stores(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> GetJobsKeyUserDataStoresResponse, OpenAPI.Clients.ApiResponse <br/>
> get_jobs_key_user_data_stores(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ GetJobsKeyUserDataStoresResponse }, OpenAPI.Clients.ApiResponse

Retrieve all user data for a job.

Retrieve all user data for a job.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]

### Return type

[**GetJobsKeyUserDataStoresResponse**](GetJobsKeyUserDataStoresResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_latest_event_key**
> get_latest_event_key(_api::DefaultApi, key::String; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> get_latest_event_key(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Return the key of the latest event.

Return the key of the latest event.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_local_schedulers**
> get_local_schedulers(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, memory=nothing, num_cpus=nothing, _mediaType=nothing) -> GetLocalSchedulersResponse, OpenAPI.Clients.ApiResponse <br/>
> get_local_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, memory=nothing, num_cpus=nothing, _mediaType=nothing) -> Channel{ GetLocalSchedulersResponse }, OpenAPI.Clients.ApiResponse

Retrieve all local compute node configuration documents

Retrieve all documents from the \"local_schedulers\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **memory** | **String**|  | [default to nothing]
 **num_cpus** | **Int64**|  | [default to nothing]

### Return type

[**GetLocalSchedulersResponse**](GetLocalSchedulersResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_local_schedulers_key**
> get_local_schedulers_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> LocalSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> get_local_schedulers_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ LocalSchedulersModel }, OpenAPI.Clients.ApiResponse

Retrieve the local compute node configuration for a key.

Retrieve the document from the \"local_schedulers\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the local_schedulers document | [default to nothing]

### Return type

[**LocalSchedulersModel**](LocalSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_ping**
> get_ping(_api::DefaultApi; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> get_ping(_api::DefaultApi, response_stream::Channel; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Check if the service is running.

Check if the service is running.

### Required Parameters
This endpoint does not need any parameter.

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_resource_requirements**
> get_resource_requirements(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, memory=nothing, num_cpus=nothing, num_gpus=nothing, num_nodes=nothing, runtime=nothing, _mediaType=nothing) -> GetResourceRequirementsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, memory=nothing, num_cpus=nothing, num_gpus=nothing, num_nodes=nothing, runtime=nothing, _mediaType=nothing) -> Channel{ GetResourceRequirementsResponse }, OpenAPI.Clients.ApiResponse

Retrieve all resource requirements documents

Retrieve all documents from the \"resource_requirements\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **name** | **String**|  | [default to nothing]
 **memory** | **String**|  | [default to nothing]
 **num_cpus** | **Int64**|  | [default to nothing]
 **num_gpus** | **Int64**|  | [default to nothing]
 **num_nodes** | **Int64**|  | [default to nothing]
 **runtime** | **String**|  | [default to nothing]

### Return type

[**GetResourceRequirementsResponse**](GetResourceRequirementsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_resource_requirements_key**
> get_resource_requirements_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ResourceRequirementsModel, OpenAPI.Clients.ApiResponse <br/>
> get_resource_requirements_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ResourceRequirementsModel }, OpenAPI.Clients.ApiResponse

Retrieve the resource requirements for a key.

Retrieve the document from the \"resource_requirements\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the resource_requirements document | [default to nothing]

### Return type

[**ResourceRequirementsModel**](ResourceRequirementsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_results**
> get_results(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, job_key=nothing, run_id=nothing, return_code=nothing, status=nothing, _mediaType=nothing) -> GetResultsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_results(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, job_key=nothing, run_id=nothing, return_code=nothing, status=nothing, _mediaType=nothing) -> Channel{ GetResultsResponse }, OpenAPI.Clients.ApiResponse

Retrieve all result documents

Retrieve all documents from the \"results\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **job_key** | **String**|  | [default to nothing]
 **run_id** | **Int64**|  | [default to nothing]
 **return_code** | **Int64**|  | [default to nothing]
 **status** | **String**|  | [default to nothing]

### Return type

[**GetResultsResponse**](GetResultsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_results_find_by_job_key**
> get_results_find_by_job_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ResultsModel, OpenAPI.Clients.ApiResponse <br/>
> get_results_find_by_job_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ResultsModel }, OpenAPI.Clients.ApiResponse

Retrieve the latest result for a job

Retrieve the latest result for a job. Throws an error if no result is stored.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]

### Return type

[**ResultsModel**](ResultsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_results_key**
> get_results_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ResultsModel, OpenAPI.Clients.ApiResponse <br/>
> get_results_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ResultsModel }, OpenAPI.Clients.ApiResponse

Retrieve the result for a key.

Retrieve the document from the \"results\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the results document | [default to nothing]

### Return type

[**ResultsModel**](ResultsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_scheduled_compute_nodes**
> get_scheduled_compute_nodes(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, scheduler_id=nothing, scheduler_config_id=nothing, status=nothing, _mediaType=nothing) -> GetScheduledComputeNodesResponse, OpenAPI.Clients.ApiResponse <br/>
> get_scheduled_compute_nodes(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, scheduler_id=nothing, scheduler_config_id=nothing, status=nothing, _mediaType=nothing) -> Channel{ GetScheduledComputeNodesResponse }, OpenAPI.Clients.ApiResponse

Retrieve all scheduled compute node documents

Retrieve all documents from the \"scheduled_compute_nodes\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **scheduler_id** | **String**|  | [default to nothing]
 **scheduler_config_id** | **String**|  | [default to nothing]
 **status** | **String**|  | [default to nothing]

### Return type

[**GetScheduledComputeNodesResponse**](GetScheduledComputeNodesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_scheduled_compute_nodes_key**
> get_scheduled_compute_nodes_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ScheduledComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> get_scheduled_compute_nodes_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ScheduledComputeNodesModel }, OpenAPI.Clients.ApiResponse

Retrieve the scheduled compute node for a key.

Retrieve the document from the \"scheduled_compute_nodes\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the scheduled_compute_nodes document | [default to nothing]

### Return type

[**ScheduledComputeNodesModel**](ScheduledComputeNodesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_slurm_schedulers**
> get_slurm_schedulers(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, account=nothing, gres=nothing, mem=nothing, nodes=nothing, partition=nothing, qos=nothing, tmp=nothing, walltime=nothing, _mediaType=nothing) -> GetSlurmSchedulersResponse, OpenAPI.Clients.ApiResponse <br/>
> get_slurm_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, account=nothing, gres=nothing, mem=nothing, nodes=nothing, partition=nothing, qos=nothing, tmp=nothing, walltime=nothing, _mediaType=nothing) -> Channel{ GetSlurmSchedulersResponse }, OpenAPI.Clients.ApiResponse

Retrieve all Slurm compute node configuration documents

Retrieve all documents from the \"slurm_schedulers\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **name** | **String**|  | [default to nothing]
 **account** | **String**|  | [default to nothing]
 **gres** | **String**|  | [default to nothing]
 **mem** | **String**|  | [default to nothing]
 **nodes** | **Int64**|  | [default to nothing]
 **partition** | **String**|  | [default to nothing]
 **qos** | **String**|  | [default to nothing]
 **tmp** | **String**|  | [default to nothing]
 **walltime** | **String**|  | [default to nothing]

### Return type

[**GetSlurmSchedulersResponse**](GetSlurmSchedulersResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_slurm_schedulers_key**
> get_slurm_schedulers_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> SlurmSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> get_slurm_schedulers_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ SlurmSchedulersModel }, OpenAPI.Clients.ApiResponse

Retrieve the Slurm compute node configuration for a key.

Retrieve the document from the \"slurm_schedulers\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the slurm_schedulers document | [default to nothing]

### Return type

[**SlurmSchedulersModel**](SlurmSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_user_data**
> get_user_data(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, is_ephemeral=nothing, _mediaType=nothing) -> GetUserDataResponse, OpenAPI.Clients.ApiResponse <br/>
> get_user_data(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, is_ephemeral=nothing, _mediaType=nothing) -> Channel{ GetUserDataResponse }, OpenAPI.Clients.ApiResponse

Retrieve all user data documents

Retrieve all documents from the \"user_data\" collection for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **key** | **String**|  | [default to nothing]
 **name** | **String**|  | [default to nothing]
 **is_ephemeral** | **Bool**|  | [default to nothing]

### Return type

[**GetUserDataResponse**](GetUserDataResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_user_data_key**
> get_user_data_key(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> UserDataModel, OpenAPI.Clients.ApiResponse <br/>
> get_user_data_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ UserDataModel }, OpenAPI.Clients.ApiResponse

Retrieve the user data for a key.

Retrieve the document from the \"user_data\" collection by key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| key of the user_data document | [default to nothing]

### Return type

[**UserDataModel**](UserDataModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_version**
> get_version(_api::DefaultApi; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> get_version(_api::DefaultApi, response_stream::Channel; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Return the version of the service.

Return the version of the service.

### Required Parameters
This endpoint does not need any parameter.

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflow_specifications_example**
> get_workflow_specifications_example(_api::DefaultApi; _mediaType=nothing) -> WorkflowSpecificationsModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflow_specifications_example(_api::DefaultApi, response_stream::Channel; _mediaType=nothing) -> Channel{ WorkflowSpecificationsModel }, OpenAPI.Clients.ApiResponse

Retrieve an example workflow specification

Retrieves an example workflow specification in JSON format.

### Required Parameters
This endpoint does not need any parameter.

### Return type

[**WorkflowSpecificationsModel**](WorkflowSpecificationsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflow_specifications_key**
> get_workflow_specifications_key(_api::DefaultApi, key::String; _mediaType=nothing) -> WorkflowSpecificationsModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflow_specifications_key(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ WorkflowSpecificationsModel }, OpenAPI.Clients.ApiResponse

Retrieve the current workflow

Retrieves the current workflow in JSON format.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| key of the workflow. | [default to nothing]

### Return type

[**WorkflowSpecificationsModel**](WorkflowSpecificationsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflow_specifications_template**
> get_workflow_specifications_template(_api::DefaultApi; _mediaType=nothing) -> WorkflowSpecificationsModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflow_specifications_template(_api::DefaultApi, response_stream::Channel; _mediaType=nothing) -> Channel{ WorkflowSpecificationsModel }, OpenAPI.Clients.ApiResponse

Retrieve the workflow specification template

Retrieve the workflow specification template in JSON format.

### Required Parameters
This endpoint does not need any parameter.

### Return type

[**WorkflowSpecificationsModel**](WorkflowSpecificationsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflows**
> get_workflows(_api::DefaultApi; skip=nothing, sort_by=nothing, reverse_sort=nothing, limit=nothing, name=nothing, user=nothing, description=nothing, _mediaType=nothing) -> GetWorkflowsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_workflows(_api::DefaultApi, response_stream::Channel; skip=nothing, sort_by=nothing, reverse_sort=nothing, limit=nothing, name=nothing, user=nothing, description=nothing, _mediaType=nothing) -> Channel{ GetWorkflowsResponse }, OpenAPI.Clients.ApiResponse

Retrieve all workflows

Retrieves all documents from the \"workflows\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **Float64**|  | [default to 0.0]
 **sort_by** | **String**|  | [default to &quot;null&quot;]
 **reverse_sort** | **Bool**|  | [default to false]
 **limit** | **Float64**|  | [default to 100000.0]
 **name** | **String**|  | [default to nothing]
 **user** | **String**|  | [default to nothing]
 **description** | **String**|  | [default to nothing]

### Return type

[**GetWorkflowsResponse**](GetWorkflowsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflows_key**
> get_workflows_key(_api::DefaultApi, key::String; _mediaType=nothing) -> WorkflowsModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflows_key(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ WorkflowsModel }, OpenAPI.Clients.ApiResponse

Retrieve the workflow for an key.

Retrieve the document for a key from the \"workflows\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| key of the workflows document | [default to nothing]

### Return type

[**WorkflowsModel**](WorkflowsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflows_key_collection_names**
> get_workflows_key_collection_names(_api::DefaultApi, key::String; _mediaType=nothing) -> GetWorkflowsKeyCollectionNamesResponse, OpenAPI.Clients.ApiResponse <br/>
> get_workflows_key_collection_names(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ GetWorkflowsKeyCollectionNamesResponse }, OpenAPI.Clients.ApiResponse

Retrieve all collection names for one workflow.

Retrieve all collection names for one workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Return type

[**GetWorkflowsKeyCollectionNamesResponse**](GetWorkflowsKeyCollectionNamesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflows_key_config**
> get_workflows_key_config(_api::DefaultApi, key::String; _mediaType=nothing) -> WorkflowConfigModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflows_key_config(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ WorkflowConfigModel }, OpenAPI.Clients.ApiResponse

Returns the workflow config.

Returns the workflow config.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Return type

[**WorkflowConfigModel**](WorkflowConfigModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflows_key_dot_graph_name**
> get_workflows_key_dot_graph_name(_api::DefaultApi, key::String, name::String; _mediaType=nothing) -> GetWorkflowsKeyDotGraphNameResponse, OpenAPI.Clients.ApiResponse <br/>
> get_workflows_key_dot_graph_name(_api::DefaultApi, response_stream::Channel, key::String, name::String; _mediaType=nothing) -> Channel{ GetWorkflowsKeyDotGraphNameResponse }, OpenAPI.Clients.ApiResponse

Build a string for a DOT graph.

Build a string for a DOT graph.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]
**name** | **String**| Graph name | [default to nothing]

### Return type

[**GetWorkflowsKeyDotGraphNameResponse**](GetWorkflowsKeyDotGraphNameResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflows_key_is_complete**
> get_workflows_key_is_complete(_api::DefaultApi, key::String; _mediaType=nothing) -> GetWorkflowsKeyIsCompleteResponse, OpenAPI.Clients.ApiResponse <br/>
> get_workflows_key_is_complete(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ GetWorkflowsKeyIsCompleteResponse }, OpenAPI.Clients.ApiResponse

Report whether the workflow is complete

Reports true if all jobs in the workflow are complete.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Return type

[**GetWorkflowsKeyIsCompleteResponse**](GetWorkflowsKeyIsCompleteResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflows_key_missing_user_data**
> get_workflows_key_missing_user_data(_api::DefaultApi, key::String; _mediaType=nothing) -> GetWorkflowsKeyMissingUserDataResponse, OpenAPI.Clients.ApiResponse <br/>
> get_workflows_key_missing_user_data(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ GetWorkflowsKeyMissingUserDataResponse }, OpenAPI.Clients.ApiResponse

List missing user data that should exist.

List missing user data that should exist.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Return type

[**GetWorkflowsKeyMissingUserDataResponse**](GetWorkflowsKeyMissingUserDataResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflows_key_ready_job_requirements**
> get_workflows_key_ready_job_requirements(_api::DefaultApi, key::String; scheduler_config_id=nothing, _mediaType=nothing) -> GetWorkflowsKeyReadyJobRequirementsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_workflows_key_ready_job_requirements(_api::DefaultApi, response_stream::Channel, key::String; scheduler_config_id=nothing, _mediaType=nothing) -> Channel{ GetWorkflowsKeyReadyJobRequirementsResponse }, OpenAPI.Clients.ApiResponse

Return the resource requirements for ready jobs.

Return the resource requirements for jobs with a status of ready.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scheduler_config_id** | **String**| Limit output to jobs assigned this scheduler. | [default to nothing]

### Return type

[**GetWorkflowsKeyReadyJobRequirementsResponse**](GetWorkflowsKeyReadyJobRequirementsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflows_key_required_existing_files**
> get_workflows_key_required_existing_files(_api::DefaultApi, key::String; _mediaType=nothing) -> GetWorkflowsKeyRequiredExistingFilesResponse, OpenAPI.Clients.ApiResponse <br/>
> get_workflows_key_required_existing_files(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ GetWorkflowsKeyRequiredExistingFilesResponse }, OpenAPI.Clients.ApiResponse

List files that must exist.

List files that must exist.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Return type

[**GetWorkflowsKeyRequiredExistingFilesResponse**](GetWorkflowsKeyRequiredExistingFilesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_workflows_key_status**
> get_workflows_key_status(_api::DefaultApi, key::String; _mediaType=nothing) -> WorkflowStatusModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflows_key_status(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ WorkflowStatusModel }, OpenAPI.Clients.ApiResponse

Reports the workflow status.

Reports the workflow status.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Return type

[**WorkflowStatusModel**](WorkflowStatusModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_aws_schedulers**
> post_aws_schedulers(_api::DefaultApi, workflow::String, body::AwsSchedulersModel; _mediaType=nothing) -> AwsSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> post_aws_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String, body::AwsSchedulersModel; _mediaType=nothing) -> Channel{ AwsSchedulersModel }, OpenAPI.Clients.ApiResponse

Store a AWS compute node configuration.

Store a AWS compute node configuration in the \"aws_schedulers\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**AwsSchedulersModel**](AwsSchedulersModel.md)| AWS compute node configuration. | 

### Return type

[**AwsSchedulersModel**](AwsSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_bulk_jobs**
> post_bulk_jobs(_api::DefaultApi, workflow::String, body::BulkJobsModel; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> post_bulk_jobs(_api::DefaultApi, response_stream::Channel, workflow::String, body::BulkJobsModel; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Add jobs in bulk with edge definitions.

Add jobs in bulk with edge definitions. Recommended max job count of 10,000.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**BulkJobsModel**](BulkJobsModel.md)|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_compute_node_stats**
> post_compute_node_stats(_api::DefaultApi, workflow::String, body::ComputeNodeStatsModel; _mediaType=nothing) -> ComputeNodeStatsModel, OpenAPI.Clients.ApiResponse <br/>
> post_compute_node_stats(_api::DefaultApi, response_stream::Channel, workflow::String, body::ComputeNodeStatsModel; _mediaType=nothing) -> Channel{ ComputeNodeStatsModel }, OpenAPI.Clients.ApiResponse

Store a compute node statistics.

Store a compute node statistics in the \"compute_node_stats\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**ComputeNodeStatsModel**](ComputeNodeStatsModel.md)| compute node statistics. | 

### Return type

[**ComputeNodeStatsModel**](ComputeNodeStatsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_compute_nodes**
> post_compute_nodes(_api::DefaultApi, workflow::String, body::ComputeNodesModel; _mediaType=nothing) -> ComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> post_compute_nodes(_api::DefaultApi, response_stream::Channel, workflow::String, body::ComputeNodesModel; _mediaType=nothing) -> Channel{ ComputeNodesModel }, OpenAPI.Clients.ApiResponse

Store a compute node.

Store a compute node in the \"compute_nodes\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**ComputeNodesModel**](ComputeNodesModel.md)| compute node. | 

### Return type

[**ComputeNodesModel**](ComputeNodesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_edges_name**
> post_edges_name(_api::DefaultApi, workflow::String, name::String, body::EdgesNameModel; _mediaType=nothing) -> EdgesNameModel, OpenAPI.Clients.ApiResponse <br/>
> post_edges_name(_api::DefaultApi, response_stream::Channel, workflow::String, name::String, body::EdgesNameModel; _mediaType=nothing) -> Channel{ EdgesNameModel }, OpenAPI.Clients.ApiResponse

Store an edge between two vertexes.

Store an edge between two vertexes in the designated collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**name** | **String**| Edge name | [default to nothing]
**body** | [**EdgesNameModel**](EdgesNameModel.md)| Relationship between two vertexes | 

### Return type

[**EdgesNameModel**](EdgesNameModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_events**
> post_events(_api::DefaultApi, workflow::String, body::Any; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> post_events(_api::DefaultApi, response_stream::Channel, workflow::String, body::Any; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Store a event.

Store a event in the \"events\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | **Any**| event. | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_files**
> post_files(_api::DefaultApi, workflow::String, body::FilesModel; _mediaType=nothing) -> FilesModel, OpenAPI.Clients.ApiResponse <br/>
> post_files(_api::DefaultApi, response_stream::Channel, workflow::String, body::FilesModel; _mediaType=nothing) -> Channel{ FilesModel }, OpenAPI.Clients.ApiResponse

Store a file.

Store a file in the \"files\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**FilesModel**](FilesModel.md)| file. | 

### Return type

[**FilesModel**](FilesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_job_process_stats**
> post_job_process_stats(_api::DefaultApi, workflow::String, body::JobProcessStatsModel; _mediaType=nothing) -> JobProcessStatsModel, OpenAPI.Clients.ApiResponse <br/>
> post_job_process_stats(_api::DefaultApi, response_stream::Channel, workflow::String, body::JobProcessStatsModel; _mediaType=nothing) -> Channel{ JobProcessStatsModel }, OpenAPI.Clients.ApiResponse

Store a job process statistics.

Store a job process statistics in the \"job_process_stats\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**JobProcessStatsModel**](JobProcessStatsModel.md)| job process statistics. | 

### Return type

[**JobProcessStatsModel**](JobProcessStatsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_job_specifications**
> post_job_specifications(_api::DefaultApi, workflow::String, body::JobSpecificationsModel; _mediaType=nothing) -> JobSpecificationsModel, OpenAPI.Clients.ApiResponse <br/>
> post_job_specifications(_api::DefaultApi, response_stream::Channel, workflow::String, body::JobSpecificationsModel; _mediaType=nothing) -> Channel{ JobSpecificationsModel }, OpenAPI.Clients.ApiResponse

Store a job and create edges.

Store a job in the \"jobs\" collection and create edges.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**JobSpecificationsModel**](JobSpecificationsModel.md)| job definition to store in the collection. | 

### Return type

[**JobSpecificationsModel**](JobSpecificationsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_jobs**
> post_jobs(_api::DefaultApi, workflow::String, body::JobsModel; _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> post_jobs(_api::DefaultApi, response_stream::Channel, workflow::String, body::JobsModel; _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

Store a job.

Store a job in the \"jobs\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**JobsModel**](JobsModel.md)| job. | 

### Return type

[**JobsModel**](JobsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_jobs_key_complete_job_status_rev_run_id**
> post_jobs_key_complete_job_status_rev_run_id(_api::DefaultApi, workflow::String, key::String, status::String, rev::String, run_id::Int64, body::ResultsModel; _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> post_jobs_key_complete_job_status_rev_run_id(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, status::String, rev::String, run_id::Int64, body::ResultsModel; _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

Complete a job and add a result.

Complete a job, connect it to a result, and manage side effects.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]
**status** | **String**| New job status. | [default to nothing]
**rev** | **String**| Current job revision. | [default to nothing]
**run_id** | **Int64**| Current job run ID | [default to nothing]
**body** | [**ResultsModel**](ResultsModel.md)| Result of the job. | 

### Return type

[**JobsModel**](JobsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_jobs_key_user_data**
> post_jobs_key_user_data(_api::DefaultApi, workflow::String, key::String, body::UserDataModel; _mediaType=nothing) -> UserDataModel, OpenAPI.Clients.ApiResponse <br/>
> post_jobs_key_user_data(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::UserDataModel; _mediaType=nothing) -> Channel{ UserDataModel }, OpenAPI.Clients.ApiResponse

Store user data for a job.

Store user data for a job and connect the two vertexes.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]
**body** | [**UserDataModel**](UserDataModel.md)| User data for the job. | 

### Return type

[**UserDataModel**](UserDataModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_local_schedulers**
> post_local_schedulers(_api::DefaultApi, workflow::String, body::LocalSchedulersModel; _mediaType=nothing) -> LocalSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> post_local_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String, body::LocalSchedulersModel; _mediaType=nothing) -> Channel{ LocalSchedulersModel }, OpenAPI.Clients.ApiResponse

Store a local compute node configuration.

Store a local compute node configuration in the \"local_schedulers\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**LocalSchedulersModel**](LocalSchedulersModel.md)| local compute node configuration. | 

### Return type

[**LocalSchedulersModel**](LocalSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_resource_requirements**
> post_resource_requirements(_api::DefaultApi, workflow::String, body::ResourceRequirementsModel; _mediaType=nothing) -> ResourceRequirementsModel, OpenAPI.Clients.ApiResponse <br/>
> post_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String, body::ResourceRequirementsModel; _mediaType=nothing) -> Channel{ ResourceRequirementsModel }, OpenAPI.Clients.ApiResponse

Store a resource requirements.

Store a resource requirements in the \"resource_requirements\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**ResourceRequirementsModel**](ResourceRequirementsModel.md)| resource requirements. | 

### Return type

[**ResourceRequirementsModel**](ResourceRequirementsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_results**
> post_results(_api::DefaultApi, workflow::String, body::ResultsModel; _mediaType=nothing) -> ResultsModel, OpenAPI.Clients.ApiResponse <br/>
> post_results(_api::DefaultApi, response_stream::Channel, workflow::String, body::ResultsModel; _mediaType=nothing) -> Channel{ ResultsModel }, OpenAPI.Clients.ApiResponse

Store a result.

Store a result in the \"results\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**ResultsModel**](ResultsModel.md)| result. | 

### Return type

[**ResultsModel**](ResultsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_scheduled_compute_nodes**
> post_scheduled_compute_nodes(_api::DefaultApi, workflow::String, body::ScheduledComputeNodesModel; _mediaType=nothing) -> ScheduledComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> post_scheduled_compute_nodes(_api::DefaultApi, response_stream::Channel, workflow::String, body::ScheduledComputeNodesModel; _mediaType=nothing) -> Channel{ ScheduledComputeNodesModel }, OpenAPI.Clients.ApiResponse

Store a scheduled compute node.

Store a scheduled compute node in the \"scheduled_compute_nodes\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**ScheduledComputeNodesModel**](ScheduledComputeNodesModel.md)| scheduled compute node. | 

### Return type

[**ScheduledComputeNodesModel**](ScheduledComputeNodesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_slurm_schedulers**
> post_slurm_schedulers(_api::DefaultApi, workflow::String, body::SlurmSchedulersModel; _mediaType=nothing) -> SlurmSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> post_slurm_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String, body::SlurmSchedulersModel; _mediaType=nothing) -> Channel{ SlurmSchedulersModel }, OpenAPI.Clients.ApiResponse

Store a Slurm compute node configuration.

Store a Slurm compute node configuration in the \"slurm_schedulers\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**SlurmSchedulersModel**](SlurmSchedulersModel.md)| Slurm compute node configuration. | 

### Return type

[**SlurmSchedulersModel**](SlurmSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_user_data**
> post_user_data(_api::DefaultApi, workflow::String, body::UserDataModel; _mediaType=nothing) -> UserDataModel, OpenAPI.Clients.ApiResponse <br/>
> post_user_data(_api::DefaultApi, response_stream::Channel, workflow::String, body::UserDataModel; _mediaType=nothing) -> Channel{ UserDataModel }, OpenAPI.Clients.ApiResponse

Store a user data.

Store a user data in the \"user_data\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**UserDataModel**](UserDataModel.md)| user data. | 

### Return type

[**UserDataModel**](UserDataModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflow_specifications**
> post_workflow_specifications(_api::DefaultApi, body::WorkflowSpecificationsModel; _mediaType=nothing) -> WorkflowsModel, OpenAPI.Clients.ApiResponse <br/>
> post_workflow_specifications(_api::DefaultApi, response_stream::Channel, body::WorkflowSpecificationsModel; _mediaType=nothing) -> Channel{ WorkflowsModel }, OpenAPI.Clients.ApiResponse

Store a workflow.

Store a workflow.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**body** | [**WorkflowSpecificationsModel**](WorkflowSpecificationsModel.md)| New workflow | 

### Return type

[**WorkflowsModel**](WorkflowsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows**
> post_workflows(_api::DefaultApi, body::WorkflowsModel; _mediaType=nothing) -> WorkflowsModel, OpenAPI.Clients.ApiResponse <br/>
> post_workflows(_api::DefaultApi, response_stream::Channel, body::WorkflowsModel; _mediaType=nothing) -> Channel{ WorkflowsModel }, OpenAPI.Clients.ApiResponse

Store a workflow.

Store a workflow in the \"workflows\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**body** | [**WorkflowsModel**](WorkflowsModel.md)| Collection of jobs and dependent resources. | 

### Return type

[**WorkflowsModel**](WorkflowsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_auto_tune_resource_requirements**
> post_workflows_key_auto_tune_resource_requirements(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_auto_tune_resource_requirements(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Enable workflow for auto-tuning resource requirements.

Enable workflow for auto-tuning resource requirements.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_initialize_jobs**
> post_workflows_key_initialize_jobs(_api::DefaultApi, key::String; only_uninitialized=nothing, clear_ephemeral_user_data=nothing, body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_initialize_jobs(_api::DefaultApi, response_stream::Channel, key::String; only_uninitialized=nothing, clear_ephemeral_user_data=nothing, body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Initialize job relationships.

Initialize job relationships based on file and user_data relationships.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **only_uninitialized** | **Bool**| Only initialize jobs with a status of uninitialized. | [default to false]
 **clear_ephemeral_user_data** | **Bool**| Clear all ephemeral user data. | [default to true]
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_join_by_inbound_edge_collection_edge**
> post_workflows_key_join_by_inbound_edge_collection_edge(_api::DefaultApi, key::String, collection::String, edge::String, body::Any; collection_key=nothing, collection_name=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> PostWorkflowsKeyJoinByInboundEdgeCollectionEdgeResponse, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_join_by_inbound_edge_collection_edge(_api::DefaultApi, response_stream::Channel, key::String, collection::String, edge::String, body::Any; collection_key=nothing, collection_name=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyJoinByInboundEdgeCollectionEdgeResponse }, OpenAPI.Clients.ApiResponse

Retrieve a joined table of two collections.

Retrieve a table of the collections joined by an inbound edge.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]
**collection** | **String**| From collection | [default to nothing]
**edge** | **String**| Edge name | [default to nothing]
**body** | **Any**| Filters for query | 

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_key** | **String**|  | [default to nothing]
 **collection_name** | **String**|  | [default to nothing]
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]

### Return type

[**PostWorkflowsKeyJoinByInboundEdgeCollectionEdgeResponse**](PostWorkflowsKeyJoinByInboundEdgeCollectionEdgeResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_join_by_outbound_edge_collection_edge**
> post_workflows_key_join_by_outbound_edge_collection_edge(_api::DefaultApi, key::String, collection::String, edge::String, body::Any; collection_key=nothing, collection_name=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> PostWorkflowsKeyJoinByOutboundEdgeCollectionEdgeResponse, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_join_by_outbound_edge_collection_edge(_api::DefaultApi, response_stream::Channel, key::String, collection::String, edge::String, body::Any; collection_key=nothing, collection_name=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyJoinByOutboundEdgeCollectionEdgeResponse }, OpenAPI.Clients.ApiResponse

Retrieve a joined table of two collections.

Retrieve a table of the collections joined by an outbound edge.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]
**collection** | **String**| From collection | [default to nothing]
**edge** | **String**| Edge name | [default to nothing]
**body** | **Any**| Filters for query | 

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_key** | **String**|  | [default to nothing]
 **collection_name** | **String**|  | [default to nothing]
 **skip** | **Float64**|  | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]

### Return type

[**PostWorkflowsKeyJoinByOutboundEdgeCollectionEdgeResponse**](PostWorkflowsKeyJoinByOutboundEdgeCollectionEdgeResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_prepare_jobs_for_scheduling**
> post_workflows_key_prepare_jobs_for_scheduling(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> PostWorkflowsKeyPrepareJobsForSchedulingResponse, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_prepare_jobs_for_scheduling(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyPrepareJobsForSchedulingResponse }, OpenAPI.Clients.ApiResponse

Return scheduler IDs that need to be activated.

Return scheduler IDs that need to be activated. Sets job status to scheduled.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**PostWorkflowsKeyPrepareJobsForSchedulingResponse**](PostWorkflowsKeyPrepareJobsForSchedulingResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_prepare_jobs_for_submission**
> post_workflows_key_prepare_jobs_for_submission(_api::DefaultApi, key::String, body::ComputeNodesResources; sort_method=nothing, limit=nothing, _mediaType=nothing) -> PostWorkflowsKeyPrepareJobsForSubmissionResponse, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_prepare_jobs_for_submission(_api::DefaultApi, response_stream::Channel, key::String, body::ComputeNodesResources; sort_method=nothing, limit=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyPrepareJobsForSubmissionResponse }, OpenAPI.Clients.ApiResponse

Return ready jobs, accounting for resource requirements.

Return jobs that are ready for submission and meet worker resource Sets status to submitted_pending.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]
**body** | [**ComputeNodesResources**](ComputeNodesResources.md)| Available worker resources. | 

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sort_method** | **String**|  | [default to &quot;gpus_runtime_memory&quot;]
 **limit** | **Float64**|  | [default to 100000.0]

### Return type

[**PostWorkflowsKeyPrepareJobsForSubmissionResponse**](PostWorkflowsKeyPrepareJobsForSubmissionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_prepare_next_jobs_for_submission**
> post_workflows_key_prepare_next_jobs_for_submission(_api::DefaultApi, key::String; limit=nothing, body=nothing, _mediaType=nothing) -> PostWorkflowsKeyPrepareNextJobsForSubmissionResponse, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_prepare_next_jobs_for_submission(_api::DefaultApi, response_stream::Channel, key::String; limit=nothing, body=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyPrepareNextJobsForSubmissionResponse }, OpenAPI.Clients.ApiResponse

Return user-requested number of ready jobs.

Return user-requested number of jobs that are ready for submission. Sets status to submitted_pending.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **Float64**|  | [default to 1.0]
 **body** | **Any**|  | 

### Return type

[**PostWorkflowsKeyPrepareNextJobsForSubmissionResponse**](PostWorkflowsKeyPrepareNextJobsForSubmissionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_process_auto_tune_resource_requirements_results**
> post_workflows_key_process_auto_tune_resource_requirements_results(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_process_auto_tune_resource_requirements_results(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Process the results of auto-tuning resource requirements.

Process the results of auto-tuning resource requirements.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_process_changed_job_inputs**
> post_workflows_key_process_changed_job_inputs(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> PostWorkflowsKeyProcessChangedJobInputsResponse, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_process_changed_job_inputs(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyProcessChangedJobInputsResponse }, OpenAPI.Clients.ApiResponse

Check for changed job inputs and update status accordingly.

Check for changed job inputs and update status accordingly.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**PostWorkflowsKeyProcessChangedJobInputsResponse**](PostWorkflowsKeyProcessChangedJobInputsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_reset_job_status**
> post_workflows_key_reset_job_status(_api::DefaultApi, key::String; failed_only=nothing, body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_reset_job_status(_api::DefaultApi, response_stream::Channel, key::String; failed_only=nothing, body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Reset job status.

Reset status for jobs to uninitialized.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **failed_only** | **Bool**| Only reset failed jobs | [default to false]
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **post_workflows_key_reset_status**
> post_workflows_key_reset_status(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> post_workflows_key_reset_status(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Reset worklow status.

Reset workflow status.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_aws_schedulers_key**
> put_aws_schedulers_key(_api::DefaultApi, workflow::String, key::String, body::AwsSchedulersModel; _mediaType=nothing) -> AwsSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> put_aws_schedulers_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::AwsSchedulersModel; _mediaType=nothing) -> Channel{ AwsSchedulersModel }, OpenAPI.Clients.ApiResponse

Update AWS compute node configuration

Update a document in the \"aws_schedulers\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the AWS compute node configuration. | [default to nothing]
**body** | [**AwsSchedulersModel**](AwsSchedulersModel.md)| AWS compute node configuration to update in the collection. | 

### Return type

[**AwsSchedulersModel**](AwsSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_compute_node_stats_key**
> put_compute_node_stats_key(_api::DefaultApi, workflow::String, key::String, body::ComputeNodeStatsModel; _mediaType=nothing) -> ComputeNodeStatsModel, OpenAPI.Clients.ApiResponse <br/>
> put_compute_node_stats_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::ComputeNodeStatsModel; _mediaType=nothing) -> Channel{ ComputeNodeStatsModel }, OpenAPI.Clients.ApiResponse

Update compute node statistics

Update a document in the \"compute_node_stats\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the compute node statistics. | [default to nothing]
**body** | [**ComputeNodeStatsModel**](ComputeNodeStatsModel.md)| compute node statistics to update in the collection. | 

### Return type

[**ComputeNodeStatsModel**](ComputeNodeStatsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_compute_nodes_key**
> put_compute_nodes_key(_api::DefaultApi, workflow::String, key::String, body::ComputeNodesModel; _mediaType=nothing) -> ComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> put_compute_nodes_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::ComputeNodesModel; _mediaType=nothing) -> Channel{ ComputeNodesModel }, OpenAPI.Clients.ApiResponse

Update compute node

Update a document in the \"compute_nodes\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the compute node. | [default to nothing]
**body** | [**ComputeNodesModel**](ComputeNodesModel.md)| compute node to update in the collection. | 

### Return type

[**ComputeNodesModel**](ComputeNodesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_events_key**
> put_events_key(_api::DefaultApi, workflow::String, key::String, body::Any; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> put_events_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::Any; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Update event

Update a document in the \"events\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the event. | [default to nothing]
**body** | **Any**| event to update in the collection. | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_files_key**
> put_files_key(_api::DefaultApi, workflow::String, key::String, body::FilesModel; _mediaType=nothing) -> FilesModel, OpenAPI.Clients.ApiResponse <br/>
> put_files_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::FilesModel; _mediaType=nothing) -> Channel{ FilesModel }, OpenAPI.Clients.ApiResponse

Update file

Update a document in the \"files\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the file. | [default to nothing]
**body** | [**FilesModel**](FilesModel.md)| file to update in the collection. | 

### Return type

[**FilesModel**](FilesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_job_process_stats_key**
> put_job_process_stats_key(_api::DefaultApi, workflow::String, key::String, body::JobProcessStatsModel; _mediaType=nothing) -> JobProcessStatsModel, OpenAPI.Clients.ApiResponse <br/>
> put_job_process_stats_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::JobProcessStatsModel; _mediaType=nothing) -> Channel{ JobProcessStatsModel }, OpenAPI.Clients.ApiResponse

Update job process statistics

Update a document in the \"job_process_stats\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the job process statistics. | [default to nothing]
**body** | [**JobProcessStatsModel**](JobProcessStatsModel.md)| job process statistics to update in the collection. | 

### Return type

[**JobProcessStatsModel**](JobProcessStatsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_jobs_key**
> put_jobs_key(_api::DefaultApi, workflow::String, key::String, body::JobsModel; _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> put_jobs_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::JobsModel; _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

Update job

Update a document in the \"jobs\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the job. | [default to nothing]
**body** | [**JobsModel**](JobsModel.md)| job to update in the collection. | 

### Return type

[**JobsModel**](JobsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_jobs_key_manage_status_change_status_rev_run_id**
> put_jobs_key_manage_status_change_status_rev_run_id(_api::DefaultApi, workflow::String, key::String, status::String, rev::String, run_id::Int64; body=nothing, _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> put_jobs_key_manage_status_change_status_rev_run_id(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, status::String, rev::String, run_id::Int64; body=nothing, _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

Change the status of a job and manage side effects.

Change the status of a job and manage side effects.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]
**status** | **String**| New job status | [default to nothing]
**rev** | **String**| Current job revision | [default to nothing]
**run_id** | **Int64**| Current job run ID | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**JobsModel**](JobsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_jobs_key_resource_requirements_rr_key**
> put_jobs_key_resource_requirements_rr_key(_api::DefaultApi, workflow::String, key::String, rr_key::String; body=nothing, _mediaType=nothing) -> EdgesNameModel, OpenAPI.Clients.ApiResponse <br/>
> put_jobs_key_resource_requirements_rr_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, rr_key::String; body=nothing, _mediaType=nothing) -> Channel{ EdgesNameModel }, OpenAPI.Clients.ApiResponse

Set the resource requirements for a job.

Set the resource requirements for a job, replacing any current value.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**key** | **String**| Job key | [default to nothing]
**rr_key** | **String**|  | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

[**EdgesNameModel**](EdgesNameModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_local_schedulers_key**
> put_local_schedulers_key(_api::DefaultApi, workflow::String, key::String, body::LocalSchedulersModel; _mediaType=nothing) -> LocalSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> put_local_schedulers_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::LocalSchedulersModel; _mediaType=nothing) -> Channel{ LocalSchedulersModel }, OpenAPI.Clients.ApiResponse

Update local compute node configuration

Update a document in the \"local_schedulers\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the local compute node configuration. | [default to nothing]
**body** | [**LocalSchedulersModel**](LocalSchedulersModel.md)| local compute node configuration to update in the collection. | 

### Return type

[**LocalSchedulersModel**](LocalSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_resource_requirements_key**
> put_resource_requirements_key(_api::DefaultApi, workflow::String, key::String, body::ResourceRequirementsModel; _mediaType=nothing) -> ResourceRequirementsModel, OpenAPI.Clients.ApiResponse <br/>
> put_resource_requirements_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::ResourceRequirementsModel; _mediaType=nothing) -> Channel{ ResourceRequirementsModel }, OpenAPI.Clients.ApiResponse

Update resource requirements

Update a document in the \"resource_requirements\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the resource requirements. | [default to nothing]
**body** | [**ResourceRequirementsModel**](ResourceRequirementsModel.md)| resource requirements to update in the collection. | 

### Return type

[**ResourceRequirementsModel**](ResourceRequirementsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_results_key**
> put_results_key(_api::DefaultApi, workflow::String, key::String, body::ResultsModel; _mediaType=nothing) -> ResultsModel, OpenAPI.Clients.ApiResponse <br/>
> put_results_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::ResultsModel; _mediaType=nothing) -> Channel{ ResultsModel }, OpenAPI.Clients.ApiResponse

Update result

Update a document in the \"results\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the result. | [default to nothing]
**body** | [**ResultsModel**](ResultsModel.md)| result to update in the collection. | 

### Return type

[**ResultsModel**](ResultsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_scheduled_compute_nodes_key**
> put_scheduled_compute_nodes_key(_api::DefaultApi, workflow::String, key::String, body::ScheduledComputeNodesModel; _mediaType=nothing) -> ScheduledComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> put_scheduled_compute_nodes_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::ScheduledComputeNodesModel; _mediaType=nothing) -> Channel{ ScheduledComputeNodesModel }, OpenAPI.Clients.ApiResponse

Update scheduled compute node

Update a document in the \"scheduled_compute_nodes\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the scheduled compute node. | [default to nothing]
**body** | [**ScheduledComputeNodesModel**](ScheduledComputeNodesModel.md)| scheduled compute node to update in the collection. | 

### Return type

[**ScheduledComputeNodesModel**](ScheduledComputeNodesModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_slurm_schedulers_key**
> put_slurm_schedulers_key(_api::DefaultApi, workflow::String, key::String, body::SlurmSchedulersModel; _mediaType=nothing) -> SlurmSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> put_slurm_schedulers_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::SlurmSchedulersModel; _mediaType=nothing) -> Channel{ SlurmSchedulersModel }, OpenAPI.Clients.ApiResponse

Update Slurm compute node configuration

Update a document in the \"slurm_schedulers\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the Slurm compute node configuration. | [default to nothing]
**body** | [**SlurmSchedulersModel**](SlurmSchedulersModel.md)| Slurm compute node configuration to update in the collection. | 

### Return type

[**SlurmSchedulersModel**](SlurmSchedulersModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_user_data_key**
> put_user_data_key(_api::DefaultApi, workflow::String, key::String, body::UserDataModel; _mediaType=nothing) -> UserDataModel, OpenAPI.Clients.ApiResponse <br/>
> put_user_data_key(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::UserDataModel; _mediaType=nothing) -> Channel{ UserDataModel }, OpenAPI.Clients.ApiResponse

Update user data

Update a document in the \"user_data\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key. | [default to nothing]
**key** | **String**| key of the user data. | [default to nothing]
**body** | [**UserDataModel**](UserDataModel.md)| user data to update in the collection. | 

### Return type

[**UserDataModel**](UserDataModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_workflows_key**
> put_workflows_key(_api::DefaultApi, key::String, body::WorkflowsModel; _mediaType=nothing) -> WorkflowsModel, OpenAPI.Clients.ApiResponse <br/>
> put_workflows_key(_api::DefaultApi, response_stream::Channel, key::String, body::WorkflowsModel; _mediaType=nothing) -> Channel{ WorkflowsModel }, OpenAPI.Clients.ApiResponse

Update workflow

Update a document in the \"workflows\" collection.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Key of the workflow. | [default to nothing]
**body** | [**WorkflowsModel**](WorkflowsModel.md)| workflow to update in the collection. | 

### Return type

[**WorkflowsModel**](WorkflowsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_workflows_key_cancel**
> put_workflows_key_cancel(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> put_workflows_key_cancel(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Cancel workflow.

Cancel workflow. Workers will detect the status change and cancel jobs.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **Any**|  | 

### Return type

**Any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_workflows_key_config**
> put_workflows_key_config(_api::DefaultApi, key::String, body::WorkflowConfigModel; _mediaType=nothing) -> WorkflowConfigModel, OpenAPI.Clients.ApiResponse <br/>
> put_workflows_key_config(_api::DefaultApi, response_stream::Channel, key::String, body::WorkflowConfigModel; _mediaType=nothing) -> Channel{ WorkflowConfigModel }, OpenAPI.Clients.ApiResponse

Updates the workflow config.

Updates the workflow config.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]
**body** | [**WorkflowConfigModel**](WorkflowConfigModel.md)| Updated workflow config | 

### Return type

[**WorkflowConfigModel**](WorkflowConfigModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **put_workflows_key_status**
> put_workflows_key_status(_api::DefaultApi, key::String, body::WorkflowStatusModel; _mediaType=nothing) -> WorkflowStatusModel, OpenAPI.Clients.ApiResponse <br/>
> put_workflows_key_status(_api::DefaultApi, response_stream::Channel, key::String, body::WorkflowStatusModel; _mediaType=nothing) -> Channel{ WorkflowStatusModel }, OpenAPI.Clients.ApiResponse

Reports the workflow status.

Reports the workflow status.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]
**body** | [**WorkflowStatusModel**](WorkflowStatusModel.md)| Updated workflow status | 

### Return type

[**WorkflowStatusModel**](WorkflowStatusModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

