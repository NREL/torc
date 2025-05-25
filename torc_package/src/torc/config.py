from dynaconf import Dynaconf, Validator  # type: ignore


DEFAULT_SETTINGS_FILENAME = ".torc_settings.toml"
# DEFAULT_SECRETS_FILENAME = ".torc_secrets.toml"

torc_settings = Dynaconf(
    envvar_prefix="TORC",
    settings_files=[
        DEFAULT_SETTINGS_FILENAME,
        # DEFAULT_SECRETS_FILENAME,
    ],
    validators=[
        Validator("DATABASE_URL", default=None),
        Validator("OUTPUT_FORMAT", default="text"),
        Validator("FILTER_WORKFLOWS_BY_USER", default=True),
        Validator("CONSOLE_LEVEL", default="info"),
        Validator("FILE_LEVEL", default="info"),
        Validator("TIMINGS", default=False),
        Validator("WORKFLOW_KEY", default=None),
    ],
)
