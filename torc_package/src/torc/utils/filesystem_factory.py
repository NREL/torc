"""Factory functions for filesystem paths, abstracts local vs cloud"""

# import re
from pathlib import Path

# import boto3
# from s3path import S3Path, register_configuration_parameter

# _s3_sessions = {}
# _REGEX_S3_PATH = re.compile(r"s3:\/\/(?P<bucket>[\w-]+)")


def make_path(path: str) -> Path:
    """Return an appropriate path instance for the current environment.

    Parameters
    ----------
    path : str

    Returns
    -------
    Path
    """
    if path.lower().startswith("s3"):
        msg = f"S3 is not supported yet {path=}"
        raise NotImplementedError(msg)
        # bucket = _get_bucket(path)
        # if bucket not in _s3_sessions:
        #    raise Exception(
        #        f"An S3 Session has not been created for bucket={bucket}. Please call create_s3_session."
        #    )
        # return _s3_sessions[bucket].path(path)
    return Path(path)


# def create_s3_session(path, profile_name):
#    """Create an S3 session with boto3. Only needs to be called once per bucket.
#
#    Parameters
#    ----------
#    path : str
#    profile_name : str
#    """
#    bucket = _get_bucket(path)
#    if bucket in _s3_sessions:
#        logger.info("Replacing an S3 session bucket={} profile_name={}", bucket, profile_name)
#    else:
#        logger.info("Creating an S3 session bucket={} profile_name={}", bucket, profile_name)
#    _s3_sessions[bucket] = _S3Session(profile_name, bucket)
#    if len(_s3_sessions) > 10:
#        raise Exception(
#            f"Possible bug: There are sessions for these buckets: {sorted(_s3_sessions.keys())}"
#        )
#
#
# def _get_bucket(path: str):
#    match = _REGEX_S3_PATH.search(path)
#    if not match:
#        raise Exception(f"Invalid S3 path format: {path}")
#    return match.groupdict()["bucket"]
#
#
# class _S3Session:
#    def __init__(self, profile_name, bucket):
#        self._bucket = bucket
#        self._base_path = f"s3://{self._bucket}"
#        self._session = boto3.session.Session(profile_name=profile_name)
#        self._client = self._session.client("s3")
#        register_configuration_parameter(S3Path("/"), resource=self._session.resource("s3"))
#
#    def path(self, path: str) -> S3Path:
#        """Return a path object from a string."""
#        if not path.startswith(self._base_path):
#            raise Exception(
#                f"path={path} does not start with the session's base path: {self._base_path}"
#            )
#        relpath = path.replace(self._base_path, "")
#        return S3Path(f"/{self._bucket}/{relpath}")
