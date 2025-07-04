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

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from typing import Optional, Set
from typing_extensions import Self

class LocalSchedulerModel(BaseModel):
    """
    LocalSchedulerModel
    """ # noqa: E501
    name: Optional[StrictStr] = 'default'
    memory: Optional[StrictStr] = None
    num_cpus: Optional[StrictInt] = None
    key: Optional[StrictStr] = Field(default=None, alias="_key")
    id: Optional[StrictStr] = Field(default=None, alias="_id")
    rev: Optional[StrictStr] = Field(default=None, alias="_rev")
    __properties: ClassVar[List[str]] = ["name", "memory", "num_cpus", "_key", "_id", "_rev"]

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
        """Create an instance of LocalSchedulerModel from a JSON string"""
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
        """Create an instance of LocalSchedulerModel from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "name": obj.get("name") if obj.get("name") is not None else 'default',
            "memory": obj.get("memory"),
            "num_cpus": obj.get("num_cpus"),
            "_key": obj.get("_key"),
            "_id": obj.get("_id"),
            "_rev": obj.get("_rev")
        })
        return _obj
