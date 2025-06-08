"""Terminal-based management console"""

import getpass
import json
import os
import shutil
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll, Grid, Container
from textual.validation import Number
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Markdown,
    RadioButton,
    RadioSet,
    RichLog,
    Static,
    TabPane,
    TabbedContent,
)

from torc.openapi_client.api.default_api import DefaultApi
from torc.api import make_api, iter_documents
from torc.cli.common import parse_filters
from torc.cli.slurm import schedule_slurm_nodes, DEFAULT_OUTPUT_DIR, JOB_COMPLETION_POLL_INTERVAL
from torc.cli.workflows import (
    has_running_jobs,
    start_workflow,
    restart_workflow,
    cancel_workflow,
    create_workflow_from_json_file,
    reset_workflow_status,
    reset_workflow_job_status,
)
from torc.common import convert_timestamp
from torc.config import torc_settings
from torc.loggers import setup_logging


LOG_FILE = "torc-management-console.log"


# TODOs:
# - Need to implement async versions of API calls. Displays of large datatables are slow.
#   textualize supports a run_worker method to help once we have async calls.
#   OpenAPI client does have async support.
# - Ctrl-c while event monitoring timer thread is active doesn't work.


class TorcManagementConsole(App):
    """A Textual app to manage torc results."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "management_console.tcss"

    def __init__(
        self,
        *args,
        api: DefaultApi | None = None,
        database_url=None,
        log_file=LOG_FILE,
        log_level="INFO",
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        setup_logging(
            filename=log_file,
            console_level="ERROR",
            file_level=log_level,
            mode="a",
        )
        self._db_url = ""
        self._db_name = ""
        # This invalid default api is just a placeholder.
        self._api = api or make_api("invalid")
        self._event_monitor_timer: threading.Timer | None = None
        self._run_local_proc: Any | None = None
        self._run_local_proc_monitor: threading.Thread | None = None

        full_url = database_url or None
        if full_url is None:
            if torc_settings.database_url is not None:
                full_url = torc_settings.database_url

        if full_url is not None:
            self._db_url, db_name = full_url.split("/_db/")
            self._db_name = db_name.split("/torc-service")[0]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Header()
        yield Footer()
        with Grid(id="main_grid"):
            with Grid(id="database_grid"):
                with Vertical(id="controls_containers"):
                    yield Input(
                        value=self._db_url,
                        placeholder="Enter a database URL",
                        id="db_url",
                    )
                    yield Input(
                        value=self._db_name,
                        placeholder="Enter a database name",
                        id="db_name",
                    )
                    with Horizontal():
                        yield Button("Connect", id="connect", variant="success")
                        yield Checkbox("Filter by user", True, id="filter_by_user")
                    yield Static("Selected workflow key:")
                    yield Input(
                        placeholder="Enter a workflow key or select a row",
                        id="workflow_key",
                    )
                with Vertical():
                    yield VerticalScroll(DataTable(id="workflow_table"))
                    yield Input(
                        value="",
                        placeholder="connected URL",
                        id="connected_url",
                        disabled=True,
                    )
                    yield Markdown("", id="output_box")
            with TabbedContent():
                with TabPane("View Status"):
                    with Grid(id="document_table_grid"):
                        with Grid(id="document_table_controls_grid"):
                            with RadioSet(id="table_options", disabled=True):
                                for table_id, table in DATA_TABLES.items():
                                    assert isinstance(table["name"], str)
                                    yield RadioButton(table["name"], id=table_id)
                            with RadioSet(id="sort_options", disabled=True):
                                yield RadioButton("None", id="no_sorting", value=True)
                                yield RadioButton("Ascending", id="ascending")
                                yield RadioButton("Descending", id="descending")
                            yield Input(
                                placeholder="Filter, ex: column1=val1 column2=val2",
                                id="filter_value",
                            )
                            yield Input(
                                placeholder="Sort column",
                                id="sort_column",
                            )
                            yield Button(
                                "Refresh",
                                id="refresh_table",
                                disabled=True,
                                variant="primary",
                            )
                        yield VerticalScroll(DataTable(id="document_table"))
                with TabPane("Manage Workflow"):
                    with Grid(id="manage_workflow_grid"):
                        with Container():
                            cwd = os.getcwd()
                            yield Static(f"Path to workflow file (relative to {cwd}):")
                            yield Input(placeholder="workflow.json5", id="workflow_spec_file")
                            yield Checkbox(
                                "Select workflow on creation",
                                True,
                                id="select_created_workflow",
                            )
                            yield Button(
                                "Create", id="create_workflow", variant="primary", disabled=True
                            )
                        with Horizontal(classes="buttons"):
                            yield Button(
                                "Start", id="start_workflow", variant="primary", disabled=True
                            )
                            yield Button(
                                "Restart", id="restart_workflow", variant="warning", disabled=True
                            )
                            yield Button(
                                "Cancel", id="cancel_workflow", variant="error", disabled=True
                            )
                            yield Button(
                                "Reset", id="reset_workflow", variant="warning", disabled=True
                            )
                            yield Button(
                                "Delete", id="delete_workflow", variant="error", disabled=True
                            )
                with TabPane("Slurm Scheduler"):
                    with Grid(id="slurm_grid"):
                        with Container(id="controls_containers"):
                            with Grid(id="slurm_schedule_grid"):
                                yield Label("Selected Slurm scheduler:")
                                yield Input(
                                    placeholder="Slurm scheduler key",
                                    id="slurm_scheduler_key",
                                )
                                yield Label("Num Slurm jobs:")
                                yield Input(
                                    "1",
                                    placeholder="Number of Slurm jobs",
                                    id="num_slurm_jobs",
                                    validators=[Number(minimum=1)],
                                )
                                yield Button(
                                    "Schedule",
                                    id="schedule_slurm_nodes",
                                    disabled=True,
                                    variant="primary",
                                )
                                yield Checkbox(
                                    "1 worker per node",
                                    False,
                                    id="one_worker_per_compute_node",
                                )
                        yield VerticalScroll(DataTable(id="slurm_schedulers_table"))
                with TabPane("Local Worker"):
                    with Horizontal(id="local_worker_container"):
                        yield Button("Start", id="start_local_worker", variant="primary")
                        yield Button("Cancel", id="cancel_local_worker", variant="warning")
                        yield Button("Clear log", id="clear_local_worker_log", variant="primary")
                        # TODO: spacing is all off
                        yield Label("  Poll interval (s):")
                        yield Input(
                            "60",
                            placeholder="Poll interval (s)",
                            id="local_worker_poll_interval",
                            validators=[Number(minimum=10)],
                        )
                    yield RichLog(max_lines=1000, id="local_worker_log")
                with TabPane("Event Monitor"):
                    with Horizontal(id="event_monitor_container"):
                        yield Button("Start", id="start_event_monitor", variant="primary")
                        yield Button("Cancel", id="cancel_event_monitor", variant="warning")
                        yield Button("Clear log", id="clear_event_log", variant="primary")
                        # TODO: spacing is all off
                        yield Label("  Poll interval (s):")
                        yield Input(
                            "60",
                            placeholder="Poll interval (s)",
                            id="monitor_poll_interval",
                            validators=[Number(minimum=10)],
                        )
                    yield RichLog(max_lines=1000, id="event_log")

    def on_mount(self) -> None:
        """Called on first mount"""
        self.query_one("#table_options", RadioSet).tooltip = "Select a document table to display."
        self.query_one(
            "#start_workflow", Button
        ).tooltip = "Move job statuses from uninitialized to ready or blocked."
        self.query_one(
            "#restart_workflow", Button
        ).tooltip = "Move incomplete/canceled/terminated job statuses to ready or blocked."
        self.query_one(
            "#cancel_workflow", Button
        ).tooltip = "Cancel the workflow and all running jobs."
        self.query_one(
            "#create_workflow", Button
        ).tooltip = "Create a workflow from a JSON/JSON5 file or Python script."
        self.query_one("#reset_workflow", Button).tooltip = "Reset all statuses to uninitialized."
        self.query_one("#delete_workflow", Button).tooltip = "Cannot be undone!"
        self.query_one(
            "#start_local_worker", Button
        ).tooltip = "Run all jobs on the current system."
        self.query_one("#cancel_local_worker", Button).tooltip = "Cancel the local worker."
        self.query_one("#clear_local_worker_log", Button).tooltip = "Clear the local worker log."
        self.query_one("#local_worker_poll_interval", Input).tooltip = "Must be >= than 10"
        self.query_one(
            "#one_worker_per_compute_node", Checkbox
        ).tooltip = "Only applies to multi-node jobs."
        self.query_one("#start_event_monitor", Button).tooltip = "Start monitoring for events."
        self.query_one("#monitor_poll_interval", Input).tooltip = "Must be >= than 10"
        self.query_one(
            "#refresh_table", Button
        ).tooltip = "Refresh the table with sorting and filtering applied."
        self.query_one("#filter_value", Input).tooltip = "Filter by one or more values."
        self.query_one("#sort_options", RadioSet).tooltip = "Sort order"
        self.query_one(
            "#sort_column", Input
        ).tooltip = "Enter sort column or click on table header."
        for table in self.query(DataTable):
            table.zebra_stripes = True
            table.cursor_type = "row"
            table.show_row_labels = True

    # async def on_input_changed(self, message: Input.Changed) -> None:
    #    """Called when an Input box changes"""

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Event handler when a DataTable header is selected."""
        self._clear_output_box()
        if event.data_table.id == "document_table":
            assert event.column_key.value is not None
            self.query_one("#sort_column", Input).value = event.column_key.value

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Event handler when a DataTable row is selected."""
        self._clear_output_box()
        if event.data_table.id == "workflow_table":
            assert event.row_key.value is not None
            self.query_one("#workflow_key", Input).value = event.row_key.value
            self.query_one("#table_options", RadioSet).disabled = False
            self.query_one("#sort_options", RadioSet).disabled = False
            self.query_one("#document_table", DataTable).clear(columns=True)
            self._populate_slurm_schedulers()
            self._set_workflow_widgets(True)
        elif event.data_table.id == "slurm_schedulers_table":
            assert event.row_key.value is not None
            self.query_one("#slurm_scheduler_key", Input).value = event.row_key.value

    def on_button_pressed(self, event: Button.Pressed) -> None:  # noqa: C901
        """Event handler called when a button is pressed."""
        self._clear_output_box()
        match event.button.id:
            case "connect":
                self._connect()
            case "refresh_table":
                self._show_document_table()
            case "create_workflow":
                self._create_workflow()
            case "start_workflow":
                self._start_workflow()
            case "restart_workflow":
                self._restart_workflow()
            case "cancel_workflow":
                self._cancel_workflow()
            case "reset_workflow":
                self._reset_workflow()
            case "delete_workflow":
                self._delete_workflow()
            case "start_local_worker":
                self._start_local_worker()
            case "cancel_local_worker":
                self._cancel_local_worker()
            case "clear_local_worker_log":
                self._clear_local_worker_log()
            case "schedule_slurm_nodes":
                self._schedule_slurm_nodes()
            case "start_event_monitor":
                self._start_event_monitor()
            case "cancel_event_monitor":
                self._cancel_event_monitor()
            case "clear_event_log":
                self._clear_event_log()
            case _:
                msg = f"{event.button.id=}"
                raise NotImplementedError(msg)

    def on_checkbox_changed(self, event: Checkbox.Changed):
        """Event handler called when a checkbox is changed."""
        match event.checkbox.id:
            case "filter_by_user":
                self._connect()
            case "select_created_workflow":
                pass
            case _:
                msg = f"{event.checkbox.id=}"
                raise NotImplementedError(msg)

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Event handler called when a RadioSet changes"""
        if event.radio_set.id == "table_options":
            self.query_one("#filter_value", Input).value = ""
            self.query_one("#sort_column", Input).value = ""
            self._show_document_table()

    def shutdown(self):
        """Perform shutdown activities."""
        if self._event_monitor_timer is not None:
            self._event_monitor_timer.cancel()
        self._event_monitor_timer = None

    def _check_db_name(self):
        db_name = self.query_one("#db_name", Input).value
        if not db_name:
            self._post_error_msg("Database name is not set")
        return db_name

    def _check_db_url(self):
        db_url = self.query_one("#db_url", Input).value
        if not db_url:
            self._post_error_msg("Database URL is not set")
        return db_url

    def _check_full_url(self):
        url = self._check_db_url()
        if not url:
            return None
        db_name = self._check_db_name()
        if not db_name:
            return None
        return f"{url}/_db/{db_name}/torc-service"

    def _check_num_slurm_jobs(self):
        num_slurm_jobs = self.query_one("#num_slurm_jobs", Input).value
        if not num_slurm_jobs:
            self._post_error_msg("Please choose a number of Slurm jobs to start.")
            return None
        return int(num_slurm_jobs)

    def _check_slurm_scheduler_key(self):
        key = self.query_one("#slurm_scheduler_key", Input).value
        if not key:
            self._post_error_msg("No slurm scheduler key is selected")
        return key

    def _check_workflow_key(self):
        key = self.query_one("#workflow_key", Input).value
        if not key:
            self._post_error_msg("No workflow key is selected")
        return key

    def _check_workflow_spec_file(self) -> Path | None:
        path = self.query_one("#workflow_spec_file", Input).value
        if not path:
            self._post_error_msg("Please enter the path to a workflow file.")
            return None
        return Path(path)

    def _check_url(self):
        url = self.query_one("#connected_url", Input).value
        if not url:
            self._post_error_msg("The database URL must be set.")
        return url

    def _check_running_jobs(self, key, op):
        if has_running_jobs(self._api, key):
            self._post_error_msg(f"Cannot {op} a workflow while jobs are running.")
            return False
        return True

    def _connect(self):
        full_url = self._check_full_url()
        if full_url is None:
            return
        self._api = make_api(full_url)
        latest_workflow = self._show_workflow_table()
        workflow_key = "" if latest_workflow is None else latest_workflow
        self.query_one("#document_table", DataTable).clear(columns=True)
        self.query_one("#slurm_schedulers_table", DataTable).clear(columns=True)
        self.query_one("#connect", Button).variant = "primary"
        self.query_one("#workflow_key", Input).value = workflow_key
        self.query_one("#connected_url", Input).value = full_url
        self.query_one("#create_workflow", Button).disabled = False

        if latest_workflow is not None:
            self._populate_slurm_schedulers()
            self._set_workflow_widgets(True)

    def _populate_slurm_schedulers(self):
        key = self.query_one("#workflow_key", Input).value
        if not key:
            return

        table = self.query_one("#slurm_schedulers_table", DataTable)
        build_document_table(table, "slurm_schedulers", self._api, key)

    def _set_workflow_widgets(self, value: bool):
        for name in ("table_options", "sort_options"):
            self.query_one(f"#{name}", RadioSet).disabled = not value

        for name in (
            "refresh_table",
            "start_workflow",
            "restart_workflow",
            "cancel_workflow",
            "reset_workflow",
            "delete_workflow",
            "schedule_slurm_nodes",
            "start_local_worker",
            "cancel_local_worker",
            "clear_local_worker_log",
        ):
            self.query_one(f"#{name}", Button).disabled = not value

    def _show_workflow_table(self) -> str | None:
        filters = (
            {"user": getpass.getuser()}
            if self.query_one("#filter_by_user", Checkbox).value
            else {}
        )
        table = self.query_one("#workflow_table", DataTable)
        table.clear(columns=True)
        # TODO: A long description causes the last row to be hidden.
        # for col in ("key", "user", "name", "timestamp", "description"):
        for col in ("key", "user", "name", "timestamp"):
            table.add_column(col, key=col)
        workflows = list(iter_documents(self._api.list_workflows, **filters))
        workflows.sort(
            key=lambda x: datetime.fromisoformat(x.timestamp.replace("Z", "")),
            reverse=True,
        )
        latest_workflow: str | None = None
        for i, workflow in enumerate(workflows, start=1):
            if i == 1:
                latest_workflow = workflow.key
            table.add_row(
                workflow.key,
                workflow.user,
                workflow.name,
                workflow.timestamp,
                # workflow.description,
                key=workflow.key,
                label=str(i),
            )
        return latest_workflow

    def _show_document_table(self):
        radio_set = self.query_one("#table_options", RadioSet)
        assert radio_set.pressed_button is not None
        table_id = radio_set.pressed_button.id
        assert table_id is not None
        table = self.query_one("#document_table", DataTable)
        filter_value = self.query_one("#filter_value", Input).value.strip()
        if filter_value != "":
            filters = parse_filters(filter_value.split())
        else:
            filters = {}
        builder = DATA_TABLES[table_id]["table_builder"]
        workflow_key = self._check_workflow_key()
        if not workflow_key:
            return
        try:
            builder(table, table_id, self._api, workflow_key, **filters)
            sort_column = self.query_one("#sort_column", Input).value
            mode = self.query_one("#sort_options", RadioSet).pressed_button.id  # type: ignore
            if sort_column and mode != "no_sorting":
                table.sort(sort_column, reverse=mode == "descending")
        except Exception as exc:
            self._post_error_msg(str(exc))

    def _create_workflow(self):
        url = self._check_url()
        if not url:
            return

        filename = self._check_workflow_spec_file()
        if not filename:
            return

        if filename.is_dir():
            self._post_error_msg(f"{filename} is a directory")

        if not filename.exists():
            self._post_error_msg(f"{filename} does not exist")
            return

        success = False
        if filename.suffix == ".py":
            proc = subprocess.run(
                [sys.executable, filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            if proc.returncode == 0:
                self._post_info_msg(proc.stdout)
                success = True
            else:
                self._post_error_msg(proc.stdout)
        else:
            try:
                workflow = create_workflow_from_json_file(
                    self._api, filename, user=getpass.getuser()
                )
                self._post_info_msg(f"Created workflow key {workflow.key}")
            except Exception as exc:
                self._post_error_msg(f"Failed to create workflow: {exc}")

        if success:
            latest_workflow = self._show_workflow_table()
            if latest_workflow and self.query_one("#select_created_workflow").value:  # type: ignore
                self.query_one("#workflow_key", Input).value = latest_workflow  # type: ignore
                self._set_workflow_widgets(True)

    def _start_workflow(self):
        url = self._check_url()
        if not url:
            return

        key = self._check_workflow_key()
        if not key:
            return

        if has_running_jobs(self._api, key):
            self._post_error_msg("Cannot start a workflow while jobs are running.")
            return

        done_jobs = self._api.list_jobs(key, status="done", limit=1).items
        if done_jobs:
            self._post_error_msg(
                "Cannot start when jobs have completed. Please reset the workflow first."
            )
            return

        try:
            start_workflow(self._api, key)
            self._post_info_msg(
                f"Started workflow {key}. Check the jobs table for ready jobs and schedule nodes."
            )
        except Exception as exc:
            self._post_error_msg(f"Failed to start workflow: {exc}")

    def _restart_workflow(self):
        url = self._check_url()
        if not url:
            return

        key = self._check_workflow_key()
        if not key:
            return

        if not self._check_running_jobs(key, "restart"):
            return

        try:
            restart_workflow(self._api, key)
            self._post_info_msg(
                f"Restarted workflow {key}. Check the jobs table for ready jobs and schedule nodes."
            )
        except Exception as exc:
            self._post_error_msg(f"Failed to restart workflow: {exc}")

    def _reset_workflow(self):
        url = self._check_url()
        if not url:
            return

        key = self._check_workflow_key()
        if not key:
            return

        try:
            reset_workflow_status(self._api, key)
            reset_workflow_job_status(self._api, key)
            self._post_info_msg(f"Reset workflow {key}")
        except Exception as exc:
            self._post_error_msg(f"Failed to reset workflow: {exc}")

    def _cancel_workflow(self):
        url = self._check_url()
        if not url:
            return

        key = self._check_workflow_key()
        if not key:
            return

        try:
            cancel_workflow(self._api, key)
            self._post_info_msg(f"Canceled workflow {key}")
        except Exception as exc:
            self._post_error_msg(f"Failed to cancel workflow: {exc}")

    def _delete_workflow(self):
        url = self._check_url()
        if not url:
            return

        key = self._check_workflow_key()
        if not key:
            return

        try:
            self._api.remove_workflow(key)
            logger.info("Deleted workflow {}", key)
            self._post_info_msg(f"Deleted workflow {key}")
            self._connect()
        except Exception as exc:
            self._post_error_msg(f"Failed to delete workflow: {exc}")

    def _schedule_slurm_nodes(self):
        workflow_key = self._check_workflow_key()
        if not workflow_key:
            return

        scheduler_key = self._check_slurm_scheduler_key()
        if not scheduler_key:
            return

        num_slurm_jobs = self._check_num_slurm_jobs()
        if not num_slurm_jobs:
            return

        ready_jobs = self._api.list_jobs(workflow_key, status="ready", limit=1)
        if not ready_jobs.items:
            ready_jobs = self._api.list_jobs(workflow_key, status="scheduled", limit=1)
        if not ready_jobs.items:
            self._post_error_msg("No jobs are in the ready state. Did you start the workflow?")
            return

        start_one_worker_per_node = self.query_one("#one_worker_per_compute_node", Checkbox).value
        config = self._api.get_slurm_scheduler(workflow_key, scheduler_key)
        poll_interval = int(
            os.environ.get("TORC_JOB_COMPLETION_POLL_INTERVAL", JOB_COMPLETION_POLL_INTERVAL)
        )
        try:
            schedule_slurm_nodes(
                self._api,
                workflow_key,
                config,
                Path(DEFAULT_OUTPUT_DIR),
                num_hpc_jobs=num_slurm_jobs,
                start_one_worker_per_node=start_one_worker_per_node,
                poll_interval=poll_interval,
            )
            self._post_info_msg(
                f"Scheduled {num_slurm_jobs} Slurm job(s) for workflow {workflow_key}"
            )
        except Exception as exc:
            self._post_error_msg(f"Failed to schedule nodes: {exc}")

    def _start_local_worker(self):
        url = self._check_url()
        if not url:
            return

        workflow_key = self._check_workflow_key()
        if not workflow_key:
            return

        ready_jobs = self._api.list_jobs(workflow_key, status="ready", limit=1)
        if not ready_jobs.items:
            ready_jobs = self._api.list_jobs(workflow_key, status="scheduled", limit=1)
        if not ready_jobs.items:
            self._post_error_msg("No jobs are in the ready state. Did you start the workflow?")
            return
        if self._run_local_proc is not None:
            self._post_error_msg("There is already one worker running on the current system.")
            return

        poll_interval_str = self.query_one("#local_worker_poll_interval", Input).value
        if not poll_interval_str:
            return
        poll_interval = int(poll_interval_str)
        try:
            cmd = [
                shutil.which("torc"),
                "-c",
                "info",
                "-u",
                url,
                "jobs",
                "run",
                "-p",
                str(poll_interval),
                "-o",
                DEFAULT_OUTPUT_DIR,
            ]
            self._run_local_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            self._post_info_msg(f"Started local worker for workflow {workflow_key}")
        except Exception as exc:
            self._post_error_msg(f"Failed to start local worker: {exc}")

        self._run_local_proc_monitor = threading.Thread(target=self._monitor_local_worker)
        self._run_local_proc_monitor.start()

    def _cancel_local_worker(self):
        if self._run_local_proc is None:
            return
        self._run_local_proc.terminate()
        self._run_local_proc = None
        self._post_info_msg("Canceled the local worker.")

    def _monitor_local_worker(self):
        if self._run_local_proc is None:
            return
        for line in iter(self._run_local_proc.stdout.readline, ""):
            self.query_one("#local_worker_log", RichLog).write(line.strip())
        self.query_one("#local_worker_log", RichLog).write("finished with iter, now call wait")
        ret = self._run_local_proc.wait()
        self._run_local_proc = None
        self.query_one("#local_worker_log", RichLog).write(
            f"wait completed, exiting monitor thread {ret=}"
        )

    def _clear_local_worker_log(self):
        self.query_one("#local_worker_log", RichLog).clear()

    def _start_event_monitor(self):
        workflow_key = self._check_workflow_key()
        if not workflow_key:
            return
        poll_interval_str = self.query_one("#monitor_poll_interval", Input).value
        if not poll_interval_str:
            return
        poll_interval = int(poll_interval_str)

        timestamp = self._api.get_latest_event_timestamp(workflow_key)["timestamp"]  # type: ignore
        self._event_monitor_timer = threading.Timer(
            poll_interval, self._run_monitor, (workflow_key, poll_interval, timestamp)
        )
        self._event_monitor_timer.start()
        self.query_one("#event_log", RichLog).write("Started event monitoring")

    def _run_monitor(self, workflow_key, poll_interval, timestamp):
        try:
            event_ = None
            for event in iter_documents(
                self._api.get_events_after_timestamp, workflow_key, timestamp
            ):
                event.pop("_id")
                event.pop("_rev")
                event["datetime"] = str(convert_timestamp(event["timestamp"]))
                self.query_one("#event_log", RichLog).write(json.dumps(event, indent=2))
                event_ = event
            if event_ is not None:
                timestamp = event_["timestamp"]
        except Exception as e:
            self.query_one("#event_log", RichLog).write(f"failed to get events {e}")

        self._event_monitor_timer = threading.Timer(
            poll_interval, self._run_monitor, (workflow_key, poll_interval, timestamp)
        )
        self._event_monitor_timer.start()

    def _cancel_event_monitor(self):
        if self._event_monitor_timer is not None:
            self._event_monitor_timer.cancel()
            self.query_one("#event_log", RichLog).write("Canceled event monitoring")
        self._event_monitor_timer = None

    def _clear_event_log(self):
        self.query_one("#event_log", RichLog).clear()

    def _post_info_msg(self, message):
        widget = self.query_one("#output_box", Markdown)
        widget.update(
            f"""
# Info
{message}
"""
        )

    def _post_error_msg(self, message):
        widget = self.query_one("#output_box", Markdown)
        widget.update(
            f"""
# ⚠️ Error ⚠️
{message}
"""
        )

    def _clear_output_box(self):
        widget = self.query_one("#output_box", Markdown)
        widget.update("")


def init_table(table, columns):
    """Initialize the datatable."""
    table.clear(columns=True)
    for column in columns:
        table.add_column(column, key=column)


def build_compute_node_table(table, table_id, api, workflow_key, **filters):
    """Build a table of compute nodes"""
    columns = DATA_TABLES[table_id]["columns"]
    init_table(table, columns)
    for i, item in enumerate(
        iter_documents(api.list_compute_nodes, workflow_key, **filters),
        start=1,
    ):
        data = item.dict()
        values = []
        for column in columns:
            if column == "scheduler_id":
                if data["scheduler"].get("hpc_type") == "slurm":
                    values.append(data["scheduler"]["slurm_job_id"])
                else:
                    values.append("Unknown")
            elif column == "duration (s)":
                values.append(data.get("duration_seconds", ""))
            else:
                values.append(data[column])
        table.add_row(*values, key=item.key, label=str(i))


def build_document_table(table, table_id, api, workflow_key, **filters):
    """Build a table of any document type"""
    columns = DATA_TABLES[table_id]["columns"]
    init_table(table, columns)
    method = getattr(api, DATA_TABLES[table_id]["method"])
    for i, item in enumerate(iter_documents(method, workflow_key, **filters), start=1):
        values = [getattr(item, col) for col in columns]
        table.add_row(*values, key=getattr(item, "key"), label=str(i))


def build_event_table(table, table_id, api, workflow_key, **filters):
    """Build a table of events"""
    columns = DATA_TABLES[table_id]["columns"]
    init_table(table, columns)
    for i, item in enumerate(
        iter_documents(api.list_events, workflow_key, **filters),
        start=1,
    ):
        table.add_row(*make_event(item), key=item["_key"], label=str(i))


def make_event(data: dict):
    """Make an event with only desired fields"""
    event = {"timestamp": str(convert_timestamp(data["timestamp"]))}
    for key in ("category", "type", "message"):
        event[key] = data.get(key, "")
    return tuple(event.values())


def build_results_table(table, table_id, api, workflow_key, **filters):
    """Build a table of results"""
    columns = DATA_TABLES[table_id]["columns"]
    init_table(table, columns)
    key_to_job_name = {x.key: x.name for x in iter_documents(api.list_jobs, workflow_key)}
    for i, item in enumerate(
        iter_documents(api.list_results, workflow_key, **filters),
        start=1,
    ):
        values = []
        for col in columns:
            if col == "job_name":
                values.append(key_to_job_name[item.job_key])
            else:
                values.append(getattr(item, col))
        table.add_row(*values, key=item.key, label=str(i))


DATA_TABLES: dict[str, dict[str, Any]] = {
    "compute_nodes": {
        "name": "Compute Nodes",
        "columns": (
            "hostname",
            "is_active",
            "scheduler_id",
            "start_time",
            "duration (s)",
        ),
        "table_builder": build_compute_node_table,
    },
    "events": {
        "name": "Events",
        "columns": ("timestamp", "category", "type", "message"),
        "table_builder": build_event_table,
    },
    "jobs": {
        "name": "Jobs",
        "columns": ("name", "status", "key"),
        "method": "list_jobs",
        "table_builder": build_document_table,
    },
    "resource_requirements": {
        "name": "Resource Requirements",
        "columns": (
            "name",
            "num_cpus",
            "num_gpus",
            "num_nodes",
            "memory",
            "runtime",
            "key",
        ),
        "method": "list_resource_requirements",
        "table_builder": build_document_table,
    },
    "results": {
        "name": "Results",
        "columns": (
            "job_name",
            "job_key",
            "run_id",
            "return_code",
            "exec_time_minutes",
            "completion_time",
        ),
        "table_builder": build_results_table,
    },
    "scheduled_compute_nodes": {
        "name": "Scheduled Nodes",
        "columns": ("scheduler_id", "status"),
        "method": "list_scheduled_compute_nodes",
        "table_builder": build_document_table,
    },
    "slurm_schedulers": {
        "name": "Slurm Schedulers",
        "columns": (
            "name",
            "account",
            "walltime",
            "gres",
            "mem",
            "nodes",
            "qos",
            "tmp",
            "extra",
            "key",
        ),
        "method": "list_slurm_schedulers",
        "table_builder": build_document_table,
    },
}

SHOW_BUTTONS = {f"show_{x}" for x in DATA_TABLES}


if __name__ == "__main__":
    app = TorcManagementConsole()
    try:
        app.run()
    except KeyboardInterrupt:
        app.shutdown()
        raise
