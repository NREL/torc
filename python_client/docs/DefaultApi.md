# swagger_client.DefaultApi

All URIs are relative to */_db/workflows/wms-service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_blocks**](DefaultApi.md#delete_blocks) | **DELETE** /blocks | Delete all blocks edges
[**delete_blocks_key**](DefaultApi.md#delete_blocks_key) | **DELETE** /blocks/{key} | Delete a block
[**delete_events**](DefaultApi.md#delete_events) | **DELETE** /events | Delete all events
[**delete_events_key**](DefaultApi.md#delete_events_key) | **DELETE** /events/{key} | Delete an event
[**delete_files**](DefaultApi.md#delete_files) | **DELETE** /files | Delete all files
[**delete_files_name**](DefaultApi.md#delete_files_name) | **DELETE** /files/{name} | Delete a file
[**delete_hpc_configs**](DefaultApi.md#delete_hpc_configs) | **DELETE** /hpc_configs | Delete all hpc_configs
[**delete_hpc_configs_name**](DefaultApi.md#delete_hpc_configs_name) | **DELETE** /hpc_configs/{name} | Delete a hpc_config
[**delete_jobs**](DefaultApi.md#delete_jobs) | **DELETE** /jobs | Delete all jobs
[**delete_jobs_name**](DefaultApi.md#delete_jobs_name) | **DELETE** /jobs/{name} | Delete a job
[**delete_needs**](DefaultApi.md#delete_needs) | **DELETE** /needs | Delete all needs edges
[**delete_needs_key**](DefaultApi.md#delete_needs_key) | **DELETE** /needs/{key} | Delete a need
[**delete_produces**](DefaultApi.md#delete_produces) | **DELETE** /produces | Delete all produces edges
[**delete_produces_key**](DefaultApi.md#delete_produces_key) | **DELETE** /produces/{key} | Delete a produces edge
[**delete_requires**](DefaultApi.md#delete_requires) | **DELETE** /requires | Delete all requires edges
[**delete_requires_key**](DefaultApi.md#delete_requires_key) | **DELETE** /requires/{key} | Delete a require
[**delete_resource_requirements**](DefaultApi.md#delete_resource_requirements) | **DELETE** /resource_requirements | Delete all resource_requirements
[**delete_resource_requirements_name**](DefaultApi.md#delete_resource_requirements_name) | **DELETE** /resource_requirements/{name} | Delete a resource
[**delete_results**](DefaultApi.md#delete_results) | **DELETE** /results | Delete all results
[**delete_results_key**](DefaultApi.md#delete_results_key) | **DELETE** /results/{key} | Delete a result
[**delete_returned**](DefaultApi.md#delete_returned) | **DELETE** /returned | Delete all returned edges
[**delete_returned_key**](DefaultApi.md#delete_returned_key) | **DELETE** /returned/{key} | Delete an edge
[**delete_scheduled_bys**](DefaultApi.md#delete_scheduled_bys) | **DELETE** /scheduled_bys | Delete all scheduled_by edges
[**delete_scheduled_bys_key**](DefaultApi.md#delete_scheduled_bys_key) | **DELETE** /scheduled_bys/{key} | Delete a scheduled_by
[**delete_stores**](DefaultApi.md#delete_stores) | **DELETE** /stores | Delete all stores edges
[**delete_stores_key**](DefaultApi.md#delete_stores_key) | **DELETE** /stores/{key} | Delete a stores edge
[**delete_user_data**](DefaultApi.md#delete_user_data) | **DELETE** /user_data | Delete all user data
[**delete_user_data_key**](DefaultApi.md#delete_user_data_key) | **DELETE** /user_data/{key} | Delete a user data object
[**delete_workflow**](DefaultApi.md#delete_workflow) | **DELETE** /workflow | Delete the workflow.
[**get_blocks**](DefaultApi.md#get_blocks) | **GET** /blocks | Retrieve all blocks edges
[**get_blocks_key**](DefaultApi.md#get_blocks_key) | **GET** /blocks/{key} | Retrieve a blocks edge
[**get_events**](DefaultApi.md#get_events) | **GET** /events | Retrieve all events
[**get_events_key**](DefaultApi.md#get_events_key) | **GET** /events/{key} | Retrieve the event for a key.
[**get_files**](DefaultApi.md#get_files) | **GET** /files | Retrieve all files
[**get_files_name**](DefaultApi.md#get_files_name) | **GET** /files/{name} | Retrieve a file
[**get_files_produced_by_job_name**](DefaultApi.md#get_files_produced_by_job_name) | **GET** /files/produced_by_job/{name} | Retrieve files produced by a job
[**get_hpc_configs**](DefaultApi.md#get_hpc_configs) | **GET** /hpc_configs | Retrieve all hpc_configs
[**get_hpc_configs_name**](DefaultApi.md#get_hpc_configs_name) | **GET** /hpc_configs/{name} | Retrieve an hpc_config document by name
[**get_job_definitions**](DefaultApi.md#get_job_definitions) | **GET** /job_definitions | Retrieve all job definitions
[**get_job_definitions_name**](DefaultApi.md#get_job_definitions_name) | **GET** /job_definitions/{name} | Retrieve a job
[**get_job_names**](DefaultApi.md#get_job_names) | **GET** /job_names | Retrieve all job names
[**get_jobs**](DefaultApi.md#get_jobs) | **GET** /jobs | Retrieve all jobs
[**get_jobs_find_by_needs_file_name**](DefaultApi.md#get_jobs_find_by_needs_file_name) | **GET** /jobs/find_by_needs_file/{name} | Retrieve all jobs that need a file
[**get_jobs_find_by_status_status**](DefaultApi.md#get_jobs_find_by_status_status) | **GET** /jobs/find_by_status/{status} | Retrieve all jobs with a specific status
[**get_jobs_get_user_data_name**](DefaultApi.md#get_jobs_get_user_data_name) | **GET** /jobs/get_user_data/{name} | Retrieve all user data for a job.
[**get_jobs_name**](DefaultApi.md#get_jobs_name) | **GET** /jobs/{name} | Retrieve a job
[**get_jobs_resource_requirements_name**](DefaultApi.md#get_jobs_resource_requirements_name) | **GET** /jobs/resource_requirements/{name} | Retrieve the resource requirements for a job.
[**get_needs**](DefaultApi.md#get_needs) | **GET** /needs | Retrieve all needs
[**get_needs_key**](DefaultApi.md#get_needs_key) | **GET** /needs/{key} | Retrieve a needs edge
[**get_produces**](DefaultApi.md#get_produces) | **GET** /produces | Retrieve all produces edges
[**get_produces_key**](DefaultApi.md#get_produces_key) | **GET** /produces/{key} | Retrieve a produces edge
[**get_requires**](DefaultApi.md#get_requires) | **GET** /requires | Retrieve all requires
[**get_requires_key**](DefaultApi.md#get_requires_key) | **GET** /requires/{key} | Retrieve a require
[**get_resource_requirements**](DefaultApi.md#get_resource_requirements) | **GET** /resource_requirements | Retrieve all resource requirements
[**get_resource_requirements_name**](DefaultApi.md#get_resource_requirements_name) | **GET** /resource_requirements/{name} | Retrieve a resource requirements document by name
[**get_results**](DefaultApi.md#get_results) | **GET** /results | Retrieve all results
[**get_results_find_by_job_name_name**](DefaultApi.md#get_results_find_by_job_name_name) | **GET** /results/find_by_job_name/{name} | Retrieve the latest result for a job
[**get_results_key**](DefaultApi.md#get_results_key) | **GET** /results/{key} | Retrieve the result for a key.
[**get_returned**](DefaultApi.md#get_returned) | **GET** /returned | Retrieve all returned
[**get_returned_key**](DefaultApi.md#get_returned_key) | **GET** /returned/{key} | Retrieve a returned edge
[**get_scheduled_bys**](DefaultApi.md#get_scheduled_bys) | **GET** /scheduled_bys | Retrieve all scheduled_by edges
[**get_scheduled_bys_key**](DefaultApi.md#get_scheduled_bys_key) | **GET** /scheduled_bys/{key} | Retrieve a scheduled_by edge
[**get_stores**](DefaultApi.md#get_stores) | **GET** /stores | Retrieve all stores edges
[**get_stores_key**](DefaultApi.md#get_stores_key) | **GET** /stores/{key} | Retrieve a stores edge
[**get_user_data**](DefaultApi.md#get_user_data) | **GET** /user_data | Retrieve all user data objects
[**get_user_data_key**](DefaultApi.md#get_user_data_key) | **GET** /user_data/{key} | Retrieve the user data object for a key.
[**get_workflow**](DefaultApi.md#get_workflow) | **GET** /workflow | Retrieve the current workflow
[**get_workflow_example**](DefaultApi.md#get_workflow_example) | **GET** /workflow/example | Retrieve an example workflow
[**get_workflow_is_complete**](DefaultApi.md#get_workflow_is_complete) | **GET** /workflow/is_complete | Report whether the workflow is complete
[**post_blocks**](DefaultApi.md#post_blocks) | **POST** /blocks | Store a blocks edge between a job and a file.
[**post_events**](DefaultApi.md#post_events) | **POST** /events | Store an event.
[**post_files**](DefaultApi.md#post_files) | **POST** /files | Store file
[**post_hpc_configs**](DefaultApi.md#post_hpc_configs) | **POST** /hpc_configs | Store an hpc_config.
[**post_job_definitions**](DefaultApi.md#post_job_definitions) | **POST** /job_definitions | Store a job and create edges.
[**post_jobs**](DefaultApi.md#post_jobs) | **POST** /jobs | Store job
[**post_jobs_complete_job_name_status_rev**](DefaultApi.md#post_jobs_complete_job_name_status_rev) | **POST** /jobs/complete_job/{name}/{status}/{rev} | Complete a job and add a result.
[**post_jobs_store_user_data_name**](DefaultApi.md#post_jobs_store_user_data_name) | **POST** /jobs/store_user_data/{name} | Store user data for a job.
[**post_needs**](DefaultApi.md#post_needs) | **POST** /needs | Store a needs edge between a job and a file.
[**post_produces**](DefaultApi.md#post_produces) | **POST** /produces | Store a produces edge between a job and a file.
[**post_requires**](DefaultApi.md#post_requires) | **POST** /requires | Store a requires edge between a job and a resource.
[**post_resource_requirements**](DefaultApi.md#post_resource_requirements) | **POST** /resource_requirements | Store a resource.
[**post_results**](DefaultApi.md#post_results) | **POST** /results | Store a job result.
[**post_returned**](DefaultApi.md#post_returned) | **POST** /returned | Store a returned edge between a job and a result.
[**post_scheduled_bys**](DefaultApi.md#post_scheduled_bys) | **POST** /scheduled_bys | Store a scheduled_by edge between a job and an hpc_config.
[**post_stores**](DefaultApi.md#post_stores) | **POST** /stores | Store a stores edge between a job and a user data object.
[**post_user_data**](DefaultApi.md#post_user_data) | **POST** /user_data | Store user data for a job.
[**post_workflow**](DefaultApi.md#post_workflow) | **POST** /workflow | Store a workflow.
[**post_workflow_estimate**](DefaultApi.md#post_workflow_estimate) | **POST** /workflow/estimate | Perform a dry run of all jobs to estimate required resources.
[**post_workflow_initialize_jobs**](DefaultApi.md#post_workflow_initialize_jobs) | **POST** /workflow/initialize_jobs | Initialize job relationships.
[**post_workflow_prepare_jobs_for_submission**](DefaultApi.md#post_workflow_prepare_jobs_for_submission) | **POST** /workflow/prepare_jobs_for_submission | Return ready jobs
[**post_workflow_reset_status**](DefaultApi.md#post_workflow_reset_status) | **POST** /workflow/reset_status | Reset job status.
[**put_files_name**](DefaultApi.md#put_files_name) | **PUT** /files/{name} | Update file
[**put_jobs_manage_status_change_name_status_rev**](DefaultApi.md#put_jobs_manage_status_change_name_status_rev) | **PUT** /jobs/manage_status_change/{name}/{status}/{rev} | Change the status of a job and manage side effects.
[**put_jobs_name**](DefaultApi.md#put_jobs_name) | **PUT** /jobs/{name} | Update job

# **delete_blocks**
> object delete_blocks(body=body)

Delete all blocks edges

Deletes all edges from the \"blocks\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all blocks edges
    api_response = api_instance.delete_blocks(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_blocks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_blocks_key**
> BlocksEdgeModel delete_blocks_key(key, body=body)

Delete a block

Deletes a blocks edge from the \"blocks\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the block.
body = NULL # object |  (optional)

try:
    # Delete a block
    api_response = api_instance.delete_blocks_key(key, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_blocks_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the block. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**BlocksEdgeModel**](BlocksEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_events**
> object delete_events()

Delete all events

Deletes all events from the \"events\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()

try:
    # Delete all events
    api_response = api_instance.delete_events()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_events: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_events_key**
> object delete_events_key(key, body=body)

Delete an event

Deletes an event from the \"events\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the event.
body = NULL # object |  (optional)

try:
    # Delete an event
    api_response = api_instance.delete_events_key(key, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_events_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the event. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_files**
> object delete_files(body=body)

Delete all files

Deletes all files from the \"files\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all files
    api_response = api_instance.delete_files(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_files: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_files_name**
> FileModel delete_files_name(name, body=body)

Delete a file

Deletes a file from the \"files\" collection by name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | Name of the file.
body = NULL # object |  (optional)

try:
    # Delete a file
    api_response = api_instance.delete_files_name(name, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_files_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Name of the file. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**FileModel**](FileModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_hpc_configs**
> object delete_hpc_configs(body=body)

Delete all hpc_configs

Deletes all hpc_configs from the \"hpc_configs\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all hpc_configs
    api_response = api_instance.delete_hpc_configs(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_hpc_configs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_hpc_configs_name**
> HpcConfigModel delete_hpc_configs_name(name, body=body)

Delete a hpc_config

Deletes a hpc_config from the \"hpc_configs\" collection by name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | Name of the hpc_config.
body = NULL # object |  (optional)

try:
    # Delete a hpc_config
    api_response = api_instance.delete_hpc_configs_name(name, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_hpc_configs_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Name of the hpc_config. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**HpcConfigModel**](HpcConfigModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_jobs**
> object delete_jobs(body=body)

Delete all jobs

Deletes all jobs from the \"jobs\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all jobs
    api_response = api_instance.delete_jobs(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_jobs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_jobs_name**
> JobModel delete_jobs_name(name, body=body)

Delete a job

Deletes a job from the \"jobs\" collection by name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | Name of the job.
body = NULL # object |  (optional)

try:
    # Delete a job
    api_response = api_instance.delete_jobs_name(name, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_jobs_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Name of the job. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**JobModel**](JobModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_needs**
> object delete_needs(body=body)

Delete all needs edges

Deletes all edges from the \"needs\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all needs edges
    api_response = api_instance.delete_needs(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_needs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_needs_key**
> NeedsEdgeModel delete_needs_key(key, body=body)

Delete a need

Deletes a need from the \"needs\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the need.
body = NULL # object |  (optional)

try:
    # Delete a need
    api_response = api_instance.delete_needs_key(key, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_needs_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the need. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**NeedsEdgeModel**](NeedsEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_produces**
> object delete_produces(body=body)

Delete all produces edges

Deletes all edges from the \"produces\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all produces edges
    api_response = api_instance.delete_produces(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_produces: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_produces_key**
> ProducesEdgeModel delete_produces_key(key, body=body)

Delete a produces edge

Deletes a produces edge from the \"produces\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the produce edge.
body = NULL # object |  (optional)

try:
    # Delete a produces edge
    api_response = api_instance.delete_produces_key(key, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_produces_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the produce edge. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**ProducesEdgeModel**](ProducesEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_requires**
> object delete_requires(body=body)

Delete all requires edges

Deletes all edges from the \"requires\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all requires edges
    api_response = api_instance.delete_requires(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_requires: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_requires_key**
> RequiresEdgeModel delete_requires_key(key, body=body)

Delete a require

Deletes a requires edge from the \"requires\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the require.
body = NULL # object |  (optional)

try:
    # Delete a require
    api_response = api_instance.delete_requires_key(key, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_requires_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the require. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**RequiresEdgeModel**](RequiresEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_resource_requirements**
> object delete_resource_requirements(body=body)

Delete all resource_requirements

Deletes all documents from the \"resource_requirements\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all resource_requirements
    api_response = api_instance.delete_resource_requirements(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_resource_requirements: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_resource_requirements_name**
> ResourceRequirementsModel delete_resource_requirements_name(name, body=body)

Delete a resource

Deletes a resource from the \"resource_requirements\" collection by name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | Name of the resource.
body = NULL # object |  (optional)

try:
    # Delete a resource
    api_response = api_instance.delete_resource_requirements_name(name, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_resource_requirements_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Name of the resource. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**ResourceRequirementsModel**](ResourceRequirementsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_results**
> object delete_results(body=body)

Delete all results

Deletes all results from the \"results\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all results
    api_response = api_instance.delete_results(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_results: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_results_key**
> ResultModel delete_results_key(key, body=body)

Delete a result

Deletes a result from the \"results\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the result object.
body = NULL # object |  (optional)

try:
    # Delete a result
    api_response = api_instance.delete_results_key(key, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_results_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the result object. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**ResultModel**](ResultModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_returned**
> object delete_returned(body=body)

Delete all returned edges

Deletes all edges from the \"returned\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all returned edges
    api_response = api_instance.delete_returned(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_returned: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_returned_key**
> ReturnedEdgeModel delete_returned_key(key, body=body)

Delete an edge

Deletes an edge from the \"returned\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the edge.
body = NULL # object |  (optional)

try:
    # Delete an edge
    api_response = api_instance.delete_returned_key(key, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_returned_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the edge. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**ReturnedEdgeModel**](ReturnedEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_scheduled_bys**
> object delete_scheduled_bys(body=body)

Delete all scheduled_by edges

Deletes all edges from the \"scheduled_by\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all scheduled_by edges
    api_response = api_instance.delete_scheduled_bys(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_scheduled_bys: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_scheduled_bys_key**
> ScheduledByEdgeModel delete_scheduled_bys_key(key, body=body)

Delete a scheduled_by

Deletes a scheduled_by edge from the \"scheduled_by\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the scheduled_by.
body = NULL # object |  (optional)

try:
    # Delete a scheduled_by
    api_response = api_instance.delete_scheduled_bys_key(key, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_scheduled_bys_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the scheduled_by. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**ScheduledByEdgeModel**](ScheduledByEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_stores**
> object delete_stores(body=body)

Delete all stores edges

Deletes all edges from the \"stores\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all stores edges
    api_response = api_instance.delete_stores(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_stores: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_stores_key**
> StoresEdgeModel delete_stores_key(key, body=body)

Delete a stores edge

Deletes a stores edge from the \"stores\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the stores edge.
body = NULL # object |  (optional)

try:
    # Delete a stores edge
    api_response = api_instance.delete_stores_key(key, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_stores_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the stores edge. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

[**StoresEdgeModel**](StoresEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_user_data**
> object delete_user_data(body=body)

Delete all user data

Deletes all user data from the \"user_data\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete all user data
    api_response = api_instance.delete_user_data(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_user_data: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_user_data_key**
> object delete_user_data_key(key, body=body)

Delete a user data object

Deletes a user data object from the \"user_data\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the user data object.
body = NULL # object |  (optional)

try:
    # Delete a user data object
    api_response = api_instance.delete_user_data_key(key, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_user_data_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the user data object. |
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_workflow**
> object delete_workflow(body=body)

Delete the workflow.

Delete all workflow objects from the database.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object |  (optional)

try:
    # Delete the workflow.
    api_response = api_instance.delete_workflow(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_workflow: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)|  | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_blocks**
> InlineResponse20011 get_blocks(skip=skip, limit=limit)

Retrieve all blocks edges

Retrieves all blocks edges from the \"blocks\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all blocks edges
    api_response = api_instance.get_blocks(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_blocks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_blocks_key**
> BlocksEdgeModel get_blocks_key(key)

Retrieve a blocks edge

Retrieves a blocks edge from the \"blocks\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the block.

try:
    # Retrieve a blocks edge
    api_response = api_instance.get_blocks_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_blocks_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the block. |

### Return type

[**BlocksEdgeModel**](BlocksEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_events**
> InlineResponse200 get_events(skip=skip, limit=limit)

Retrieve all events

Retrieves all events from the \"events\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all events
    api_response = api_instance.get_events(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_events: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_events_key**
> object get_events_key(key)

Retrieve the event for a key.

Retrieve the event for a key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the events object

try:
    # Retrieve the event for a key.
    api_response = api_instance.get_events_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_events_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the events object |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_files**
> InlineResponse2005 get_files(skip=skip, limit=limit)

Retrieve all files

Retrieves all files from the \"files\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all files
    api_response = api_instance.get_files(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_files: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse2005**](InlineResponse2005.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_files_name**
> FileModel get_files_name(name)

Retrieve a file

Retrieves a file from the \"files\" collection by name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | Name of the file.

try:
    # Retrieve a file
    api_response = api_instance.get_files_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_files_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Name of the file. |

### Return type

[**FileModel**](FileModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_files_produced_by_job_name**
> InlineResponse2005 get_files_produced_by_job_name(name, skip=skip, limit=limit)

Retrieve files produced by a job

Retrieves files from the \"files\" collection produced by a job.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str |
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve files produced by a job
    api_response = api_instance.get_files_produced_by_job_name(name, skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_files_produced_by_job_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  |
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse2005**](InlineResponse2005.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_hpc_configs**
> InlineResponse2006 get_hpc_configs(skip=skip, limit=limit)

Retrieve all hpc_configs

Retrieves all hpc_configs from the \"hpc_configs\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all hpc_configs
    api_response = api_instance.get_hpc_configs(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_hpc_configs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse2006**](InlineResponse2006.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_hpc_configs_name**
> HpcConfigModel get_hpc_configs_name(name)

Retrieve an hpc_config document by name

Retrieves an hpc_config document from the \"hpc_configs\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str |

try:
    # Retrieve an hpc_config document by name
    api_response = api_instance.get_hpc_configs_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_hpc_configs_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  |

### Return type

[**HpcConfigModel**](HpcConfigModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_definitions**
> InlineResponse2007 get_job_definitions(skip=skip, limit=limit)

Retrieve all job definitions

Retrieves all job definitions. Limit output with skip and limit.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all job definitions
    api_response = api_instance.get_job_definitions(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_job_definitions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse2007**](InlineResponse2007.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_definitions_name**
> InlineResponse2004 get_job_definitions_name(name)

Retrieve a job

Retrieves a job from the \"jobs\" collection by name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | Name of the job.

try:
    # Retrieve a job
    api_response = api_instance.get_job_definitions_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_job_definitions_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Name of the job. |

### Return type

[**InlineResponse2004**](InlineResponse2004.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_names**
> object get_job_names()

Retrieve all job names

Retrieves all job names from the \"jobs\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()

try:
    # Retrieve all job names
    api_response = api_instance.get_job_names()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_job_names: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jobs**
> InlineResponse2008 get_jobs(skip=skip, limit=limit)

Retrieve all jobs

Retrieve all jobs. Limit output with skip and limit.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all jobs
    api_response = api_instance.get_jobs(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_jobs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse2008**](InlineResponse2008.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jobs_find_by_needs_file_name**
> InlineResponse2008 get_jobs_find_by_needs_file_name(name, skip=skip, limit=limit)

Retrieve all jobs that need a file

Retrieves all jobs connected to a file by the needs edge.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | File name.
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all jobs that need a file
    api_response = api_instance.get_jobs_find_by_needs_file_name(name, skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_jobs_find_by_needs_file_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| File name. |
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse2008**](InlineResponse2008.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jobs_find_by_status_status**
> InlineResponse2008 get_jobs_find_by_status_status(status, skip=skip, limit=limit)

Retrieve all jobs with a specific status

Retrieves all jobs from the \"jobs\" collection with a specific status.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
status = 'status_example' # str | Job status.
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all jobs with a specific status
    api_response = api_instance.get_jobs_find_by_status_status(status, skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_jobs_find_by_status_status: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | **str**| Job status. |
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse2008**](InlineResponse2008.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jobs_get_user_data_name**
> object get_jobs_get_user_data_name(name)

Retrieve all user data for a job.

Retrieve all user data for a job.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | Job name.

try:
    # Retrieve all user data for a job.
    api_response = api_instance.get_jobs_get_user_data_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_jobs_get_user_data_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Job name. |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jobs_name**
> JobModel get_jobs_name(name)

Retrieve a job

Retrieves a job from the \"jobs\" collection by name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | Name of the job.

try:
    # Retrieve a job
    api_response = api_instance.get_jobs_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_jobs_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Name of the job. |

### Return type

[**JobModel**](JobModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jobs_resource_requirements_name**
> WorkflowResourceRequirements get_jobs_resource_requirements_name(name)

Retrieve the resource requirements for a job.

Retrieve the resource requirements for a job by its name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | Name of the job.

try:
    # Retrieve the resource requirements for a job.
    api_response = api_instance.get_jobs_resource_requirements_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_jobs_resource_requirements_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Name of the job. |

### Return type

[**WorkflowResourceRequirements**](WorkflowResourceRequirements.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_needs**
> InlineResponse20011 get_needs(skip=skip, limit=limit)

Retrieve all needs

Retrieves all needs from the \"needs\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all needs
    api_response = api_instance.get_needs(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_needs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_needs_key**
> NeedsEdgeModel get_needs_key(key)

Retrieve a needs edge

Retrieves a need edge from the \"needs\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the needs edge.

try:
    # Retrieve a needs edge
    api_response = api_instance.get_needs_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_needs_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the needs edge. |

### Return type

[**NeedsEdgeModel**](NeedsEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_produces**
> InlineResponse20011 get_produces(skip=skip, limit=limit)

Retrieve all produces edges

Retrieves all produces edges from the \"produces\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all produces edges
    api_response = api_instance.get_produces(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_produces: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_produces_key**
> ProducesEdgeModel get_produces_key(key)

Retrieve a produces edge

Retrieves a produces edge from the \"produces\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the produces edge.

try:
    # Retrieve a produces edge
    api_response = api_instance.get_produces_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_produces_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the produces edge. |

### Return type

[**ProducesEdgeModel**](ProducesEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_requires**
> InlineResponse20011 get_requires(skip=skip, limit=limit)

Retrieve all requires

Retrieves all requires edges from the \"requires\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all requires
    api_response = api_instance.get_requires(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_requires: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_requires_key**
> RequiresEdgeModel get_requires_key(key)

Retrieve a require

Retrieves a requires edge from the \"requires\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the require.

try:
    # Retrieve a require
    api_response = api_instance.get_requires_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_requires_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the require. |

### Return type

[**RequiresEdgeModel**](RequiresEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_resource_requirements**
> InlineResponse2009 get_resource_requirements(skip=skip, limit=limit)

Retrieve all resource requirements

Retrieves all requirement from the \"resource_requirements\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all resource requirements
    api_response = api_instance.get_resource_requirements(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_resource_requirements: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse2009**](InlineResponse2009.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_resource_requirements_name**
> ResourceRequirementsModel get_resource_requirements_name(name)

Retrieve a resource requirements document by name

Retrieve a resource requirements document by name.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str |

try:
    # Retrieve a resource requirements document by name
    api_response = api_instance.get_resource_requirements_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_resource_requirements_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  |

### Return type

[**ResourceRequirementsModel**](ResourceRequirementsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_results**
> InlineResponse20010 get_results(skip=skip, limit=limit)

Retrieve all results

Retrieves all results from the \"results\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all results
    api_response = api_instance.get_results(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_results: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse20010**](InlineResponse20010.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_results_find_by_job_name_name**
> ResultModel get_results_find_by_job_name_name(name)

Retrieve the latest result for a job

Retrieve the latest result for a job. Throws an error if no result is stored.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str | Job name.

try:
    # Retrieve the latest result for a job
    api_response = api_instance.get_results_find_by_job_name_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_results_find_by_job_name_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Job name. |

### Return type

[**ResultModel**](ResultModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_results_key**
> ResultModel get_results_key(key)

Retrieve the result for a key.

Retrieve the result for a key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the results object

try:
    # Retrieve the result for a key.
    api_response = api_instance.get_results_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_results_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the results object |

### Return type

[**ResultModel**](ResultModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_returned**
> InlineResponse20011 get_returned(skip=skip, limit=limit)

Retrieve all returned

Retrieves all edges from the \"returned\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all returned
    api_response = api_instance.get_returned(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_returned: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_returned_key**
> ReturnedEdgeModel get_returned_key(key)

Retrieve a returned edge

Retrieves an edge from the \"returned\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the returned edge.

try:
    # Retrieve a returned edge
    api_response = api_instance.get_returned_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_returned_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the returned edge. |

### Return type

[**ReturnedEdgeModel**](ReturnedEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_scheduled_bys**
> InlineResponse20011 get_scheduled_bys(skip=skip, limit=limit)

Retrieve all scheduled_by edges

Retrieves all edges from the \"scheduled_by\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all scheduled_by edges
    api_response = api_instance.get_scheduled_bys(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_scheduled_bys: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_scheduled_bys_key**
> ScheduledByEdgeModel get_scheduled_bys_key(key)

Retrieve a scheduled_by edge

Retrieves an edge from the \"scheduled_by\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the scheduled_by.

try:
    # Retrieve a scheduled_by edge
    api_response = api_instance.get_scheduled_bys_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_scheduled_bys_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the scheduled_by. |

### Return type

[**ScheduledByEdgeModel**](ScheduledByEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_stores**
> InlineResponse20011 get_stores(skip=skip, limit=limit)

Retrieve all stores edges

Retrieves all stores edges from the \"stores\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all stores edges
    api_response = api_instance.get_stores(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_stores: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_stores_key**
> StoresEdgeModel get_stores_key(key)

Retrieve a stores edge

Retrieves a stores edge from the \"stores\" collection by key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the stores edge.

try:
    # Retrieve a stores edge
    api_response = api_instance.get_stores_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_stores_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the stores edge. |

### Return type

[**StoresEdgeModel**](StoresEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_user_data**
> InlineResponse200 get_user_data(skip=skip, limit=limit)

Retrieve all user data objects

Retrieves all user data from the \"user_data\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
skip = 0.0 # float |  (optional) (default to 0.0)
limit = 100.0 # float |  (optional) (default to 100.0)

try:
    # Retrieve all user data objects
    api_response = api_instance.get_user_data(skip=skip, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_user_data: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **skip** | **float**|  | [optional] [default to 0.0]
 **limit** | **float**|  | [optional] [default to 100.0]

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_user_data_key**
> object get_user_data_key(key)

Retrieve the user data object for a key.

Retrieve the user data object for a key.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
key = 'key_example' # str | Key of the user_data object

try:
    # Retrieve the user data object for a key.
    api_response = api_instance.get_user_data_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_user_data_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the user_data object |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_workflow**
> InlineResponse2001 get_workflow()

Retrieve the current workflow

Retrieves the current workflow in JSON format.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()

try:
    # Retrieve the current workflow
    api_response = api_instance.get_workflow()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_workflow: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_workflow_example**
> InlineResponse2001 get_workflow_example()

Retrieve an example workflow

Retrieves an example workflow in JSON format.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()

try:
    # Retrieve an example workflow
    api_response = api_instance.get_workflow_example()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_workflow_example: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_workflow_is_complete**
> InlineResponse2002 get_workflow_is_complete()

Report whether the workflow is complete

Reports true if all jobs in the workflow are complete.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()

try:
    # Report whether the workflow is complete
    api_response = api_instance.get_workflow_is_complete()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_workflow_is_complete: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2002**](InlineResponse2002.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_blocks**
> BlocksEdgeModel post_blocks(body)

Store a blocks edge between a job and a file.

Store a job-file relationship in the \"blocks\" edge collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.BlocksEdgeModel() # BlocksEdgeModel | blocks relationship between a job and a file.

try:
    # Store a blocks edge between a job and a file.
    api_response = api_instance.post_blocks(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_blocks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**BlocksEdgeModel**](BlocksEdgeModel.md)| blocks relationship between a job and a file. |

### Return type

[**BlocksEdgeModel**](BlocksEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_events**
> object post_events(body)

Store an event.

Store an event in the \"events\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object | event.

try:
    # Store an event.
    api_response = api_instance.post_events(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_events: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)| event. |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_files**
> FileModel post_files(body)

Store file

Store a file in the \"files\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.FileModel() # FileModel | file to store in the collection.

try:
    # Store file
    api_response = api_instance.post_files(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_files: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FileModel**](FileModel.md)| file to store in the collection. |

### Return type

[**FileModel**](FileModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_hpc_configs**
> HpcConfigModel post_hpc_configs(body)

Store an hpc_config.

Store an hpc_config in the \"hpc_configs\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.HpcConfigModel() # HpcConfigModel | hpc_config to store in the collection

try:
    # Store an hpc_config.
    api_response = api_instance.post_hpc_configs(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_hpc_configs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**HpcConfigModel**](HpcConfigModel.md)| hpc_config to store in the collection |

### Return type

[**HpcConfigModel**](HpcConfigModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_job_definitions**
> InlineResponse2004 post_job_definitions(body)

Store a job and create edges.

Store a job in the \"jobs\" collection and create edges.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.JobDefinition() # JobDefinition | job definition to store in the collection.

try:
    # Store a job and create edges.
    api_response = api_instance.post_job_definitions(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_job_definitions: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**JobDefinition**](JobDefinition.md)| job definition to store in the collection. |

### Return type

[**InlineResponse2004**](InlineResponse2004.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_jobs**
> JobModel post_jobs(body)

Store job

Store a job in the \"jobs\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.JobModel() # JobModel | job to store in the collection.

try:
    # Store job
    api_response = api_instance.post_jobs(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_jobs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**JobModel**](JobModel.md)| job to store in the collection. |

### Return type

[**JobModel**](JobModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_jobs_complete_job_name_status_rev**
> JobModel post_jobs_complete_job_name_status_rev(body, name, status, rev)

Complete a job and add a result.

Complete a job, connect it to a result, and manage side effects.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.StatusRevBody() # StatusRevBody | Result of the job.
name = 'name_example' # str |
status = 'status_example' # str |
rev = 'rev_example' # str |

try:
    # Complete a job and add a result.
    api_response = api_instance.post_jobs_complete_job_name_status_rev(body, name, status, rev)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_jobs_complete_job_name_status_rev: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StatusRevBody**](StatusRevBody.md)| Result of the job. |
 **name** | **str**|  |
 **status** | **str**|  |
 **rev** | **str**|  |

### Return type

[**JobModel**](JobModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_jobs_store_user_data_name**
> object post_jobs_store_user_data_name(body, name)

Store user data for a job.

Store user data for a job and connect the two vertexes.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.StoreUserDataNameBody() # StoreUserDataNameBody | User data for the job.
name = 'name_example' # str |

try:
    # Store user data for a job.
    api_response = api_instance.post_jobs_store_user_data_name(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_jobs_store_user_data_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StoreUserDataNameBody**](StoreUserDataNameBody.md)| User data for the job. |
 **name** | **str**|  |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_needs**
> NeedsEdgeModel post_needs(body)

Store a needs edge between a job and a file.

Store a job-file relationship in the \"needs\" edge collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.NeedsEdgeModel() # NeedsEdgeModel | Needs relationship between a job and a file.

try:
    # Store a needs edge between a job and a file.
    api_response = api_instance.post_needs(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_needs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**NeedsEdgeModel**](NeedsEdgeModel.md)| Needs relationship between a job and a file. |

### Return type

[**NeedsEdgeModel**](NeedsEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_produces**
> ProducesEdgeModel post_produces(body)

Store a produces edge between a job and a file.

Store a job-file relationship in the \"produces\" edge collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.ProducesEdgeModel() # ProducesEdgeModel | produces relationship between a job and a file.

try:
    # Store a produces edge between a job and a file.
    api_response = api_instance.post_produces(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_produces: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ProducesEdgeModel**](ProducesEdgeModel.md)| produces relationship between a job and a file. |

### Return type

[**ProducesEdgeModel**](ProducesEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_requires**
> RequiresEdgeModel post_requires(body)

Store a requires edge between a job and a resource.

Store a job-resource relationship in the \"requires\" edge collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.RequiresEdgeModel() # RequiresEdgeModel | requires relationship between a job and a resource.

try:
    # Store a requires edge between a job and a resource.
    api_response = api_instance.post_requires(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_requires: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**RequiresEdgeModel**](RequiresEdgeModel.md)| requires relationship between a job and a resource. |

### Return type

[**RequiresEdgeModel**](RequiresEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_resource_requirements**
> ResourceRequirementsModel post_resource_requirements(body)

Store a resource.

Store a resource in the \"resource_requirements\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.ResourceRequirementsModel() # ResourceRequirementsModel | resource to store in the collection

try:
    # Store a resource.
    api_response = api_instance.post_resource_requirements(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_resource_requirements: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ResourceRequirementsModel**](ResourceRequirementsModel.md)| resource to store in the collection |

### Return type

[**ResourceRequirementsModel**](ResourceRequirementsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_results**
> ResultModel post_results(body)

Store a job result.

Store a job result in the \"results\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.ResultModel() # ResultModel | Job result.

try:
    # Store a job result.
    api_response = api_instance.post_results(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_results: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ResultModel**](ResultModel.md)| Job result. |

### Return type

[**ResultModel**](ResultModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_returned**
> ReturnedEdgeModel post_returned(body)

Store a returned edge between a job and a result.

Store a job-result relationship in the \"returned\" edge collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.ReturnedEdgeModel() # ReturnedEdgeModel | returned relationship between a job and a result.

try:
    # Store a returned edge between a job and a result.
    api_response = api_instance.post_returned(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_returned: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ReturnedEdgeModel**](ReturnedEdgeModel.md)| returned relationship between a job and a result. |

### Return type

[**ReturnedEdgeModel**](ReturnedEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_scheduled_bys**
> ScheduledByEdgeModel post_scheduled_bys(body)

Store a scheduled_by edge between a job and an hpc_config.

Store a job-hpc_config relationship in the \"scheduled_by\" edge collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.ScheduledByEdgeModel() # ScheduledByEdgeModel | scheduled_by relationship between a job and an hpc_config.

try:
    # Store a scheduled_by edge between a job and an hpc_config.
    api_response = api_instance.post_scheduled_bys(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_scheduled_bys: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ScheduledByEdgeModel**](ScheduledByEdgeModel.md)| scheduled_by relationship between a job and an hpc_config. |

### Return type

[**ScheduledByEdgeModel**](ScheduledByEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_stores**
> StoresEdgeModel post_stores(body)

Store a stores edge between a job and a user data object.

Store a job-user-data relationship in the \"stores\" edge collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.StoresEdgeModel() # StoresEdgeModel | stores relationship between a job and a user data object.

try:
    # Store a stores edge between a job and a user data object.
    api_response = api_instance.post_stores(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_stores: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**StoresEdgeModel**](StoresEdgeModel.md)| stores relationship between a job and a user data object. |

### Return type

[**StoresEdgeModel**](StoresEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_user_data**
> object post_user_data(body=body)

Store user data for a job.

Store user data in the \"user_data\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object | User data. (optional)

try:
    # Store user data for a job.
    api_response = api_instance.post_user_data(body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_user_data: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)| User data. | [optional]

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_workflow**
> object post_workflow(body)

Store a workflow.

Store a workflow, overwriting any existing entries.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.Workflow() # Workflow | New workflow

try:
    # Store a workflow.
    api_response = api_instance.post_workflow(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_workflow: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Workflow**](Workflow.md)| New workflow |

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_workflow_estimate**
> InlineResponse2003 post_workflow_estimate()

Perform a dry run of all jobs to estimate required resources.

Perform a dry run of all jobs to estimate required resources.       Only valid if jobs have similar runtimes

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()

try:
    # Perform a dry run of all jobs to estimate required resources.
    api_response = api_instance.post_workflow_estimate()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_workflow_estimate: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**InlineResponse2003**](InlineResponse2003.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_workflow_initialize_jobs**
> object post_workflow_initialize_jobs()

Initialize job relationships.

Initialize job relationships based on file relationships.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()

try:
    # Initialize job relationships.
    api_response = api_instance.post_workflow_initialize_jobs()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_workflow_initialize_jobs: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_workflow_prepare_jobs_for_submission**
> list[InlineResponse2004] post_workflow_prepare_jobs_for_submission(body)

Return ready jobs

Return jobs that are ready for submission. Sets status to submitted_pending

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = swagger_client.WorkerResources() # WorkerResources | Available worker resources.

try:
    # Return ready jobs
    api_response = api_instance.post_workflow_prepare_jobs_for_submission(body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_workflow_prepare_jobs_for_submission: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkerResources**](WorkerResources.md)| Available worker resources. |

### Return type

[**list[InlineResponse2004]**](InlineResponse2004.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_workflow_reset_status**
> object post_workflow_reset_status()

Reset job status.

Reset status for all jobs to uninitialized.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()

try:
    # Reset job status.
    api_response = api_instance.post_workflow_reset_status()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->post_workflow_reset_status: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_files_name**
> FileModel put_files_name(body, name)

Update file

Update a file in the \"files\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object | file to update in the collection.
name = 'name_example' # str |

try:
    # Update file
    api_response = api_instance.put_files_name(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->put_files_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)| file to update in the collection. |
 **name** | **str**|  |

### Return type

[**FileModel**](FileModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_jobs_manage_status_change_name_status_rev**
> JobModel put_jobs_manage_status_change_name_status_rev(name, status, rev)

Change the status of a job and manage side effects.

Change the status of a job and manage side effects.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
name = 'name_example' # str |
status = 'status_example' # str |
rev = 'rev_example' # str |

try:
    # Change the status of a job and manage side effects.
    api_response = api_instance.put_jobs_manage_status_change_name_status_rev(name, status, rev)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->put_jobs_manage_status_change_name_status_rev: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  |
 **status** | **str**|  |
 **rev** | **str**|  |

### Return type

[**JobModel**](JobModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: */*
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **put_jobs_name**
> JobModel put_jobs_name(body, name)

Update job

Update a job in the \"jobs\" collection.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = swagger_client.DefaultApi()
body = NULL # object | job to update in the collection.
name = 'name_example' # str |

try:
    # Update job
    api_response = api_instance.put_jobs_name(body, name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->put_jobs_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**object**](object.md)| job to update in the collection. |
 **name** | **str**|  |

### Return type

[**JobModel**](JobModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
