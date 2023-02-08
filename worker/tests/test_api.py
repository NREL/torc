import pytest

from swagger_client.rest import ApiException


def test_api_by_key(completed_workflow):
    api, _ = completed_workflow
    names = [
        "blocks",
        "events",
        "needs",
        "produces",
        "requires",
        "results",
        "returned",
        "scheduled_bys",
        "stores",
        "user_data",
    ]

    def get_key(data: dict):
        for key in ("key", "_key"):
            if key in data:
                return data[key]
        raise KeyError(f"key is not stored in {data.keys()}")

    for name in names:
        results = getattr(api, f"get_{name}")()
        if results.items:
            item = results.items[0]
            if not isinstance(item, dict):
                item = item.to_dict()
            key = get_key(item)
            val = getattr(api, f"get_{name}_key")(key)
            if not isinstance(val, dict):
                val = val.to_dict()
            assert val == item
            getattr(api, f"delete_{name}_key")(key)
            with pytest.raises(ApiException):
                val = getattr(api, f"get_{name}_key")(key)

        getattr(api, f"delete_{name}")()
        result = getattr(api, f"get_{name}")()
        assert len(result.items) == 0


def test_api_by_name(completed_workflow):
    api, _ = completed_workflow
    names = ["hpc_configs", "files", "jobs", "resource_requirements"]
    for name in names:
        results = getattr(api, f"get_{name}")()
        if results.items:
            val = getattr(api, f"get_{name}_name")(results.items[0].name)
            assert val.to_dict() == results.items[0].to_dict()
            getattr(api, f"delete_{name}_name")(results.items[0].name)
            with pytest.raises(ApiException):
                val = getattr(api, f"get_{name}_name")(results.items[0].name)

        getattr(api, f"delete_{name}")()
        result = getattr(api, f"get_{name}")()
        assert len(result.items) == 0
