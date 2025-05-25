"""
Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

-- Project information -----------------------------------------------------
https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
"""


project = "torc"
copyright = "2025, NREL"
author = "NREL"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.githubpages",
    "sphinx.ext.graphviz",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx_copybutton",
    "sphinx_click",
    "sphinxcontrib.openapi",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_tabs.tabs",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix = {
    ".md": "markdown",
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_title = "Torc Documentation"
html_theme_options = {
    "navigation_with_keys": True,
}
html_static_path = ["_static"]

todo_include_todos = True
autoclass_content = "both"
autodoc_member_order = "bysource"
todo_include_todos = True
copybutton_only_copy_prompt_lines = True
copybutton_exclude = ".linenos, .gp, .go"
copybutton_line_continuation_character = "\\"
copybutton_here_doc_delimiter = "EOT"
copybutton_prompt_text = "$"
copybutton_copy_empty_lines = False
