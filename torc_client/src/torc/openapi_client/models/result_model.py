# coding: utf-8

"""
    torc

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: v0.6.4
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional, Union
from typing import Optional, Set
from typing_extensions import Self

class ResultModel(BaseModel):
    """
    ResultModel
    """ # noqa: E501
    job_key: StrictStr = Field(description="Database key for the job tied to this result")
    run_id: StrictInt = Field(description="ID of the workflow run. Incremements on every start and restart.")
    return_code: StrictInt = Field(description="Code returned by the job. Zero is success; non-zero is a failure.")
    exec_time_minutes: Union[StrictFloat, StrictInt] = Field(description="Job execution time in minutes")
    completion_time: StrictStr = Field(description="Timestamp of when the job completed.")
    status: StrictStr = Field(description="Status of the job; managed by torc.")
    key: Optional[StrictStr] = Field(default=None, description="Unique database identifier for the result. Does not include collection name.", alias="_key")
    id: Optional[StrictStr] = Field(default=None, description="Unique database identifier for the result. Includes collection name and _key.", alias="_id")
    rev: Optional[StrictStr] = Field(default=None, description="Database revision of the result", alias="_rev")
    __properties: ClassVar[List[str]] = ["job_key", "run_id", "return_code", "exec_time_minutes", "completion_time", "status", "_key", "_id", "_rev"]

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of ResultModel from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        excluded_fields: Set[str] = set([
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ResultModel from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "job_key": obj.get("job_key"),
            "run_id": obj.get("run_id"),
            "return_code": obj.get("return_code"),
            "exec_time_minutes": obj.get("exec_time_minutes"),
            "completion_time": obj.get("completion_time"),
            "status": obj.get("status"),
            "_key": obj.get("_key"),
            "_id": obj.get("_id"),
            "_rev": obj.get("_rev")
        })
        return _obj
