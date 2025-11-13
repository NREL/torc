# WorkflowSpecificationModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **String** | Name of the workflow | [optional] [default to nothing]
**key** | **String** | Optional key to use as the database identifier. If set, it must be unique in the database. It is recommended to let the database create the identifier. | [optional] [default to nothing]
**user** | **String** | User that created the workflow | [optional] [default to nothing]
**description** | **String** | Timestamp of workflow creation | [optional] [default to nothing]
**jobs** | [**Vector{JobSpecificationModel}**](JobSpecificationModel.md) | Jobs in the workflow. Each job name must be unique. | [optional] [default to nothing]
**files** | [**Vector{FileModel}**](FileModel.md) | Files in the workflow. Each file name must be unique. | [optional] [default to nothing]
**user_data** | [**Vector{UserDataModel}**](UserDataModel.md) | User data in the workflow. Each name must be unique. | [optional] [default to nothing]
**resource_requirements** | [**Vector{ResourceRequirementsModel}**](ResourceRequirementsModel.md) | Resource requirements in the workflow. Each name must be unique. | [optional] [default to nothing]
**schedulers** | [***WorkflowSpecificationsSchedulers**](WorkflowSpecificationsSchedulers.md) |  | [optional] [default to nothing]
**config** | [***WorkflowConfigModel**](WorkflowConfigModel.md) |  | [optional] [default to nothing]


[[Back to Model list]](../README.md#models) [[Back to API list]](../README.md#api-endpoints) [[Back to README]](../README.md)


