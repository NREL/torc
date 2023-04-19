"""Helper code to build a workflow dynamically"""


from swagger_client.models.workflow_files_model import WorkflowFilesModel
from swagger_client.models.workflow_job_specifications_model import (
    WorkflowJobSpecificationsModel,
)
from swagger_client.models.workflow_resource_requirements_model import (
    WorkflowResourceRequirementsModel,
)
from swagger_client.models.workflow_specifications_model import (
    WorkflowSpecificationsModel,
)
from swagger_client.models.workflow_aws_schedulers_model import (
    WorkflowAwsSchedulersModel,
)
from swagger_client.models.workflow_local_schedulers_model import (
    WorkflowLocalSchedulersModel,
)
from swagger_client.models.workflow_slurm_schedulers_model import (
    WorkflowSlurmSchedulersModel,
)
from swagger_client.models.workflow_specifications_schedulers import (
    WorkflowSpecificationsSchedulers,
)
from swagger_client.models.workflow_user_data_model import WorkflowUserDataModel


class WorkflowBuilder:
    """Helper class to build a workflow dynamically"""

    def __init__(self):
        self._files = []
        self._jobs = []
        self._resource_requirements = []
        self._resources = []
        self._aws_schedulers = []
        self._local_schedulers = []
        self._slurm_schedulers = []
        self._user_data = []

    def add_file(self, *args, **kwargs) -> WorkflowFilesModel:
        """Add a file and return it."""
        self._files.append(WorkflowFilesModel(*args, **kwargs))
        return self._files[-1]

    def add_job(self, *args, **kwargs) -> WorkflowJobSpecificationsModel:
        """Add a job and return it."""
        self._jobs.append(WorkflowJobSpecificationsModel(*args, **kwargs))
        return self._jobs[-1]

    def add_resource_requirements(self, *args, **kwargs) -> WorkflowResourceRequirementsModel:
        """Add a resource_requirement and return it."""
        self._resource_requirements.append(WorkflowResourceRequirementsModel(*args, **kwargs))
        return self._resource_requirements[-1]

    def add_aws_scheduler(self, *args, **kwargs) -> WorkflowAwsSchedulersModel:
        """Add a slurm_scheduler and return it."""
        self._aws_schedulers.append(WorkflowAwsSchedulersModel(*args, **kwargs))
        return self._aws_schedulers[-1]

    def add_local_scheduler(self, *args, **kwargs) -> WorkflowLocalSchedulersModel:
        """Add a slurm_scheduler and return it."""
        self._local_schedulers.append(WorkflowLocalSchedulersModel(*args, **kwargs))
        return self._local_schedulers[-1]

    def add_slurm_scheduler(self, *args, **kwargs) -> WorkflowSlurmSchedulersModel:
        """Add a slurm_scheduler and return it."""
        self._slurm_schedulers.append(WorkflowSlurmSchedulersModel(*args, **kwargs))
        return self._slurm_schedulers[-1]

    def add_user_data(self, *args, **kwargs) -> WorkflowUserDataModel:
        """Add user data and return it."""
        self._user_data.append(WorkflowUserDataModel(*args, **kwargs))
        return self._user_data[-1]

    def build(self, *args, **kwargs) -> WorkflowSpecificationsModel:
        """Build a workflow specification from the stored parameters."""
        return WorkflowSpecificationsModel(
            *args,
            files=self._files,
            jobs=self._jobs,
            resource_requirements=self._resource_requirements,
            schedulers=WorkflowSpecificationsSchedulers(
                aws_schedulers=self._aws_schedulers or None,
                local_schedulers=self._local_schedulers or None,
                slurm_schedulers=self._slurm_schedulers or None,
            ),
            user_data=self._user_data,
            **kwargs
        )
