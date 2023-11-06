# DefaultApi

All URIs are relative to *http://localhost/_db/test-workflows/torc-service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_aws_scheduler**](DefaultApi.md#add_aws_scheduler) | **POST** /workflows/{workflow}/aws_schedulers | Store a AWS compute node configuration.
[**add_bulk_job_with_edges**](DefaultApi.md#add_bulk_job_with_edges) | **POST** /workflows/{workflow}/bulk_jobs_with_edges | Add jobs in bulk with edge definitions.
[**add_compute_node**](DefaultApi.md#add_compute_node) | **POST** /workflows/{workflow}/compute_nodes | Store a compute node.
[**add_compute_node_stats**](DefaultApi.md#add_compute_node_stats) | **POST** /workflows/{workflow}/compute_node_stats | Store a compute node statistics.
[**add_edge**](DefaultApi.md#add_edge) | **POST** /workflows/{workflow}/edges/{name} | Store an edge between two vertexes.
[**add_event**](DefaultApi.md#add_event) | **POST** /workflows/{workflow}/events | Store a event.
[**add_file**](DefaultApi.md#add_file) | **POST** /workflows/{workflow}/files | Store a file.
[**add_job**](DefaultApi.md#add_job) | **POST** /workflows/{workflow}/jobs | Store a job.
[**add_job_process_stats**](DefaultApi.md#add_job_process_stats) | **POST** /workflows/{workflow}/job_process_stats | Store a job process statistics.
[**add_job_specification**](DefaultApi.md#add_job_specification) | **POST** /workflows/{workflow}/job_specifications | Store a job and create edges.
[**add_job_user_data**](DefaultApi.md#add_job_user_data) | **POST** /workflows/{workflow}/jobs/{key}/user_data | Store user data for a job.
[**add_job_with_edges**](DefaultApi.md#add_job_with_edges) | **POST** /workflows/{workflow}/job_with_edges | Add a job with edge definitions.
[**add_local_scheduler**](DefaultApi.md#add_local_scheduler) | **POST** /workflows/{workflow}/local_schedulers | Store a local compute node configuration.
[**add_resource_requirements**](DefaultApi.md#add_resource_requirements) | **POST** /workflows/{workflow}/resource_requirements | Store a resource requirements.
[**add_result**](DefaultApi.md#add_result) | **POST** /workflows/{workflow}/results | Store a result.
[**add_scheduled_compute_node**](DefaultApi.md#add_scheduled_compute_node) | **POST** /workflows/{workflow}/scheduled_compute_nodes | Store a scheduled compute node.
[**add_slurm_scheduler**](DefaultApi.md#add_slurm_scheduler) | **POST** /workflows/{workflow}/slurm_schedulers | Store a Slurm compute node configuration.
[**add_user_data**](DefaultApi.md#add_user_data) | **POST** /workflows/{workflow}/user_data | Store a user data.
[**add_workflow**](DefaultApi.md#add_workflow) | **POST** /workflows | Store a workflow.
[**add_workflow_specification**](DefaultApi.md#add_workflow_specification) | **POST** /workflow_specifications | Store a workflow.
[**auto_tune_resource_requirements**](DefaultApi.md#auto_tune_resource_requirements) | **POST** /workflows/{key}/auto_tune_resource_requirements | Enable workflow for auto-tuning resource requirements.
[**cancel_workflow**](DefaultApi.md#cancel_workflow) | **PUT** /workflows/{key}/cancel | Cancel workflow.
[**complete_job**](DefaultApi.md#complete_job) | **POST** /workflows/{workflow}/jobs/{key}/complete_job/{status}/{rev}/{run_id} | Complete a job and add a result.
[**delete_aws_schedulers**](DefaultApi.md#delete_aws_schedulers) | **DELETE** /workflows/{workflow}/aws_schedulers | Delete all documents of type AWS compute node configuration for a workflow
[**delete_compute_node_stats**](DefaultApi.md#delete_compute_node_stats) | **DELETE** /workflows/{workflow}/compute_node_stats | Delete all documents of type compute node statistics for a workflow
[**delete_compute_nodes**](DefaultApi.md#delete_compute_nodes) | **DELETE** /workflows/{workflow}/compute_nodes | Delete all documents of type compute node for a workflow
[**delete_edges**](DefaultApi.md#delete_edges) | **DELETE** /workflows/{workflow}/edges/{name} | Delete all edges from the designated collection
[**delete_events**](DefaultApi.md#delete_events) | **DELETE** /workflows/{workflow}/events | Delete all documents of type event for a workflow
[**delete_files**](DefaultApi.md#delete_files) | **DELETE** /workflows/{workflow}/files | Delete all documents of type file for a workflow
[**delete_job_process_stats**](DefaultApi.md#delete_job_process_stats) | **DELETE** /workflows/{workflow}/job_process_stats | Delete all documents of type job process statistics for a workflow
[**delete_jobs**](DefaultApi.md#delete_jobs) | **DELETE** /workflows/{workflow}/jobs | Delete all documents of type job for a workflow
[**delete_local_schedulers**](DefaultApi.md#delete_local_schedulers) | **DELETE** /workflows/{workflow}/local_schedulers | Delete all documents of type local compute node configuration for a workflow
[**delete_resource_requirements**](DefaultApi.md#delete_resource_requirements) | **DELETE** /workflows/{workflow}/resource_requirements | Delete all documents of type resource requirements for a workflow
[**delete_results**](DefaultApi.md#delete_results) | **DELETE** /workflows/{workflow}/results | Delete all documents of type result for a workflow
[**delete_scheduled_compute_nodes**](DefaultApi.md#delete_scheduled_compute_nodes) | **DELETE** /workflows/{workflow}/scheduled_compute_nodes | Delete all documents of type scheduled compute node for a workflow
[**delete_slurm_schedulers**](DefaultApi.md#delete_slurm_schedulers) | **DELETE** /workflows/{workflow}/slurm_schedulers | Delete all documents of type Slurm compute node configuration for a workflow
[**delete_user_data**](DefaultApi.md#delete_user_data) | **DELETE** /workflows/{workflow}/user_data | Delete all documents of type user data for a workflow
[**get_aws_scheduler**](DefaultApi.md#get_aws_scheduler) | **GET** /workflows/{workflow}/aws_schedulers/{key} | Retrieve the AWS compute node configuration for a key.
[**get_compute_node**](DefaultApi.md#get_compute_node) | **GET** /workflows/{workflow}/compute_nodes/{key} | Retrieve the compute node for a key.
[**get_compute_node_stats**](DefaultApi.md#get_compute_node_stats) | **GET** /workflows/{workflow}/compute_node_stats/{key} | Retrieve the compute node statistics for a key.
[**get_dot_graph**](DefaultApi.md#get_dot_graph) | **GET** /workflows/{key}/dot_graph/{name} | Build a string for a DOT graph.
[**get_edge**](DefaultApi.md#get_edge) | **GET** /workflows/{workflow}/edges/{name}/{key} | Retrieve an edge
[**get_event**](DefaultApi.md#get_event) | **GET** /workflows/{workflow}/events/{key} | Retrieve the event for a key.
[**get_events_after_timestamp**](DefaultApi.md#get_events_after_timestamp) | **GET** /workflows/{key}/events_after_timestamp/{timestamp} | Return all events newer than the event with event_key.
[**get_file**](DefaultApi.md#get_file) | **GET** /workflows/{workflow}/files/{key} | Retrieve the file for a key.
[**get_job**](DefaultApi.md#get_job) | **GET** /workflows/{workflow}/jobs/{key} | Retrieve the job for a key.
[**get_job_process_stats**](DefaultApi.md#get_job_process_stats) | **GET** /workflows/{workflow}/job_process_stats/{key} | Retrieve the job process statistics for a key.
[**get_job_resource_requirements**](DefaultApi.md#get_job_resource_requirements) | **GET** /workflows/{workflow}/jobs/{key}/resource_requirements | Retrieve the resource requirements for a job.
[**get_job_specification**](DefaultApi.md#get_job_specification) | **GET** /workflows/{workflow}/job_specifications/{key} | Retrieve a job
[**get_latest_event_timestamp**](DefaultApi.md#get_latest_event_timestamp) | **GET** /workflows/{key}/latest_event_timestamp | Return the timestamp of the latest event.
[**get_latest_job_result**](DefaultApi.md#get_latest_job_result) | **GET** /workflows/{workflow}/results/find_by_job/{key} | Retrieve the latest result for a job
[**get_local_scheduler**](DefaultApi.md#get_local_scheduler) | **GET** /workflows/{workflow}/local_schedulers/{key} | Retrieve the local compute node configuration for a key.
[**get_process_stats_for_job**](DefaultApi.md#get_process_stats_for_job) | **GET** /workflows/{workflow}/jobs/{key}/process_stats | Retrieve the job process stats for a job.
[**get_ready_job_requirements**](DefaultApi.md#get_ready_job_requirements) | **GET** /workflows/{key}/ready_job_requirements | Return the resource requirements for ready jobs.
[**get_resource_requirements**](DefaultApi.md#get_resource_requirements) | **GET** /workflows/{workflow}/resource_requirements/{key} | Retrieve the resource requirements for a key.
[**get_result**](DefaultApi.md#get_result) | **GET** /workflows/{workflow}/results/{key} | Retrieve the result for a key.
[**get_scheduled_compute_node**](DefaultApi.md#get_scheduled_compute_node) | **GET** /workflows/{workflow}/scheduled_compute_nodes/{key} | Retrieve the scheduled compute node for a key.
[**get_slurm_scheduler**](DefaultApi.md#get_slurm_scheduler) | **GET** /workflows/{workflow}/slurm_schedulers/{key} | Retrieve the Slurm compute node configuration for a key.
[**get_user_data**](DefaultApi.md#get_user_data) | **GET** /workflows/{workflow}/user_data/{key} | Retrieve the user data for a key.
[**get_version**](DefaultApi.md#get_version) | **GET** /version | Return the version of the service.
[**get_workflow**](DefaultApi.md#get_workflow) | **GET** /workflows/{key} | Retrieve the workflow for an key.
[**get_workflow_config**](DefaultApi.md#get_workflow_config) | **GET** /workflows/{key}/config | Returns the workflow config.
[**get_workflow_specification**](DefaultApi.md#get_workflow_specification) | **GET** /workflow_specifications/{key} | Retrieve the current workflow
[**get_workflow_specification_example**](DefaultApi.md#get_workflow_specification_example) | **GET** /workflow_specifications/example | Retrieve an example workflow specification
[**get_workflow_specification_template**](DefaultApi.md#get_workflow_specification_template) | **GET** /workflow_specifications/template | Retrieve the workflow specification template
[**get_workflow_status**](DefaultApi.md#get_workflow_status) | **GET** /workflows/{key}/status | Reports the workflow status.
[**initialize_jobs**](DefaultApi.md#initialize_jobs) | **POST** /workflows/{key}/initialize_jobs | Initialize job relationships.
[**is_workflow_complete**](DefaultApi.md#is_workflow_complete) | **GET** /workflows/{key}/is_complete | Report whether the workflow is complete
[**join_collections_by_inbound_edge**](DefaultApi.md#join_collections_by_inbound_edge) | **POST** /workflows/{key}/join_by_inbound_edge/{collection}/{edge} | Retrieve a joined table of two collections.
[**join_collections_by_outbound_edge**](DefaultApi.md#join_collections_by_outbound_edge) | **POST** /workflows/{key}/join_by_outbound_edge/{collection}/{edge} | Retrieve a joined table of two collections.
[**list_aws_schedulers**](DefaultApi.md#list_aws_schedulers) | **GET** /workflows/{workflow}/aws_schedulers | Retrieve all AWS compute node configuration documents
[**list_collection_names**](DefaultApi.md#list_collection_names) | **GET** /workflows/{key}/collection_names | Retrieve all collection names for one workflow.
[**list_compute_node_stats**](DefaultApi.md#list_compute_node_stats) | **GET** /workflows/{workflow}/compute_node_stats | Retrieve all compute node statistics documents
[**list_compute_nodes**](DefaultApi.md#list_compute_nodes) | **GET** /workflows/{workflow}/compute_nodes | Retrieve all compute node documents
[**list_edges**](DefaultApi.md#list_edges) | **GET** /workflows/{workflow}/edges/{name} | Retrieve all edges from the designated collection.
[**list_events**](DefaultApi.md#list_events) | **GET** /workflows/{workflow}/events | Retrieve all event documents
[**list_files**](DefaultApi.md#list_files) | **GET** /workflows/{workflow}/files | Retrieve all file documents
[**list_files_produced_by_job**](DefaultApi.md#list_files_produced_by_job) | **GET** /workflows/{workflow}/files/produced_by_job/{key} | Retrieve files produced by a job
[**list_job_keys**](DefaultApi.md#list_job_keys) | **GET** /workflows/{workflow}/job_keys | Retrieve all job keys for a workflow.
[**list_job_process_stats**](DefaultApi.md#list_job_process_stats) | **GET** /workflows/{workflow}/job_process_stats | Retrieve all job process statistics documents
[**list_job_specifications**](DefaultApi.md#list_job_specifications) | **GET** /workflows/{workflow}/job_specifications | Retrieve all job definitions
[**list_job_user_data_consumes**](DefaultApi.md#list_job_user_data_consumes) | **GET** /workflows/{workflow}/jobs/{key}/user_data_consumes | Retrieve all user data consumed by a job.
[**list_job_user_data_stores**](DefaultApi.md#list_job_user_data_stores) | **GET** /workflows/{workflow}/jobs/{key}/user_data_stores | Retrieve all user data for a job.
[**list_jobs**](DefaultApi.md#list_jobs) | **GET** /workflows/{workflow}/jobs | Retrieve all job documents
[**list_jobs_by_needs_file**](DefaultApi.md#list_jobs_by_needs_file) | **GET** /workflows/{workflow}/jobs/find_by_needs_file/{key} | Retrieve all jobs that need a file
[**list_jobs_by_status**](DefaultApi.md#list_jobs_by_status) | **GET** /workflows/{workflow}/jobs/find_by_status/{status} | Retrieve all jobs with a specific status
[**list_local_schedulers**](DefaultApi.md#list_local_schedulers) | **GET** /workflows/{workflow}/local_schedulers | Retrieve all local compute node configuration documents
[**list_missing_user_data**](DefaultApi.md#list_missing_user_data) | **GET** /workflows/{key}/missing_user_data | List missing user data that should exist.
[**list_required_existing_files**](DefaultApi.md#list_required_existing_files) | **GET** /workflows/{key}/required_existing_files | List files that must exist.
[**list_resource_requirements**](DefaultApi.md#list_resource_requirements) | **GET** /workflows/{workflow}/resource_requirements | Retrieve all resource requirements documents
[**list_results**](DefaultApi.md#list_results) | **GET** /workflows/{workflow}/results | Retrieve all result documents
[**list_scheduled_compute_nodes**](DefaultApi.md#list_scheduled_compute_nodes) | **GET** /workflows/{workflow}/scheduled_compute_nodes | Retrieve all scheduled compute node documents
[**list_slurm_schedulers**](DefaultApi.md#list_slurm_schedulers) | **GET** /workflows/{workflow}/slurm_schedulers | Retrieve all Slurm compute node configuration documents
[**list_user_data**](DefaultApi.md#list_user_data) | **GET** /workflows/{workflow}/user_data | Retrieve all user data documents
[**list_workflows**](DefaultApi.md#list_workflows) | **GET** /workflows | Retrieve all workflows
[**manage_status_change**](DefaultApi.md#manage_status_change) | **PUT** /workflows/{workflow}/jobs/{key}/manage_status_change/{status}/{rev}/{run_id} | Change the status of a job and manage side effects.
[**modify_aws_scheduler**](DefaultApi.md#modify_aws_scheduler) | **PUT** /workflows/{workflow}/aws_schedulers/{key} | Update AWS compute node configuration
[**modify_compute_node**](DefaultApi.md#modify_compute_node) | **PUT** /workflows/{workflow}/compute_nodes/{key} | Update compute node
[**modify_compute_node_stats**](DefaultApi.md#modify_compute_node_stats) | **PUT** /workflows/{workflow}/compute_node_stats/{key} | Update compute node statistics
[**modify_event**](DefaultApi.md#modify_event) | **PUT** /workflows/{workflow}/events/{key} | Update event
[**modify_file**](DefaultApi.md#modify_file) | **PUT** /workflows/{workflow}/files/{key} | Update file
[**modify_job**](DefaultApi.md#modify_job) | **PUT** /workflows/{workflow}/jobs/{key} | Update job
[**modify_job_process_stats**](DefaultApi.md#modify_job_process_stats) | **PUT** /workflows/{workflow}/job_process_stats/{key} | Update job process statistics
[**modify_job_resource_requirements**](DefaultApi.md#modify_job_resource_requirements) | **PUT** /workflows/{workflow}/jobs/{key}/resource_requirements/{rr_key} | Set the resource requirements for a job.
[**modify_local_scheduler**](DefaultApi.md#modify_local_scheduler) | **PUT** /workflows/{workflow}/local_schedulers/{key} | Update local compute node configuration
[**modify_resource_requirements**](DefaultApi.md#modify_resource_requirements) | **PUT** /workflows/{workflow}/resource_requirements/{key} | Update resource requirements
[**modify_result**](DefaultApi.md#modify_result) | **PUT** /workflows/{workflow}/results/{key} | Update result
[**modify_scheduled_compute_node**](DefaultApi.md#modify_scheduled_compute_node) | **PUT** /workflows/{workflow}/scheduled_compute_nodes/{key} | Update scheduled compute node
[**modify_slurm_scheduler**](DefaultApi.md#modify_slurm_scheduler) | **PUT** /workflows/{workflow}/slurm_schedulers/{key} | Update Slurm compute node configuration
[**modify_user_data**](DefaultApi.md#modify_user_data) | **PUT** /workflows/{workflow}/user_data/{key} | Update user data
[**modify_workflow**](DefaultApi.md#modify_workflow) | **PUT** /workflows/{key} | Update workflow
[**modify_workflow_config**](DefaultApi.md#modify_workflow_config) | **PUT** /workflows/{key}/config | Updates the workflow config.
[**modify_workflow_status**](DefaultApi.md#modify_workflow_status) | **PUT** /workflows/{key}/status | Reports the workflow status.
[**ping**](DefaultApi.md#ping) | **GET** /ping | Check if the service is running.
[**prepare_jobs_for_scheduling**](DefaultApi.md#prepare_jobs_for_scheduling) | **POST** /workflows/{key}/prepare_jobs_for_scheduling | Return scheduler IDs that need to be activated.
[**prepare_jobs_for_submission**](DefaultApi.md#prepare_jobs_for_submission) | **POST** /workflows/{key}/prepare_jobs_for_submission | Return ready jobs, accounting for resource requirements.
[**prepare_next_jobs_for_submission**](DefaultApi.md#prepare_next_jobs_for_submission) | **POST** /workflows/{key}/prepare_next_jobs_for_submission | Return user-requested number of ready jobs.
[**process_auto_tune_resource_requirements_results**](DefaultApi.md#process_auto_tune_resource_requirements_results) | **POST** /workflows/{key}/process_auto_tune_resource_requirements_results | Process the results of auto-tuning resource requirements.
[**process_changed_job_inputs**](DefaultApi.md#process_changed_job_inputs) | **POST** /workflows/{key}/process_changed_job_inputs | Check for changed job inputs and update status accordingly.
[**remove_aws_scheduler**](DefaultApi.md#remove_aws_scheduler) | **DELETE** /workflows/{workflow}/aws_schedulers/{key} | Delete a document of type AWS compute node configuration
[**remove_compute_node**](DefaultApi.md#remove_compute_node) | **DELETE** /workflows/{workflow}/compute_nodes/{key} | Delete a document of type compute node
[**remove_compute_node_stats**](DefaultApi.md#remove_compute_node_stats) | **DELETE** /workflows/{workflow}/compute_node_stats/{key} | Delete a document of type compute node statistics
[**remove_edge**](DefaultApi.md#remove_edge) | **DELETE** /workflows/{workflow}/edges/{name}/{key} | Delete an edge
[**remove_event**](DefaultApi.md#remove_event) | **DELETE** /workflows/{workflow}/events/{key} | Delete a document of type event
[**remove_file**](DefaultApi.md#remove_file) | **DELETE** /workflows/{workflow}/files/{key} | Delete a document of type file
[**remove_job**](DefaultApi.md#remove_job) | **DELETE** /workflows/{workflow}/jobs/{key} | Delete a document of type job
[**remove_job_process_stats**](DefaultApi.md#remove_job_process_stats) | **DELETE** /workflows/{workflow}/job_process_stats/{key} | Delete a document of type job process statistics
[**remove_local_scheduler**](DefaultApi.md#remove_local_scheduler) | **DELETE** /workflows/{workflow}/local_schedulers/{key} | Delete a document of type local compute node configuration
[**remove_resource_requirements**](DefaultApi.md#remove_resource_requirements) | **DELETE** /workflows/{workflow}/resource_requirements/{key} | Delete a document of type resource requirements
[**remove_result**](DefaultApi.md#remove_result) | **DELETE** /workflows/{workflow}/results/{key} | Delete a document of type result
[**remove_scheduled_compute_node**](DefaultApi.md#remove_scheduled_compute_node) | **DELETE** /workflows/{workflow}/scheduled_compute_nodes/{key} | Delete a document of type scheduled compute node
[**remove_slurm_scheduler**](DefaultApi.md#remove_slurm_scheduler) | **DELETE** /workflows/{workflow}/slurm_schedulers/{key} | Delete a document of type Slurm compute node configuration
[**remove_user_data**](DefaultApi.md#remove_user_data) | **DELETE** /workflows/{workflow}/user_data/{key} | Delete a document of type user data
[**remove_workflow**](DefaultApi.md#remove_workflow) | **DELETE** /workflows/{key} | Delete a workflow
[**reset_job_status**](DefaultApi.md#reset_job_status) | **POST** /workflows/{key}/reset_job_status | Reset job status.
[**reset_workflow_status**](DefaultApi.md#reset_workflow_status) | **POST** /workflows/{key}/reset_status | Reset worklow status.


# **add_aws_scheduler**
> add_aws_scheduler(_api::DefaultApi, workflow::String, body::AwsSchedulersModel; _mediaType=nothing) -> AwsSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> add_aws_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, body::AwsSchedulersModel; _mediaType=nothing) -> Channel{ AwsSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **add_bulk_job_with_edges**
> add_bulk_job_with_edges(_api::DefaultApi, workflow::String, body::BulkJobsWithEdgesModel; _mediaType=nothing) -> PostBulkJobsWithEdgesResponse, OpenAPI.Clients.ApiResponse <br/>
> add_bulk_job_with_edges(_api::DefaultApi, response_stream::Channel, workflow::String, body::BulkJobsWithEdgesModel; _mediaType=nothing) -> Channel{ PostBulkJobsWithEdgesResponse }, OpenAPI.Clients.ApiResponse

Add jobs in bulk with edge definitions.

Add jobs in bulk with edge definitions. Recommended max job count of 10,000.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**BulkJobsWithEdgesModel**](BulkJobsWithEdgesModel.md)|  | 

### Return type

[**PostBulkJobsWithEdgesResponse**](PostBulkJobsWithEdgesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **add_compute_node**
> add_compute_node(_api::DefaultApi, workflow::String, body::ComputeNodesModel; _mediaType=nothing) -> ComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> add_compute_node(_api::DefaultApi, response_stream::Channel, workflow::String, body::ComputeNodesModel; _mediaType=nothing) -> Channel{ ComputeNodesModel }, OpenAPI.Clients.ApiResponse

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

# **add_compute_node_stats**
> add_compute_node_stats(_api::DefaultApi, workflow::String, body::ComputeNodeStatsModel; _mediaType=nothing) -> ComputeNodeStatsModel, OpenAPI.Clients.ApiResponse <br/>
> add_compute_node_stats(_api::DefaultApi, response_stream::Channel, workflow::String, body::ComputeNodeStatsModel; _mediaType=nothing) -> Channel{ ComputeNodeStatsModel }, OpenAPI.Clients.ApiResponse

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

# **add_edge**
> add_edge(_api::DefaultApi, workflow::String, name::String, body::EdgesNameModel; _mediaType=nothing) -> EdgesNameModel, OpenAPI.Clients.ApiResponse <br/>
> add_edge(_api::DefaultApi, response_stream::Channel, workflow::String, name::String, body::EdgesNameModel; _mediaType=nothing) -> Channel{ EdgesNameModel }, OpenAPI.Clients.ApiResponse

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

# **add_event**
> add_event(_api::DefaultApi, workflow::String, body::Any; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> add_event(_api::DefaultApi, response_stream::Channel, workflow::String, body::Any; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **add_file**
> add_file(_api::DefaultApi, workflow::String, body::FilesModel; _mediaType=nothing) -> FilesModel, OpenAPI.Clients.ApiResponse <br/>
> add_file(_api::DefaultApi, response_stream::Channel, workflow::String, body::FilesModel; _mediaType=nothing) -> Channel{ FilesModel }, OpenAPI.Clients.ApiResponse

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

# **add_job**
> add_job(_api::DefaultApi, workflow::String, body::JobsModel; _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> add_job(_api::DefaultApi, response_stream::Channel, workflow::String, body::JobsModel; _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

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

# **add_job_process_stats**
> add_job_process_stats(_api::DefaultApi, workflow::String, body::JobProcessStatsModel; _mediaType=nothing) -> JobProcessStatsModel, OpenAPI.Clients.ApiResponse <br/>
> add_job_process_stats(_api::DefaultApi, response_stream::Channel, workflow::String, body::JobProcessStatsModel; _mediaType=nothing) -> Channel{ JobProcessStatsModel }, OpenAPI.Clients.ApiResponse

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

# **add_job_specification**
> add_job_specification(_api::DefaultApi, workflow::String, body::JobSpecificationsModel; _mediaType=nothing) -> JobSpecificationsModel, OpenAPI.Clients.ApiResponse <br/>
> add_job_specification(_api::DefaultApi, response_stream::Channel, workflow::String, body::JobSpecificationsModel; _mediaType=nothing) -> Channel{ JobSpecificationsModel }, OpenAPI.Clients.ApiResponse

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

# **add_job_user_data**
> add_job_user_data(_api::DefaultApi, workflow::String, key::String, body::UserDataModel; _mediaType=nothing) -> UserDataModel, OpenAPI.Clients.ApiResponse <br/>
> add_job_user_data(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::UserDataModel; _mediaType=nothing) -> Channel{ UserDataModel }, OpenAPI.Clients.ApiResponse

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

# **add_job_with_edges**
> add_job_with_edges(_api::DefaultApi, workflow::String, body::JobWithEdgesModel; _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> add_job_with_edges(_api::DefaultApi, response_stream::Channel, workflow::String, body::JobWithEdgesModel; _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

Add a job with edge definitions.

Add a job with edge definitions.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**workflow** | **String**| Workflow key | [default to nothing]
**body** | [**JobWithEdgesModel**](JobWithEdgesModel.md)|  | 

### Return type

[**JobsModel**](JobsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **add_local_scheduler**
> add_local_scheduler(_api::DefaultApi, workflow::String, body::LocalSchedulersModel; _mediaType=nothing) -> LocalSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> add_local_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, body::LocalSchedulersModel; _mediaType=nothing) -> Channel{ LocalSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **add_resource_requirements**
> add_resource_requirements(_api::DefaultApi, workflow::String, body::ResourceRequirementsModel; _mediaType=nothing) -> ResourceRequirementsModel, OpenAPI.Clients.ApiResponse <br/>
> add_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String, body::ResourceRequirementsModel; _mediaType=nothing) -> Channel{ ResourceRequirementsModel }, OpenAPI.Clients.ApiResponse

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

# **add_result**
> add_result(_api::DefaultApi, workflow::String, body::ResultsModel; _mediaType=nothing) -> ResultsModel, OpenAPI.Clients.ApiResponse <br/>
> add_result(_api::DefaultApi, response_stream::Channel, workflow::String, body::ResultsModel; _mediaType=nothing) -> Channel{ ResultsModel }, OpenAPI.Clients.ApiResponse

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

# **add_scheduled_compute_node**
> add_scheduled_compute_node(_api::DefaultApi, workflow::String, body::ScheduledComputeNodesModel; _mediaType=nothing) -> ScheduledComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> add_scheduled_compute_node(_api::DefaultApi, response_stream::Channel, workflow::String, body::ScheduledComputeNodesModel; _mediaType=nothing) -> Channel{ ScheduledComputeNodesModel }, OpenAPI.Clients.ApiResponse

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

# **add_slurm_scheduler**
> add_slurm_scheduler(_api::DefaultApi, workflow::String, body::SlurmSchedulersModel; _mediaType=nothing) -> SlurmSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> add_slurm_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, body::SlurmSchedulersModel; _mediaType=nothing) -> Channel{ SlurmSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **add_user_data**
> add_user_data(_api::DefaultApi, workflow::String, body::UserDataModel; _mediaType=nothing) -> UserDataModel, OpenAPI.Clients.ApiResponse <br/>
> add_user_data(_api::DefaultApi, response_stream::Channel, workflow::String, body::UserDataModel; _mediaType=nothing) -> Channel{ UserDataModel }, OpenAPI.Clients.ApiResponse

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

# **add_workflow**
> add_workflow(_api::DefaultApi, body::WorkflowsModel; _mediaType=nothing) -> WorkflowsModel, OpenAPI.Clients.ApiResponse <br/>
> add_workflow(_api::DefaultApi, response_stream::Channel, body::WorkflowsModel; _mediaType=nothing) -> Channel{ WorkflowsModel }, OpenAPI.Clients.ApiResponse

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

# **add_workflow_specification**
> add_workflow_specification(_api::DefaultApi, body::WorkflowSpecificationsModel; _mediaType=nothing) -> WorkflowsModel, OpenAPI.Clients.ApiResponse <br/>
> add_workflow_specification(_api::DefaultApi, response_stream::Channel, body::WorkflowSpecificationsModel; _mediaType=nothing) -> Channel{ WorkflowsModel }, OpenAPI.Clients.ApiResponse

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

# **auto_tune_resource_requirements**
> auto_tune_resource_requirements(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> auto_tune_resource_requirements(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **cancel_workflow**
> cancel_workflow(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> cancel_workflow(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **complete_job**
> complete_job(_api::DefaultApi, workflow::String, key::String, status::String, rev::String, run_id::Int64, body::ResultsModel; _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> complete_job(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, status::String, rev::String, run_id::Int64, body::ResultsModel; _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

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

# **delete_aws_schedulers**
> delete_aws_schedulers(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_aws_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_compute_node_stats**
> delete_compute_node_stats(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_compute_node_stats(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_compute_nodes**
> delete_compute_nodes(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_compute_nodes(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_edges**
> delete_edges(_api::DefaultApi, workflow::String, name::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_edges(_api::DefaultApi, response_stream::Channel, workflow::String, name::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_events**
> delete_events(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_events(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_files**
> delete_files(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_files(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_job_process_stats**
> delete_job_process_stats(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_job_process_stats(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_jobs**
> delete_jobs(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_jobs(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_local_schedulers**
> delete_local_schedulers(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_local_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_resource_requirements**
> delete_resource_requirements(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_results**
> delete_results(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_results(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_scheduled_compute_nodes**
> delete_scheduled_compute_nodes(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_scheduled_compute_nodes(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_slurm_schedulers**
> delete_slurm_schedulers(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_slurm_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **delete_user_data**
> delete_user_data(_api::DefaultApi, workflow::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> delete_user_data(_api::DefaultApi, response_stream::Channel, workflow::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **get_aws_scheduler**
> get_aws_scheduler(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> AwsSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> get_aws_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ AwsSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **get_compute_node**
> get_compute_node(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> get_compute_node(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ComputeNodesModel }, OpenAPI.Clients.ApiResponse

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

# **get_compute_node_stats**
> get_compute_node_stats(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ComputeNodeStatsModel, OpenAPI.Clients.ApiResponse <br/>
> get_compute_node_stats(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ComputeNodeStatsModel }, OpenAPI.Clients.ApiResponse

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

# **get_dot_graph**
> get_dot_graph(_api::DefaultApi, key::String, name::String; _mediaType=nothing) -> GetWorkflowsKeyDotGraphNameResponse, OpenAPI.Clients.ApiResponse <br/>
> get_dot_graph(_api::DefaultApi, response_stream::Channel, key::String, name::String; _mediaType=nothing) -> Channel{ GetWorkflowsKeyDotGraphNameResponse }, OpenAPI.Clients.ApiResponse

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

# **get_edge**
> get_edge(_api::DefaultApi, workflow::String, name::String, key::String; _mediaType=nothing) -> EdgesNameModel, OpenAPI.Clients.ApiResponse <br/>
> get_edge(_api::DefaultApi, response_stream::Channel, workflow::String, name::String, key::String; _mediaType=nothing) -> Channel{ EdgesNameModel }, OpenAPI.Clients.ApiResponse

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

# **get_event**
> get_event(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> get_event(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **get_events_after_timestamp**
> get_events_after_timestamp(_api::DefaultApi, key::String, timestamp::Float64; category=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> ListEventsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_events_after_timestamp(_api::DefaultApi, response_stream::Channel, key::String, timestamp::Float64; category=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ ListEventsResponse }, OpenAPI.Clients.ApiResponse

Return all events newer than the event with event_key.

Return all events newer than the event with event_key.

### Required Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **_api** | **DefaultApi** | API context | 
**key** | **String**| Workflow key | [default to nothing]
**timestamp** | **Float64**| Timestamp expressed as number of milliseconds since the epoch in UTC | [default to nothing]

### Optional Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **category** | **String**|  | [default to &quot;null&quot;]
 **skip** | **Float64**| Ignored | [default to 0.0]
 **limit** | **Float64**|  | [default to 100000.0]

### Return type

[**ListEventsResponse**](ListEventsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **get_file**
> get_file(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> FilesModel, OpenAPI.Clients.ApiResponse <br/>
> get_file(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ FilesModel }, OpenAPI.Clients.ApiResponse

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

# **get_job**
> get_job(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> get_job(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

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

# **get_job_process_stats**
> get_job_process_stats(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> JobProcessStatsModel, OpenAPI.Clients.ApiResponse <br/>
> get_job_process_stats(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ JobProcessStatsModel }, OpenAPI.Clients.ApiResponse

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

# **get_job_resource_requirements**
> get_job_resource_requirements(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ResourceRequirementsModel, OpenAPI.Clients.ApiResponse <br/>
> get_job_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ResourceRequirementsModel }, OpenAPI.Clients.ApiResponse

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

# **get_job_specification**
> get_job_specification(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> JobSpecificationsModel, OpenAPI.Clients.ApiResponse <br/>
> get_job_specification(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ JobSpecificationsModel }, OpenAPI.Clients.ApiResponse

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

# **get_latest_event_timestamp**
> get_latest_event_timestamp(_api::DefaultApi, key::String; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> get_latest_event_timestamp(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

Return the timestamp of the latest event.

Return the timestamp of the latest event in ms since the epoch in UTC.

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

# **get_latest_job_result**
> get_latest_job_result(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ResultsModel, OpenAPI.Clients.ApiResponse <br/>
> get_latest_job_result(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ResultsModel }, OpenAPI.Clients.ApiResponse

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

# **get_local_scheduler**
> get_local_scheduler(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> LocalSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> get_local_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ LocalSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **get_process_stats_for_job**
> get_process_stats_for_job(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> Vector{JobProcessStatsModel}, OpenAPI.Clients.ApiResponse <br/>
> get_process_stats_for_job(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ Vector{JobProcessStatsModel} }, OpenAPI.Clients.ApiResponse

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

# **get_ready_job_requirements**
> get_ready_job_requirements(_api::DefaultApi, key::String; scheduler_config_id=nothing, _mediaType=nothing) -> GetWorkflowsKeyReadyJobRequirementsResponse, OpenAPI.Clients.ApiResponse <br/>
> get_ready_job_requirements(_api::DefaultApi, response_stream::Channel, key::String; scheduler_config_id=nothing, _mediaType=nothing) -> Channel{ GetWorkflowsKeyReadyJobRequirementsResponse }, OpenAPI.Clients.ApiResponse

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

# **get_resource_requirements**
> get_resource_requirements(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ResourceRequirementsModel, OpenAPI.Clients.ApiResponse <br/>
> get_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ResourceRequirementsModel }, OpenAPI.Clients.ApiResponse

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

# **get_result**
> get_result(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ResultsModel, OpenAPI.Clients.ApiResponse <br/>
> get_result(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ResultsModel }, OpenAPI.Clients.ApiResponse

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

# **get_scheduled_compute_node**
> get_scheduled_compute_node(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> ScheduledComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> get_scheduled_compute_node(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ ScheduledComputeNodesModel }, OpenAPI.Clients.ApiResponse

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

# **get_slurm_scheduler**
> get_slurm_scheduler(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> SlurmSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> get_slurm_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ SlurmSchedulersModel }, OpenAPI.Clients.ApiResponse

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
> get_user_data(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> UserDataModel, OpenAPI.Clients.ApiResponse <br/>
> get_user_data(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ UserDataModel }, OpenAPI.Clients.ApiResponse

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

# **get_workflow**
> get_workflow(_api::DefaultApi, key::String; _mediaType=nothing) -> WorkflowsModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflow(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ WorkflowsModel }, OpenAPI.Clients.ApiResponse

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

# **get_workflow_config**
> get_workflow_config(_api::DefaultApi, key::String; _mediaType=nothing) -> WorkflowConfigModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflow_config(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ WorkflowConfigModel }, OpenAPI.Clients.ApiResponse

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

# **get_workflow_specification**
> get_workflow_specification(_api::DefaultApi, key::String; _mediaType=nothing) -> WorkflowSpecificationsModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflow_specification(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ WorkflowSpecificationsModel }, OpenAPI.Clients.ApiResponse

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

# **get_workflow_specification_example**
> get_workflow_specification_example(_api::DefaultApi; _mediaType=nothing) -> WorkflowSpecificationsModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflow_specification_example(_api::DefaultApi, response_stream::Channel; _mediaType=nothing) -> Channel{ WorkflowSpecificationsModel }, OpenAPI.Clients.ApiResponse

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

# **get_workflow_specification_template**
> get_workflow_specification_template(_api::DefaultApi; _mediaType=nothing) -> WorkflowSpecificationsModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflow_specification_template(_api::DefaultApi, response_stream::Channel; _mediaType=nothing) -> Channel{ WorkflowSpecificationsModel }, OpenAPI.Clients.ApiResponse

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

# **get_workflow_status**
> get_workflow_status(_api::DefaultApi, key::String; _mediaType=nothing) -> WorkflowStatusModel, OpenAPI.Clients.ApiResponse <br/>
> get_workflow_status(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ WorkflowStatusModel }, OpenAPI.Clients.ApiResponse

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

# **initialize_jobs**
> initialize_jobs(_api::DefaultApi, key::String; only_uninitialized=nothing, clear_ephemeral_user_data=nothing, body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> initialize_jobs(_api::DefaultApi, response_stream::Channel, key::String; only_uninitialized=nothing, clear_ephemeral_user_data=nothing, body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **is_workflow_complete**
> is_workflow_complete(_api::DefaultApi, key::String; _mediaType=nothing) -> GetWorkflowsKeyIsCompleteResponse, OpenAPI.Clients.ApiResponse <br/>
> is_workflow_complete(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ GetWorkflowsKeyIsCompleteResponse }, OpenAPI.Clients.ApiResponse

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

# **join_collections_by_inbound_edge**
> join_collections_by_inbound_edge(_api::DefaultApi, key::String, collection::String, edge::String, body::Any; collection_key=nothing, collection_name=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> PostWorkflowsKeyJoinByInboundEdgeCollectionEdgeResponse, OpenAPI.Clients.ApiResponse <br/>
> join_collections_by_inbound_edge(_api::DefaultApi, response_stream::Channel, key::String, collection::String, edge::String, body::Any; collection_key=nothing, collection_name=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyJoinByInboundEdgeCollectionEdgeResponse }, OpenAPI.Clients.ApiResponse

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

# **join_collections_by_outbound_edge**
> join_collections_by_outbound_edge(_api::DefaultApi, key::String, collection::String, edge::String, body::Any; collection_key=nothing, collection_name=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> PostWorkflowsKeyJoinByOutboundEdgeCollectionEdgeResponse, OpenAPI.Clients.ApiResponse <br/>
> join_collections_by_outbound_edge(_api::DefaultApi, response_stream::Channel, key::String, collection::String, edge::String, body::Any; collection_key=nothing, collection_name=nothing, skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyJoinByOutboundEdgeCollectionEdgeResponse }, OpenAPI.Clients.ApiResponse

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

# **list_aws_schedulers**
> list_aws_schedulers(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, _mediaType=nothing) -> GetAwsSchedulersResponse, OpenAPI.Clients.ApiResponse <br/>
> list_aws_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, _mediaType=nothing) -> Channel{ GetAwsSchedulersResponse }, OpenAPI.Clients.ApiResponse

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

# **list_collection_names**
> list_collection_names(_api::DefaultApi, key::String; _mediaType=nothing) -> GetWorkflowsKeyCollectionNamesResponse, OpenAPI.Clients.ApiResponse <br/>
> list_collection_names(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ GetWorkflowsKeyCollectionNamesResponse }, OpenAPI.Clients.ApiResponse

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

# **list_compute_node_stats**
> list_compute_node_stats(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, hostname=nothing, _mediaType=nothing) -> ListComputeNodeStatsResponse, OpenAPI.Clients.ApiResponse <br/>
> list_compute_node_stats(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, hostname=nothing, _mediaType=nothing) -> Channel{ ListComputeNodeStatsResponse }, OpenAPI.Clients.ApiResponse

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

[**ListComputeNodeStatsResponse**](ListComputeNodeStatsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **list_compute_nodes**
> list_compute_nodes(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, hostname=nothing, is_active=nothing, _mediaType=nothing) -> GetComputeNodesResponse, OpenAPI.Clients.ApiResponse <br/>
> list_compute_nodes(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, hostname=nothing, is_active=nothing, _mediaType=nothing) -> Channel{ GetComputeNodesResponse }, OpenAPI.Clients.ApiResponse

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

# **list_edges**
> list_edges(_api::DefaultApi, workflow::String, name::String; skip=nothing, limit=nothing, _mediaType=nothing) -> GetEdgesNameResponse, OpenAPI.Clients.ApiResponse <br/>
> list_edges(_api::DefaultApi, response_stream::Channel, workflow::String, name::String; skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetEdgesNameResponse }, OpenAPI.Clients.ApiResponse

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

# **list_events**
> list_events(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, category=nothing, _mediaType=nothing) -> ListEventsResponse, OpenAPI.Clients.ApiResponse <br/>
> list_events(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, category=nothing, _mediaType=nothing) -> Channel{ ListEventsResponse }, OpenAPI.Clients.ApiResponse

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

[**ListEventsResponse**](ListEventsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **list_files**
> list_files(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, path=nothing, _mediaType=nothing) -> ListFilesResponse, OpenAPI.Clients.ApiResponse <br/>
> list_files(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, path=nothing, _mediaType=nothing) -> Channel{ ListFilesResponse }, OpenAPI.Clients.ApiResponse

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

[**ListFilesResponse**](ListFilesResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **list_files_produced_by_job**
> list_files_produced_by_job(_api::DefaultApi, workflow::String, key::String; skip=nothing, limit=nothing, _mediaType=nothing) -> GetFilesProducedByJobKeyResponse, OpenAPI.Clients.ApiResponse <br/>
> list_files_produced_by_job(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetFilesProducedByJobKeyResponse }, OpenAPI.Clients.ApiResponse

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

# **list_job_keys**
> list_job_keys(_api::DefaultApi, workflow::String; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> list_job_keys(_api::DefaultApi, response_stream::Channel, workflow::String; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **list_job_process_stats**
> list_job_process_stats(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, job_key=nothing, run_id=nothing, _mediaType=nothing) -> ListJobProcessStatsResponse, OpenAPI.Clients.ApiResponse <br/>
> list_job_process_stats(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, job_key=nothing, run_id=nothing, _mediaType=nothing) -> Channel{ ListJobProcessStatsResponse }, OpenAPI.Clients.ApiResponse

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

[**ListJobProcessStatsResponse**](ListJobProcessStatsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **list_job_specifications**
> list_job_specifications(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, _mediaType=nothing) -> GetJobSpecificationsResponse, OpenAPI.Clients.ApiResponse <br/>
> list_job_specifications(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetJobSpecificationsResponse }, OpenAPI.Clients.ApiResponse

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

# **list_job_user_data_consumes**
> list_job_user_data_consumes(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> GetJobsKeyUserDataConsumesResponse, OpenAPI.Clients.ApiResponse <br/>
> list_job_user_data_consumes(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ GetJobsKeyUserDataConsumesResponse }, OpenAPI.Clients.ApiResponse

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

# **list_job_user_data_stores**
> list_job_user_data_stores(_api::DefaultApi, workflow::String, key::String; _mediaType=nothing) -> GetJobsKeyUserDataStoresResponse, OpenAPI.Clients.ApiResponse <br/>
> list_job_user_data_stores(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; _mediaType=nothing) -> Channel{ GetJobsKeyUserDataStoresResponse }, OpenAPI.Clients.ApiResponse

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

# **list_jobs**
> list_jobs(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, command=nothing, status=nothing, cancel_on_blocking_job_failure=nothing, supports_termination=nothing, _mediaType=nothing) -> ListJobsResponse, OpenAPI.Clients.ApiResponse <br/>
> list_jobs(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, command=nothing, status=nothing, cancel_on_blocking_job_failure=nothing, supports_termination=nothing, _mediaType=nothing) -> Channel{ ListJobsResponse }, OpenAPI.Clients.ApiResponse

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

[**ListJobsResponse**](ListJobsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **list_jobs_by_needs_file**
> list_jobs_by_needs_file(_api::DefaultApi, workflow::String, key::String; skip=nothing, limit=nothing, _mediaType=nothing) -> GetJobsFindByNeedsFileKeyResponse, OpenAPI.Clients.ApiResponse <br/>
> list_jobs_by_needs_file(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetJobsFindByNeedsFileKeyResponse }, OpenAPI.Clients.ApiResponse

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

# **list_jobs_by_status**
> list_jobs_by_status(_api::DefaultApi, workflow::String, status::String; skip=nothing, limit=nothing, _mediaType=nothing) -> GetJobsFindByStatusStatusResponse, OpenAPI.Clients.ApiResponse <br/>
> list_jobs_by_status(_api::DefaultApi, response_stream::Channel, workflow::String, status::String; skip=nothing, limit=nothing, _mediaType=nothing) -> Channel{ GetJobsFindByStatusStatusResponse }, OpenAPI.Clients.ApiResponse

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

# **list_local_schedulers**
> list_local_schedulers(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, memory=nothing, num_cpus=nothing, _mediaType=nothing) -> ListLocalSchedulersResponse, OpenAPI.Clients.ApiResponse <br/>
> list_local_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, memory=nothing, num_cpus=nothing, _mediaType=nothing) -> Channel{ ListLocalSchedulersResponse }, OpenAPI.Clients.ApiResponse

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

[**ListLocalSchedulersResponse**](ListLocalSchedulersResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)

# **list_missing_user_data**
> list_missing_user_data(_api::DefaultApi, key::String; _mediaType=nothing) -> GetWorkflowsKeyMissingUserDataResponse, OpenAPI.Clients.ApiResponse <br/>
> list_missing_user_data(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ GetWorkflowsKeyMissingUserDataResponse }, OpenAPI.Clients.ApiResponse

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

# **list_required_existing_files**
> list_required_existing_files(_api::DefaultApi, key::String; _mediaType=nothing) -> GetWorkflowsKeyRequiredExistingFilesResponse, OpenAPI.Clients.ApiResponse <br/>
> list_required_existing_files(_api::DefaultApi, response_stream::Channel, key::String; _mediaType=nothing) -> Channel{ GetWorkflowsKeyRequiredExistingFilesResponse }, OpenAPI.Clients.ApiResponse

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

# **list_resource_requirements**
> list_resource_requirements(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, memory=nothing, num_cpus=nothing, num_gpus=nothing, num_nodes=nothing, runtime=nothing, _mediaType=nothing) -> GetResourceRequirementsResponse, OpenAPI.Clients.ApiResponse <br/>
> list_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, memory=nothing, num_cpus=nothing, num_gpus=nothing, num_nodes=nothing, runtime=nothing, _mediaType=nothing) -> Channel{ GetResourceRequirementsResponse }, OpenAPI.Clients.ApiResponse

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

# **list_results**
> list_results(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, job_key=nothing, run_id=nothing, return_code=nothing, status=nothing, _mediaType=nothing) -> GetResultsResponse, OpenAPI.Clients.ApiResponse <br/>
> list_results(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, job_key=nothing, run_id=nothing, return_code=nothing, status=nothing, _mediaType=nothing) -> Channel{ GetResultsResponse }, OpenAPI.Clients.ApiResponse

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

# **list_scheduled_compute_nodes**
> list_scheduled_compute_nodes(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, scheduler_id=nothing, scheduler_config_id=nothing, status=nothing, _mediaType=nothing) -> GetScheduledComputeNodesResponse, OpenAPI.Clients.ApiResponse <br/>
> list_scheduled_compute_nodes(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, scheduler_id=nothing, scheduler_config_id=nothing, status=nothing, _mediaType=nothing) -> Channel{ GetScheduledComputeNodesResponse }, OpenAPI.Clients.ApiResponse

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

# **list_slurm_schedulers**
> list_slurm_schedulers(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, account=nothing, gres=nothing, mem=nothing, nodes=nothing, partition=nothing, qos=nothing, tmp=nothing, walltime=nothing, _mediaType=nothing) -> GetSlurmSchedulersResponse, OpenAPI.Clients.ApiResponse <br/>
> list_slurm_schedulers(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, account=nothing, gres=nothing, mem=nothing, nodes=nothing, partition=nothing, qos=nothing, tmp=nothing, walltime=nothing, _mediaType=nothing) -> Channel{ GetSlurmSchedulersResponse }, OpenAPI.Clients.ApiResponse

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

# **list_user_data**
> list_user_data(_api::DefaultApi, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, is_ephemeral=nothing, _mediaType=nothing) -> GetUserDataResponse, OpenAPI.Clients.ApiResponse <br/>
> list_user_data(_api::DefaultApi, response_stream::Channel, workflow::String; skip=nothing, limit=nothing, sort_by=nothing, reverse_sort=nothing, key=nothing, name=nothing, is_ephemeral=nothing, _mediaType=nothing) -> Channel{ GetUserDataResponse }, OpenAPI.Clients.ApiResponse

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

# **list_workflows**
> list_workflows(_api::DefaultApi; skip=nothing, sort_by=nothing, reverse_sort=nothing, limit=nothing, name=nothing, user=nothing, description=nothing, _mediaType=nothing) -> GetWorkflowsResponse, OpenAPI.Clients.ApiResponse <br/>
> list_workflows(_api::DefaultApi, response_stream::Channel; skip=nothing, sort_by=nothing, reverse_sort=nothing, limit=nothing, name=nothing, user=nothing, description=nothing, _mediaType=nothing) -> Channel{ GetWorkflowsResponse }, OpenAPI.Clients.ApiResponse

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

# **manage_status_change**
> manage_status_change(_api::DefaultApi, workflow::String, key::String, status::String, rev::String, run_id::Int64; body=nothing, _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> manage_status_change(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, status::String, rev::String, run_id::Int64; body=nothing, _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

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

# **modify_aws_scheduler**
> modify_aws_scheduler(_api::DefaultApi, workflow::String, key::String, body::AwsSchedulersModel; _mediaType=nothing) -> AwsSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> modify_aws_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::AwsSchedulersModel; _mediaType=nothing) -> Channel{ AwsSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **modify_compute_node**
> modify_compute_node(_api::DefaultApi, workflow::String, key::String, body::ComputeNodesModel; _mediaType=nothing) -> ComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> modify_compute_node(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::ComputeNodesModel; _mediaType=nothing) -> Channel{ ComputeNodesModel }, OpenAPI.Clients.ApiResponse

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

# **modify_compute_node_stats**
> modify_compute_node_stats(_api::DefaultApi, workflow::String, key::String, body::ComputeNodeStatsModel; _mediaType=nothing) -> ComputeNodeStatsModel, OpenAPI.Clients.ApiResponse <br/>
> modify_compute_node_stats(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::ComputeNodeStatsModel; _mediaType=nothing) -> Channel{ ComputeNodeStatsModel }, OpenAPI.Clients.ApiResponse

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

# **modify_event**
> modify_event(_api::DefaultApi, workflow::String, key::String, body::Any; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> modify_event(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::Any; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **modify_file**
> modify_file(_api::DefaultApi, workflow::String, key::String, body::FilesModel; _mediaType=nothing) -> FilesModel, OpenAPI.Clients.ApiResponse <br/>
> modify_file(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::FilesModel; _mediaType=nothing) -> Channel{ FilesModel }, OpenAPI.Clients.ApiResponse

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

# **modify_job**
> modify_job(_api::DefaultApi, workflow::String, key::String, body::JobsModel; _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> modify_job(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::JobsModel; _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

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

# **modify_job_process_stats**
> modify_job_process_stats(_api::DefaultApi, workflow::String, key::String, body::JobProcessStatsModel; _mediaType=nothing) -> JobProcessStatsModel, OpenAPI.Clients.ApiResponse <br/>
> modify_job_process_stats(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::JobProcessStatsModel; _mediaType=nothing) -> Channel{ JobProcessStatsModel }, OpenAPI.Clients.ApiResponse

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

# **modify_job_resource_requirements**
> modify_job_resource_requirements(_api::DefaultApi, workflow::String, key::String, rr_key::String; body=nothing, _mediaType=nothing) -> EdgesNameModel, OpenAPI.Clients.ApiResponse <br/>
> modify_job_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, rr_key::String; body=nothing, _mediaType=nothing) -> Channel{ EdgesNameModel }, OpenAPI.Clients.ApiResponse

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

# **modify_local_scheduler**
> modify_local_scheduler(_api::DefaultApi, workflow::String, key::String, body::LocalSchedulersModel; _mediaType=nothing) -> LocalSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> modify_local_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::LocalSchedulersModel; _mediaType=nothing) -> Channel{ LocalSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **modify_resource_requirements**
> modify_resource_requirements(_api::DefaultApi, workflow::String, key::String, body::ResourceRequirementsModel; _mediaType=nothing) -> ResourceRequirementsModel, OpenAPI.Clients.ApiResponse <br/>
> modify_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::ResourceRequirementsModel; _mediaType=nothing) -> Channel{ ResourceRequirementsModel }, OpenAPI.Clients.ApiResponse

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

# **modify_result**
> modify_result(_api::DefaultApi, workflow::String, key::String, body::ResultsModel; _mediaType=nothing) -> ResultsModel, OpenAPI.Clients.ApiResponse <br/>
> modify_result(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::ResultsModel; _mediaType=nothing) -> Channel{ ResultsModel }, OpenAPI.Clients.ApiResponse

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

# **modify_scheduled_compute_node**
> modify_scheduled_compute_node(_api::DefaultApi, workflow::String, key::String, body::ScheduledComputeNodesModel; _mediaType=nothing) -> ScheduledComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> modify_scheduled_compute_node(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::ScheduledComputeNodesModel; _mediaType=nothing) -> Channel{ ScheduledComputeNodesModel }, OpenAPI.Clients.ApiResponse

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

# **modify_slurm_scheduler**
> modify_slurm_scheduler(_api::DefaultApi, workflow::String, key::String, body::SlurmSchedulersModel; _mediaType=nothing) -> SlurmSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> modify_slurm_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::SlurmSchedulersModel; _mediaType=nothing) -> Channel{ SlurmSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **modify_user_data**
> modify_user_data(_api::DefaultApi, workflow::String, key::String, body::UserDataModel; _mediaType=nothing) -> UserDataModel, OpenAPI.Clients.ApiResponse <br/>
> modify_user_data(_api::DefaultApi, response_stream::Channel, workflow::String, key::String, body::UserDataModel; _mediaType=nothing) -> Channel{ UserDataModel }, OpenAPI.Clients.ApiResponse

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

# **modify_workflow**
> modify_workflow(_api::DefaultApi, key::String, body::WorkflowsModel; _mediaType=nothing) -> WorkflowsModel, OpenAPI.Clients.ApiResponse <br/>
> modify_workflow(_api::DefaultApi, response_stream::Channel, key::String, body::WorkflowsModel; _mediaType=nothing) -> Channel{ WorkflowsModel }, OpenAPI.Clients.ApiResponse

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

# **modify_workflow_config**
> modify_workflow_config(_api::DefaultApi, key::String, body::WorkflowConfigModel; _mediaType=nothing) -> WorkflowConfigModel, OpenAPI.Clients.ApiResponse <br/>
> modify_workflow_config(_api::DefaultApi, response_stream::Channel, key::String, body::WorkflowConfigModel; _mediaType=nothing) -> Channel{ WorkflowConfigModel }, OpenAPI.Clients.ApiResponse

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

# **modify_workflow_status**
> modify_workflow_status(_api::DefaultApi, key::String, body::WorkflowStatusModel; _mediaType=nothing) -> WorkflowStatusModel, OpenAPI.Clients.ApiResponse <br/>
> modify_workflow_status(_api::DefaultApi, response_stream::Channel, key::String, body::WorkflowStatusModel; _mediaType=nothing) -> Channel{ WorkflowStatusModel }, OpenAPI.Clients.ApiResponse

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

# **ping**
> ping(_api::DefaultApi; _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> ping(_api::DefaultApi, response_stream::Channel; _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **prepare_jobs_for_scheduling**
> prepare_jobs_for_scheduling(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> PostWorkflowsKeyPrepareJobsForSchedulingResponse, OpenAPI.Clients.ApiResponse <br/>
> prepare_jobs_for_scheduling(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyPrepareJobsForSchedulingResponse }, OpenAPI.Clients.ApiResponse

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

# **prepare_jobs_for_submission**
> prepare_jobs_for_submission(_api::DefaultApi, key::String, body::ComputeNodesResources; sort_method=nothing, limit=nothing, _mediaType=nothing) -> PostWorkflowsKeyPrepareJobsForSubmissionResponse, OpenAPI.Clients.ApiResponse <br/>
> prepare_jobs_for_submission(_api::DefaultApi, response_stream::Channel, key::String, body::ComputeNodesResources; sort_method=nothing, limit=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyPrepareJobsForSubmissionResponse }, OpenAPI.Clients.ApiResponse

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

# **prepare_next_jobs_for_submission**
> prepare_next_jobs_for_submission(_api::DefaultApi, key::String; limit=nothing, body=nothing, _mediaType=nothing) -> PostWorkflowsKeyPrepareNextJobsForSubmissionResponse, OpenAPI.Clients.ApiResponse <br/>
> prepare_next_jobs_for_submission(_api::DefaultApi, response_stream::Channel, key::String; limit=nothing, body=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyPrepareNextJobsForSubmissionResponse }, OpenAPI.Clients.ApiResponse

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

# **process_auto_tune_resource_requirements_results**
> process_auto_tune_resource_requirements_results(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> process_auto_tune_resource_requirements_results(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **process_changed_job_inputs**
> process_changed_job_inputs(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> PostWorkflowsKeyProcessChangedJobInputsResponse, OpenAPI.Clients.ApiResponse <br/>
> process_changed_job_inputs(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ PostWorkflowsKeyProcessChangedJobInputsResponse }, OpenAPI.Clients.ApiResponse

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

# **remove_aws_scheduler**
> remove_aws_scheduler(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> AwsSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> remove_aws_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ AwsSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **remove_compute_node**
> remove_compute_node(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> ComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> remove_compute_node(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ ComputeNodesModel }, OpenAPI.Clients.ApiResponse

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

# **remove_compute_node_stats**
> remove_compute_node_stats(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> ComputeNodeStatsModel, OpenAPI.Clients.ApiResponse <br/>
> remove_compute_node_stats(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ ComputeNodeStatsModel }, OpenAPI.Clients.ApiResponse

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

# **remove_edge**
> remove_edge(_api::DefaultApi, workflow::String, name::String, key::String; body=nothing, _mediaType=nothing) -> EdgesNameModel, OpenAPI.Clients.ApiResponse <br/>
> remove_edge(_api::DefaultApi, response_stream::Channel, workflow::String, name::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ EdgesNameModel }, OpenAPI.Clients.ApiResponse

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

# **remove_event**
> remove_event(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> remove_event(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **remove_file**
> remove_file(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> FilesModel, OpenAPI.Clients.ApiResponse <br/>
> remove_file(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ FilesModel }, OpenAPI.Clients.ApiResponse

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

# **remove_job**
> remove_job(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> JobsModel, OpenAPI.Clients.ApiResponse <br/>
> remove_job(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ JobsModel }, OpenAPI.Clients.ApiResponse

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

# **remove_job_process_stats**
> remove_job_process_stats(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> JobProcessStatsModel, OpenAPI.Clients.ApiResponse <br/>
> remove_job_process_stats(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ JobProcessStatsModel }, OpenAPI.Clients.ApiResponse

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

# **remove_local_scheduler**
> remove_local_scheduler(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> LocalSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> remove_local_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ LocalSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **remove_resource_requirements**
> remove_resource_requirements(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> ResourceRequirementsModel, OpenAPI.Clients.ApiResponse <br/>
> remove_resource_requirements(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ ResourceRequirementsModel }, OpenAPI.Clients.ApiResponse

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

# **remove_result**
> remove_result(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> ResultsModel, OpenAPI.Clients.ApiResponse <br/>
> remove_result(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ ResultsModel }, OpenAPI.Clients.ApiResponse

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

# **remove_scheduled_compute_node**
> remove_scheduled_compute_node(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> ScheduledComputeNodesModel, OpenAPI.Clients.ApiResponse <br/>
> remove_scheduled_compute_node(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ ScheduledComputeNodesModel }, OpenAPI.Clients.ApiResponse

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

# **remove_slurm_scheduler**
> remove_slurm_scheduler(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> SlurmSchedulersModel, OpenAPI.Clients.ApiResponse <br/>
> remove_slurm_scheduler(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ SlurmSchedulersModel }, OpenAPI.Clients.ApiResponse

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

# **remove_user_data**
> remove_user_data(_api::DefaultApi, workflow::String, key::String; body=nothing, _mediaType=nothing) -> UserDataModel, OpenAPI.Clients.ApiResponse <br/>
> remove_user_data(_api::DefaultApi, response_stream::Channel, workflow::String, key::String; body=nothing, _mediaType=nothing) -> Channel{ UserDataModel }, OpenAPI.Clients.ApiResponse

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

# **remove_workflow**
> remove_workflow(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> WorkflowsModel, OpenAPI.Clients.ApiResponse <br/>
> remove_workflow(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ WorkflowsModel }, OpenAPI.Clients.ApiResponse

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

# **reset_job_status**
> reset_job_status(_api::DefaultApi, key::String; failed_only=nothing, body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> reset_job_status(_api::DefaultApi, response_stream::Channel, key::String; failed_only=nothing, body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

# **reset_workflow_status**
> reset_workflow_status(_api::DefaultApi, key::String; body=nothing, _mediaType=nothing) -> Any, OpenAPI.Clients.ApiResponse <br/>
> reset_workflow_status(_api::DefaultApi, response_stream::Channel, key::String; body=nothing, _mediaType=nothing) -> Channel{ Any }, OpenAPI.Clients.ApiResponse

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

