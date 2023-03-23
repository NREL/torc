"""Helper code to run tests"""


from swagger_client.api.default_api import DefaultApi

from torc.api import iter_documents


class TestApiManager:
    """Contains helper code to access objects from the API in tests."""

    def __init__(self, api: DefaultApi):
        self._api = api
        self._job_name_to_key = self._map_job_names_to_keys(api)

    @staticmethod
    def _map_job_names_to_keys(api: DefaultApi):
        lookup = {}
        for job in iter_documents(api.get_jobs):
            assert job.name not in lookup, job.name
            lookup[job.name] = job.key
        return lookup

    def get_job(self, name):
        """Return the job from the API by first mapping the name."""
        return self._api.get_jobs_key(self._job_name_to_key[name])

    def get_job_key(self, name):
        """Return the job key for name."""
        return self._job_name_to_key[name]
