"""Helper code to run tests"""

from collections import defaultdict

from torc.openapi_client.api.default_api import DefaultApi

from torc.api import iter_documents


class DatabaseInterface:
    """Contains helper code to access objects from the database in tests."""

    def __init__(self, api: DefaultApi, workflow):
        self._api = api
        self._workflow = workflow
        self._names_to_keys = self._map_names_to_keys(api, workflow.key)

    @staticmethod
    def _map_names_to_keys(api: DefaultApi, workflow_key) -> dict[str, dict[str, str]]:
        doc_types = (
            "files",
            "jobs",
            "local_schedulers",
            "resource_requirements",
            "slurm_schedulers",
            "user_data",
        )
        lookup: dict[str, dict[str, str]] = defaultdict(dict)
        for doc_type in doc_types:
            method = getattr(api, f"list_{doc_type}")
            for doc in iter_documents(method, workflow_key):
                assert doc.name not in lookup[doc_type], f"{doc_type=} {doc.name=}"
                lookup[doc_type][doc.name] = doc.key
        return lookup

    @property
    def api(self) -> DefaultApi:
        """Return the API object."""
        return self._api

    @property
    def workflow(self):
        """Return the workflow object."""
        return self._workflow

    def get_document(self, document_type, name):
        """Return the document from the API by first mapping the name."""
        if document_type in {"resource_requirements", "user_data"}:
            get_one = f"get_{document_type}"
        else:
            get_one = f"get_{document_type[:-1]}"
        method = getattr(self._api, get_one)
        return method(self._workflow.key, self._names_to_keys[document_type][name])

    def get_document_key(self, document_type, name):
        """Return the key for name."""
        return self._names_to_keys[document_type][name]

    def list_documents(self, document_type):
        """Return all documents of the givent type."""
        method = getattr(self._api, f"list_{document_type}")
        return list(iter_documents(method, self._workflow.key))

    @property
    def url(self):
        """Return the database URL."""
        return self._api.api_client.configuration.host
