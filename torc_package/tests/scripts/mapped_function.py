"""Contains a function that will be mapped across workers."""


def run(data: dict):
    """Function to be mapped across workers."""
    assert "val" in data
    return {"params": data, "result": 5, "output_data_path": "/projects/my-project/run1"}
