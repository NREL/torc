"""
setup.py
"""
import os
import logging
from codecs import open
from pathlib import Path
from setuptools import setup, find_packages


logger = logging.getLogger(__name__)


def read_lines(filename):
    return Path(filename).read_text().splitlines()


here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

with open(os.path.join(here, "wms", "version.py"), encoding="utf-8") as f:
    version = f.read()

version = version.split()[2].strip('"').strip("'")


setup(
    name="wms",
    version=version,
    description="Provides workflow automation services",
    long_description=readme,
    long_description_content_type="text/markdown",
    maintainer="Daniel Thom",
    maintainer_email="daniel.thom@nrel.gov",
    url="https://github.nrel.gov/dthom/wms",
    packages=find_packages(),
    package_dir={"wms": "wms"},
    entry_points={
        "console_scripts": [
            "wms=wms.cli.wms:cli",
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
    extras_require={
        "dev": ["black", "flake8", "pytest"],
    },
    install_requires=["click", "psutil", "prettytable", "s3path"],
)
