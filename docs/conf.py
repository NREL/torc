"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

-- Project information -----------------------------------------------------
https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""
# pylint: skip-file
# flake8: noqa
import sys

sys.path.append("../db_service/python_client")  # For swagger_client

import sphinx_rtd_theme

from swagger_client.api import default_api

import torc

project = "wms"
copyright = "2023, Daniel Thom"  # pylint: disable=redefined-builtin
author = "Daniel Thom"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.graphviz",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx_copybutton",
    "sphinx_click",
    "sphinxcontrib.openapi",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "titles_only": False,
    "navigation_depth": 2,
}
html_static_path = ["_static"]

todo_include_todos = True
autoclass_content = "both"
autodoc_member_order = "bysource"
todo_include_todos = True
