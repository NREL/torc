def run(job_name: str, input_params: dict) -> dict:
    """Runs one simulation on a set of input parameters.

    Returns
    -------
    dict
        Result of the simulation.
    """
    return {
        "inputs": input_params,
        "result": 5,
        "output_data_path": f"/projects/my-project/{job_name}",
    }


def postprocess(results: list[dict]) -> dict:
    """Collects the results of the workers and performs postprocessing.

    Parameters
    ----------
    results : list[dict]
        Results from each simulation

    Returns
    -------
    dict
        Final result
    """
    total = 0
    paths = []
    for result in results:
        assert "result" in result
        assert "output_data_path" in result
        total += result["result"]
        paths.append(result["output_data_path"])
    return {"total": total, "output_data_paths": paths}
