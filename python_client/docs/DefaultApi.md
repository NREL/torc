# swagger_client.DefaultApi

All URIs are relative to */_db/workflows/wms-service*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_blocks**](DefaultApi.md#delete_blocks) | **DELETE** /blocks | Delete all blocks edges
[**delete_blocks_key**](DefaultApi.md#delete_blocks_key) | **DELETE** /blocks/{key} | Delete a block
[**delete_events**](DefaultApi.md#delete_events) | **DELETE** /events | Delete all events
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
[**delete_scheduled_bys**](DefaultApi.md#delete_scheduled_bys) | **DELETE** /scheduled_bys | Delete all scheduled_by edges
[**delete_scheduled_bys_key**](DefaultApi.md#delete_scheduled_bys_key) | **DELETE** /scheduled_bys/{key} | Delete a scheduled_by
[**delete_workflow**](DefaultApi.md#delete_workflow) | **DELETE** /workflow | Delete the workflow.
[**get_blocks**](DefaultApi.md#get_blocks) | **GET** /blocks | Retrieve all blocks edges
[**get_blocks_key**](DefaultApi.md#get_blocks_key) | **GET** /blocks/{key} | Retrieve a blocks edge
[**get_events**](DefaultApi.md#get_events) | **GET** /events | Retrieve all events
[**get_files**](DefaultApi.md#get_files) | **GET** /files | Retrieve all files
[**get_files_name**](DefaultApi.md#get_files_name) | **GET** /files/{name} | Retrieve a file
[**get_files_produced_by_job_name**](DefaultApi.md#get_files_produced_by_job_name) | **GET** /files/produced_by_job/{name} | Retrieve files produced by a job
[**get_hpc_configs**](DefaultApi.md#get_hpc_configs) | **GET** /hpc_configs | Retrieve all hpc_configs
[**get_hpc_configs_name**](DefaultApi.md#get_hpc_configs_name) | **GET** /hpc_configs/{name} | Retrieve an hpc_config document by name
[**get_job_definitions**](DefaultApi.md#get_job_definitions) | **GET** /job_definitions | Retrieve all job definitions
[**get_job_definitions_name**](DefaultApi.md#get_job_definitions_name) | **GET** /job_definitions/{name} | Retrieve a job
[**get_job_names**](DefaultApi.md#get_job_names) | **GET** /job_names | Retrieve all job names
[**get_jobs**](DefaultApi.md#get_jobs) | **GET** /jobs | Retrieve all jobs
[**get_jobs_find_by_status_status**](DefaultApi.md#get_jobs_find_by_status_status) | **GET** /jobs/find_by_status/{status} | Retrieve all jobs with a specific status
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
[**get_scheduled_bys**](DefaultApi.md#get_scheduled_bys) | **GET** /scheduled_bys | Retrieve all scheduled_by edges
[**get_scheduled_bys_key**](DefaultApi.md#get_scheduled_bys_key) | **GET** /scheduled_bys/{key} | Retrieve a scheduled_by edge
[**get_workflow**](DefaultApi.md#get_workflow) | **GET** /workflow | Retrieve the current workflow
[**get_workflow_example**](DefaultApi.md#get_workflow_example) | **GET** /workflow/example | Retrieve an example workflow
[**get_workflow_is_complete**](DefaultApi.md#get_workflow_is_complete) | **GET** /workflow/is_complete | Report whether the workflow is complete
[**post_blocks**](DefaultApi.md#post_blocks) | **POST** /blocks | Store a blocks edge between a job and a file.
[**post_events**](DefaultApi.md#post_events) | **POST** /events | Store an event.
[**post_files**](DefaultApi.md#post_files) | **POST** /files | Store file
[**post_hpc_configs**](DefaultApi.md#post_hpc_configs) | **POST** /hpc_configs | Store an hpc_config.
[**post_job_definitions**](DefaultApi.md#post_job_definitions) | **POST** /job_definitions | Store a job and create edges.
[**post_jobs**](DefaultApi.md#post_jobs) | **POST** /jobs | Store job
[**post_needs**](DefaultApi.md#post_needs) | **POST** /needs | Store a needs edge between a job and a file.
[**post_produces**](DefaultApi.md#post_produces) | **POST** /produces | Store a produces edge between a job and a file.
[**post_requires**](DefaultApi.md#post_requires) | **POST** /requires | Store a requires edge between a job and a resource.
[**post_resource_requirements**](DefaultApi.md#post_resource_requirements) | **POST** /resource_requirements | Store a resource.
[**post_results**](DefaultApi.md#post_results) | **POST** /results | Store a job result.
[**post_scheduled_bys**](DefaultApi.md#post_scheduled_bys) | **POST** /scheduled_bys | Store a scheduled_by edge between a job and an hpc_config.
[**post_workflow**](DefaultApi.md#post_workflow) | **POST** /workflow | Store a workflow.
[**post_workflow_estimate**](DefaultApi.md#post_workflow_estimate) | **POST** /workflow/estimate | Perform a dry run of all jobs to estimate required resources.
[**post_workflow_initialize_jobs**](DefaultApi.md#post_workflow_initialize_jobs) | **POST** /workflow/initialize_jobs | Initialize job relationships.
[**post_workflow_prepare_jobs_for_submission**](DefaultApi.md#post_workflow_prepare_jobs_for_submission) | **POST** /workflow/prepare_jobs_for_submission | Return ready jobs
[**post_workflow_reset_status**](DefaultApi.md#post_workflow_reset_status) | **POST** /workflow/reset_status | Reset job status.
[**put_files_name**](DefaultApi.md#put_files_name) | **PUT** /files/{name} | Update file
[**put_jobs_name**](DefaultApi.md#put_jobs_name) | **PUT** /jobs/{name} | Update job

# **delete_blocks**
> object delete_blocks()

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

try:
    # Delete all blocks edges
    api_response = api_instance.delete_blocks()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_blocks: %s\n" % e)
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

# **delete_blocks_key**
> BlocksEdgeModel delete_blocks_key(key)

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

try:
    # Delete a block
    api_response = api_instance.delete_blocks_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_blocks_key: %s\n" % e)
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

# **delete_files**
> object delete_files()

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

try:
    # Delete all files
    api_response = api_instance.delete_files()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_files: %s\n" % e)
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

# **delete_files_name**
> FileModel delete_files_name(name)

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

try:
    # Delete a file
    api_response = api_instance.delete_files_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_files_name: %s\n" % e)
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

# **delete_hpc_configs**
> object delete_hpc_configs()

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

try:
    # Delete all hpc_configs
    api_response = api_instance.delete_hpc_configs()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_hpc_configs: %s\n" % e)
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

# **delete_hpc_configs_name**
> HpcConfigModel delete_hpc_configs_name(name)

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

try:
    # Delete a hpc_config
    api_response = api_instance.delete_hpc_configs_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_hpc_configs_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Name of the hpc_config. | 

### Return type

[**HpcConfigModel**](HpcConfigModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_jobs**
> object delete_jobs()

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

try:
    # Delete all jobs
    api_response = api_instance.delete_jobs()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_jobs: %s\n" % e)
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

# **delete_jobs_name**
> JobModel delete_jobs_name(name)

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

try:
    # Delete a job
    api_response = api_instance.delete_jobs_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_jobs_name: %s\n" % e)
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

# **delete_needs**
> object delete_needs()

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

try:
    # Delete all needs edges
    api_response = api_instance.delete_needs()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_needs: %s\n" % e)
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

# **delete_needs_key**
> NeedsEdgeModel delete_needs_key(key)

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

try:
    # Delete a need
    api_response = api_instance.delete_needs_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_needs_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the need. | 

### Return type

[**NeedsEdgeModel**](NeedsEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_produces**
> object delete_produces()

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

try:
    # Delete all produces edges
    api_response = api_instance.delete_produces()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_produces: %s\n" % e)
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

# **delete_produces_key**
> ProducesEdgeModel delete_produces_key(key)

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
key = 'key_example' # str | Key of the produce.

try:
    # Delete a produces edge
    api_response = api_instance.delete_produces_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_produces_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**| Key of the produce. | 

### Return type

[**ProducesEdgeModel**](ProducesEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_requires**
> object delete_requires()

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

try:
    # Delete all requires edges
    api_response = api_instance.delete_requires()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_requires: %s\n" % e)
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

# **delete_requires_key**
> RequiresEdgeModel delete_requires_key(key)

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

try:
    # Delete a require
    api_response = api_instance.delete_requires_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_requires_key: %s\n" % e)
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

# **delete_resource_requirements**
> object delete_resource_requirements()

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

try:
    # Delete all resource_requirements
    api_response = api_instance.delete_resource_requirements()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_resource_requirements: %s\n" % e)
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

# **delete_resource_requirements_name**
> ResourceRequirementsModel delete_resource_requirements_name(name)

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

try:
    # Delete a resource
    api_response = api_instance.delete_resource_requirements_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_resource_requirements_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**| Name of the resource. | 

### Return type

[**ResourceRequirementsModel**](ResourceRequirementsModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_results**
> object delete_results()

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

try:
    # Delete all results
    api_response = api_instance.delete_results()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_results: %s\n" % e)
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

# **delete_scheduled_bys**
> object delete_scheduled_bys()

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

try:
    # Delete all scheduled_by edges
    api_response = api_instance.delete_scheduled_bys()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_scheduled_bys: %s\n" % e)
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

# **delete_scheduled_bys_key**
> ScheduledByEdgeModel delete_scheduled_bys_key(key)

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

try:
    # Delete a scheduled_by
    api_response = api_instance.delete_scheduled_bys_key(key)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->delete_scheduled_bys_key: %s\n" % e)
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
> list[ProducesEdgeModel] get_blocks()

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

try:
    # Retrieve all blocks edges
    api_response = api_instance.get_blocks()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_blocks: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ProducesEdgeModel]**](ProducesEdgeModel.md)

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
> list[object] get_events()

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

try:
    # Retrieve all events
    api_response = api_instance.get_events()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_events: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**list[object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_files**
> list[WorkflowFiles] get_files()

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

try:
    # Retrieve all files
    api_response = api_instance.get_files()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_files: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[WorkflowFiles]**](WorkflowFiles.md)

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
> list[FileModel] get_files_produced_by_job_name(name)

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

try:
    # Retrieve files produced by a job
    api_response = api_instance.get_files_produced_by_job_name(name)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_files_produced_by_job_name: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**list[FileModel]**](FileModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_hpc_configs**
> list[WorkflowSchedulers] get_hpc_configs()

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

try:
    # Retrieve all hpc_configs
    api_response = api_instance.get_hpc_configs()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_hpc_configs: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[WorkflowSchedulers]**](WorkflowSchedulers.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_hpc_configs_name**
> WorkflowResourceRequirements get_hpc_configs_name(name)

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

[**WorkflowResourceRequirements**](WorkflowResourceRequirements.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_definitions**
> list[JobDefinition2] get_job_definitions()

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

try:
    # Retrieve all job definitions
    api_response = api_instance.get_job_definitions()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_job_definitions: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[JobDefinition2]**](JobDefinition2.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_definitions_name**
> InlineResponse2003 get_job_definitions_name(name)

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

[**InlineResponse2003**](InlineResponse2003.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_names**
> list[str] get_job_names()

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

**list[str]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jobs**
> list[InlineResponse2003] get_jobs()

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

try:
    # Retrieve all jobs
    api_response = api_instance.get_jobs()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_jobs: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[InlineResponse2003]**](InlineResponse2003.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_jobs_find_by_status_status**
> list[JobModel] get_jobs_find_by_status_status(status)

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

try:
    # Retrieve all jobs with a specific status
    api_response = api_instance.get_jobs_find_by_status_status(status)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_jobs_find_by_status_status: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | **str**| Job status. | 

### Return type

[**list[JobModel]**](JobModel.md)

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
> list[InlineResponse2004] get_needs()

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

try:
    # Retrieve all needs
    api_response = api_instance.get_needs()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_needs: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[InlineResponse2004]**](InlineResponse2004.md)

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
> list[NeedsEdgeModel] get_produces()

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

try:
    # Retrieve all produces edges
    api_response = api_instance.get_produces()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_produces: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[NeedsEdgeModel]**](NeedsEdgeModel.md)

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
> list[ScheduledByEdgeModel] get_requires()

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

try:
    # Retrieve all requires
    api_response = api_instance.get_requires()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_requires: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[ScheduledByEdgeModel]**](ScheduledByEdgeModel.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_requires_key**
> RequiresEdgeModel get_requires_key(key)

Retrieve a require

Retrieves a requires edge edge from the \"requires\" collection by key.

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
> list[WorkflowResourceRequirements] get_resource_requirements()

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

try:
    # Retrieve all resource requirements
    api_response = api_instance.get_resource_requirements()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_resource_requirements: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[WorkflowResourceRequirements]**](WorkflowResourceRequirements.md)

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
> list[object] get_results()

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

try:
    # Retrieve all results
    api_response = api_instance.get_results()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_results: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**list[object]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_scheduled_bys**
> list[BlocksEdgeModel] get_scheduled_bys()

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

try:
    # Retrieve all scheduled_by edges
    api_response = api_instance.get_scheduled_bys()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_scheduled_bys: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**list[BlocksEdgeModel]**](BlocksEdgeModel.md)

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

# **get_workflow**
> InlineResponse200 get_workflow()

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

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_workflow_example**
> InlineResponse200 get_workflow_example()

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

[**InlineResponse200**](InlineResponse200.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_workflow_is_complete**
> InlineResponse2001 get_workflow_is_complete()

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

[**InlineResponse2001**](InlineResponse2001.md)

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
> InlineResponse2003 post_job_definitions(body)

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

[**InlineResponse2003**](InlineResponse2003.md)

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
> InlineResponse2002 post_workflow_estimate()

Perform a dry run of all jobs to estimate required resources.

Perform a dry run of all jobs to estimate required resources.        Only valid if jobs have similar runtimes

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

[**InlineResponse2002**](InlineResponse2002.md)

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
> list[InlineResponse2003] post_workflow_prepare_jobs_for_submission(body)

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

[**list[InlineResponse2003]**](InlineResponse2003.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_workflow_reset_status**
> object post_workflow_reset_status()

Reset job status.

Reset status for all jobs to not_submitted.

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

