from torc import make_job_label
from torc.openapi_client import JobModel


def test_job_label():
    job = JobModel(name="my job", command="echo hello")
    label = make_job_label(job)
    assert "name=my job" in label
    assert "key" in label
    assert "status" not in label

    label2 = make_job_label(job, include_status=True)
    assert "name=my job" in label2
    assert "key" in label2
    assert "status" in label2
