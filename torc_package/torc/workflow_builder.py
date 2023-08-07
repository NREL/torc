"""Helper code to build a workflow dynamically"""


from torc.swagger_client.models.workflow_files_model import WorkflowFilesModel
from torc.swagger_client.models.workflow_job_specifications_model import (
    WorkflowJobSpecificationsModel,
)
from torc.swagger_client.models.workflow_config_compute_node_resource_stats import (
    WorkflowConfigComputeNodeResourceStats,
)
from torc.swagger_client.models.workflow_config_model import WorkflowConfigModel
from torc.swagger_client.models.workflow_resource_requirements_model import (
    WorkflowResourceRequirementsModel,
)
from torc.swagger_client.models.workflow_specifications_model import (
    WorkflowSpecificationsModel,
)
from torc.swagger_client.models.workflow_aws_schedulers_model import (
    WorkflowAwsSchedulersModel,
)
from torc.swagger_client.models.workflow_local_schedulers_model import (
    WorkflowLocalSchedulersModel,
)
from torc.swagger_client.models.workflow_slurm_schedulers_model import (
    WorkflowSlurmSchedulersModel,
)
from torc.swagger_client.models.workflow_specifications_schedulers import (
    WorkflowSpecificationsSchedulers,
)
from torc.swagger_client.models.workflow_user_data_model import WorkflowUserDataModel
from torc.cli.run_function import check_function


class WorkflowBuilder:
    """Helper class to build a workflow dynamically"""

    def __init__(self):
        self._files = []
        self._jobs = []
        self._resource_monitor_config = None
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

    def map_function_to_jobs(
        self,
        module: str,
        func: str,
        params: list[dict],
        module_directory=None,
        resource_requirements=None,
        scheduler=None,
        start_index=0,
        name_prefix="",
    ) -> list[WorkflowJobSpecificationsModel]:
        """Add a job that will call func for each item in params.

        Parameters
        ----------
        module : str
            Name of module that contains func. If it is not available in the Python path, specify
            the parent directory in module_directory.
        func : str
            Name of the function in module to be called.
        params : list[dict]
            Each item in this list will be passed to func. The contents must be serializable to
            JSON.
        module_directory : str | None
            Required if module is not importable.
        resource_requirements : str | None
            Optional name of resource_requirements that should be used by each job.
        scheduler : str | None
            Optional name of scheduler that should be used by each job.
        start_index : int
            Starting index to use for job names.
        name_prefix : str
            Prepend job names with this prefix; defaults to an empty string. Names will be the
            index converted to a string.

        Returns
        -------
        list[WorkflowJobSpecificationsModel]
        """
        jobs = []
        for i, job_params in enumerate(params, start=start_index):
            check_function(module, func, module_directory)
            data = {
                "module": module,
                "func": func,
                "params": job_params,
            }
            if module_directory is not None:
                data["module_directory"] = module_directory
            job_name = f"{name_prefix}{i}"
            input_ud = self.add_user_data(name=f"input_{job_name}", data=data)
            output_ud = self.add_user_data(name=f"output_{job_name}", data=data)
            job = self.add_job(
                name=job_name,
                command="torc jobs run-function",
                consumes_user_data=[input_ud.name],
                stores_user_data=[output_ud.name],
                resource_requirements=resource_requirements,
                scheduler=scheduler,
            )
            jobs.append(job)

        return jobs

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

    def configure_resource_monitoring(self, *args, **kwargs):
        """Configure resource monitoring for the workflow. Refer to
        WorkflowConfigComputeNodeResourceStats for input parameters."""
        self._resource_monitor_config = WorkflowConfigComputeNodeResourceStats(*args, **kwargs)

    def build(self, *args, **kwargs) -> WorkflowSpecificationsModel:
        """Build a workflow specification from the stored parameters."""
        config = WorkflowConfigModel(compute_node_resource_stats=self._resource_monitor_config)
        return WorkflowSpecificationsModel(
            *args,
            config=config,
            files=self._files or None,
            jobs=self._jobs or None,
            resource_requirements=self._resource_requirements or None,
            schedulers=WorkflowSpecificationsSchedulers(
                aws_schedulers=self._aws_schedulers or None,
                local_schedulers=self._local_schedulers or None,
                slurm_schedulers=self._slurm_schedulers or None,
            ),
            user_data=self._user_data or None,
            **kwargs,
        )
