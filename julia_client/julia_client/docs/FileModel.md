# FileModel


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **String** | User-defined name of the file (not necessarily the filename) | [optional] [default to nothing]
**path** | **String** | Path to the file; can be relative to the execution directory. | [default to nothing]
**st_mtime** | **Float64** | Timestamp of when the file was last modified | [optional] [default to nothing]
**_key** | **String** | Unique database identifier for the file. Does not include collection name. | [optional] [default to nothing]
**_id** | **String** | Unique database identifier for the file. Includes collection name and _key. | [optional] [default to nothing]
**_rev** | **String** | Database revision of the file | [optional] [default to nothing]


[[Back to Model list]](../README.md#models) [[Back to API list]](../README.md#api-endpoints) [[Back to README]](../README.md)


