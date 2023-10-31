"""Helper code to build a workflow dynamically"""

import getpass

from torc.openapi_client.models.files_model import FilesModel
from torc.openapi_client.models.job_specifications_model import (
    JobSpecificationsModel,
)
from torc.openapi_client.models.compute_node_resource_stats_model import (
    ComputeNodeResourceStatsModel,
)
from torc.openapi_client.models.workflow_config_model import WorkflowConfigModel
from torc.openapi_client.models.resource_requirements_model import (
    ResourceRequirementsModel,
)
from torc.openapi_client.models.workflow_specifications_model import (
    WorkflowSpecificationsModel,
)
from torc.openapi_client.models.aws_schedulers_model import (
    AwsSchedulersModel,
)
from torc.openapi_client.models.local_schedulers_model import (
    LocalSchedulersModel,
)
from torc.openapi_client.models.slurm_schedulers_model import (
    SlurmSchedulersModel,
)
from torc.openapi_client.models.workflow_specifications_schedulers import (
    WorkflowSpecificationsSchedulers,
)
from torc.openapi_client.models.user_data_model import UserDataModel
from torc.common import check_function


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
        self._compute_node_wait_for_new_jobs_seconds = 0
        self._compute_node_ignore_workflow_completion = False
        self._compute_node_expiration_buffer_seconds = None
        self._compute_node_wait_for_healthy_database = None
        self._prepare_jobs_sort_method = "gpus_runtime_memory"

    def add_file(self, *args, **kwargs) -> FilesModel:
        """Add a file and return it."""
        self._files.append(FilesModel(*args, **kwargs))
        return self._files[-1]

    def add_job(self, *args, **kwargs) -> JobSpecificationsModel:
        """Add a job and return it."""
        self._jobs.append(JobSpecificationsModel(*args, **kwargs))
        return self._jobs[-1]

    def map_function_to_jobs(
        self,
        module: str,
        func: str,
        params: list[dict],
        postprocess_func: str | None = None,
        module_directory=None,
        resource_requirements=None,
        scheduler=None,
        start_index=0,
        name_prefix="",
    ) -> list[JobSpecificationsModel]:
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
        postprocess_func : str
            Optional name of the function in module to be called to postprocess all results.
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
        list[JobSpecificationsModel]
        """
        jobs = []
        output_data_names = []
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
            output_data_names.append(output_ud.name)
            job = self.add_job(
                name=job_name,
                command="torc jobs run-function",
                input_user_data=[input_ud.name],
                output_user_data=[output_ud.name],
                resource_requirements=resource_requirements,
                scheduler=scheduler,
            )
            jobs.append(job)

        if postprocess_func is not None:
            check_function(module, postprocess_func, module_directory)
            data = {
                "module": module,
                "func": postprocess_func,
            }
            if module_directory is not None:
                data["module_directory"] = module_directory
            input_ud = self.add_user_data(name="input_postprocess", data=data)
            output_ud = self.add_user_data(name="postprocess_result", data=data)
            self.add_job(
                name="postprocess",
                command="torc jobs run-postprocess",
                input_user_data=[input_ud.name] + output_data_names,
                output_user_data=[output_ud.name],
                resource_requirements=resource_requirements,
                scheduler=scheduler,
            )

        return jobs

    def add_resource_requirements(self, *args, **kwargs) -> ResourceRequirementsModel:
        """Add a resource_requirement and return it."""
        self._resource_requirements.append(ResourceRequirementsModel(*args, **kwargs))
        return self._resource_requirements[-1]

    def add_aws_scheduler(self, *args, **kwargs) -> AwsSchedulersModel:
        """Add a slurm_scheduler and return it."""
        self._aws_schedulers.append(AwsSchedulersModel(*args, **kwargs))
        return self._aws_schedulers[-1]

    def add_local_scheduler(self, *args, **kwargs) -> LocalSchedulersModel:
        """Add a slurm_scheduler and return it."""
        self._local_schedulers.append(LocalSchedulersModel(*args, **kwargs))
        return self._local_schedulers[-1]

    def add_slurm_scheduler(self, *args, **kwargs) -> SlurmSchedulersModel:
        """Add a slurm_scheduler and return it."""
        self._slurm_schedulers.append(SlurmSchedulersModel(*args, **kwargs))
        return self._slurm_schedulers[-1]

    def add_user_data(self, *args, **kwargs) -> UserDataModel:
        """Add user data and return it."""
        self._user_data.append(UserDataModel(*args, **kwargs))
        return self._user_data[-1]

    def configure_resource_monitoring(self, *args, **kwargs):
        """Configure resource monitoring for the workflow. Refer to
        ComputeNodeResourceStatsModel for input parameters."""
        self._resource_monitor_config = ComputeNodeResourceStatsModel(*args, **kwargs)

    @property
    def compute_node_wait_for_new_jobs_seconds(self) -> int:
        """Return the value for compute_node_wait_for_new_jobs_seconds."""
        return self._compute_node_wait_for_new_jobs_seconds

    @compute_node_wait_for_new_jobs_seconds.setter
    def compute_node_wait_for_new_jobs_seconds(self, val):
        """Inform all compute nodes to wait for new jobs for this time period before exiting.
        Does not apply if the workflow is complete.

        Parameters
        ----------
        val : int
            Number of seconds to wait for new jobs before exiting.
        """
        self._compute_node_wait_for_new_jobs_seconds = val

    @property
    def compute_node_ignore_workflow_completion(self) -> bool:
        """Return the value for compute_node_ignore_workflow_completion."""
        return self._compute_node_ignore_workflow_completion

    @compute_node_ignore_workflow_completion.setter
    def compute_node_ignore_workflow_completion(self, val):
        """Inform all compute nodes to ignore workflow completions and hold onto allocations
        indefinitely. Useful for debugging failed jobs and possibly dynamic workflows where jobs
        get added after starting.

        Parameters
        ----------
        val : bool
            Enable or disable; default is disabled.
        """
        self._compute_node_ignore_workflow_completion = val

    @property
    def compute_node_expiration_buffer_seconds(self) -> int | None:
        """Return the value for compute_node_expiration_buffer_seconds."""
        return self._compute_node_expiration_buffer_seconds

    @compute_node_expiration_buffer_seconds.setter
    def compute_node_expiration_buffer_seconds(self, val):
        """Inform all compute nodes to shut down this number of seconds before the
        expiration time. This allows torc to send SIGTERM to all job processes and set all
        statuses to terminated. Increase the time in cases where the job processes handle SIGTERM
        and need more time to gracefully shut down. Set the value to 0 to maximize the time given
        to jobs. If not set, take the database's default value of 30 seconds.

        Parameters
        ----------
        val : int
            Number of seconds before expiration time to terminate jobs.
        """
        self._compute_node_expiration_buffer_seconds = val

    @property
    def compute_node_wait_for_healthy_database_minutes(self) -> int | None:
        """Return the value for compute_node_wait_for_healthy_database_minutes."""
        return self._compute_node_wait_for_healthy_database

    @compute_node_wait_for_healthy_database_minutes.setter
    def compute_node_wait_for_healthy_database_minutes(self, val):
        """Inform all compute nodes to wait this number of minutes if the database becomes
        unresponsive.

        Parameters
        ----------
        val : int
            Number of minutes to wait for an unresponsive database before exiting.
        """
        self._compute_node_wait_for_healthy_database = val

    @property
    def prepare_jobs_sort_method(self) -> str:
        """Return the value for prepare_jobs_sort_method."""
        return self._prepare_jobs_sort_method

    @prepare_jobs_sort_method.setter
    def prepare_jobs_sort_method(self, val):
        """Inform all compute nodes to use this sort method when calling the
        prepare_jobs_for_submission command.

        Parameters
        ----------
        val : str
            Sort method, defaults to gpus_runtime_memory
        """
        self._prepare_jobs_sort_method = val

    @property
    def files(self) -> list[FilesModel]:
        """Return a reference to the files list."""
        return self._files

    @property
    def jobs(self) -> list[JobSpecificationsModel]:
        """Return a reference to the jobs list."""
        return self._jobs

    @property
    def resource_monitor_config(self) -> list[ResourceRequirementsModel]:
        """Return a reference to the resource requirements list."""
        return self._resource_requirements

    @property
    def resource_requirements(self) -> ComputeNodeResourceStatsModel | None:
        """Return a reference to the resource requirements list."""
        return self._resource_monitor_config

    def build(self, *args, **kwargs) -> WorkflowSpecificationsModel:
        """Build a workflow specification from the stored parameters."""
        config = WorkflowConfigModel(
            compute_node_resource_stats=self._resource_monitor_config,
            compute_node_wait_for_new_jobs_seconds=self._compute_node_wait_for_new_jobs_seconds,
            compute_node_ignore_workflow_completion=self._compute_node_ignore_workflow_completion,
            compute_node_expiration_buffer_seconds=self._compute_node_expiration_buffer_seconds,
            compute_node_wait_for_healthy_database=self._compute_node_wait_for_healthy_database,
            prepare_jobs_sort_method=self._prepare_jobs_sort_method,
        )
        if not kwargs.get("user"):
            kwargs["user"] = getpass.getuser()
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
