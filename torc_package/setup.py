"""
setup.py
"""
import os
import logging
from setuptools import setup, find_packages


logger = logging.getLogger(__name__)


here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

version = None
with open(os.path.join(here, "torc", "version.py"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.strip().split()[2].strip('"').strip("'")

assert version is not None


setup(
    name="torc",
    version=version,
    description="Provides workflow automation services",
    long_description=readme,
    long_description_content_type="text/markdown",
    maintainer="Daniel Thom",
    maintainer_email="daniel.thom@nrel.gov",
    url="https://github.nrel.gov/dthom/torc",
    packages=find_packages(),
    package_dir={"torc": "torc"},
    entry_points={
        "console_scripts": [
            "torc=torc.cli.torc:cli",
        ],
    },
    include_package_data=True,
    license="BSD license",
    zip_safe=False,
    keywords=["hpc", "workflow"],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
    ],
    test_suite="tests",
    install_requires=[
        "click",
        "connectorx>=0.3.1",
        "graphviz",
        "json5",
        "plotly",
        "polars~=0.17.9",
        "psutil",
        "prettytable",
        "pyarrow",
        "pydantic~=2.0.2",
        "s3path",
        # These are required by the swagger_client. Keep in sync with its setup.py.
        "urllib3>=1.15",
        "six>=1.10",
        "certifi",
        "python-dateutil",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "furo",
            "ghp-import",
            "pre-commit",
            "pylint",
            "pytest",
            "pytest-cov",
            "sphinx",
            "sphinx-click",
            "sphinxcontrib-openapi",
            "sphinx-copybutton",
        ],
        "plots": [
            "networkx",
            "networkxgmml",
            "pygraphviz",
        ],
    },
)
