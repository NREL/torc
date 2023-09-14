"""Contains a function that will be mapped across workers."""


def run(data: dict):
    """Function to be mapped across workers."""
    assert "val" in data
    return {"params": data, "result": 5, "output_data_path": "/projects/my-project/run1"}


def postprocess(results: list[dict]):
    """Collects the results of workers."""
    total = 0
    paths = []
    for result in results:
        assert "result" in result
        assert "output_data_path" in result
        total += result["result"]
        paths.append(result["output_data_path"])
    return {"total": total, "output_data_paths": paths}
