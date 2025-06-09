"""CLI commands for workflow graphs in the database"""

import sys
from pathlib import Path

import rich_click as click
from loguru import logger

try:
    import graphviz
    import networkx as nx
    from networkxgmml import XGMMLParserHelper

    _has_plotting_libs = True
except ImportError:
    _has_plotting_libs = False

from .common import get_workflow_key_from_context, setup_cli_logging


GRAPH_NAMES = ["job_job_dependencies", "job_file_dependencies", "job_user_data_dependencies"]


@click.group()
@click.pass_context
def graphs(ctx):
    """Graph commands"""
    setup_cli_logging(ctx, __name__)


@click.command()
@click.argument(
    "names",
    type=click.Choice(GRAPH_NAMES),
    nargs=-1,
)
@click.option(
    "-k",
    "--keep-dot-file",
    default=False,
    show_default=True,
    is_flag=True,
    help="Keep the intermediate DOT file",
)
@click.option(
    "-o",
    "--output",
    default="output",
    show_default=True,
    help="Output directory",
    callback=lambda *x: Path(x[2]),
)
@click.pass_obj
@click.pass_context
def plot(ctx, api, names, keep_dot_file, output):
    """Make a plot from an exported graph.

    \b
    Example:
    $ torc graphs plot job_job_dependencies
    """
    if not names:
        logger.warning("No graph names were passed")
    output.mkdir(exist_ok=True)
    workflow_key = get_workflow_key_from_context(ctx, api)
    for name in names:
        response = api.get_dot_graph(workflow_key, name)
        filename = name + ".dot"
        dot_file = output / filename
        dot_file.write_text(response.graph, encoding="utf-8")
        try:
            png_file = graphviz.render("dot", "png", dot_file)
            logger.info("Created graph image file {}", png_file)
        finally:
            if keep_dot_file:
                logger.info("Created {}", dot_file)
            else:
                dot_file.unlink(dot_file)


@click.command()
@click.argument("graph_file", callback=lambda *x: Path(x[2]))
@click.option(
    "-k",
    "--keep-dot-file",
    default=False,
    show_default=True,
    is_flag=True,
    help="Keep the intermediate DOT file",
)
def plot_xgmml(graph_file: Path, keep_dot_file):
    """Make a plot from an XGMML graph file exported with arangoexport.

    \b
    Example:
    $ torc graphs plot-xgmml export/job-blocks.xgmml
    """
    if not _has_plotting_libs:
        print(
            """The required plotting libraries are not installed. Please run

$ pip install -e '<path-to-torc>[plots]'

On some systems pip cannot install pygraphviz. If you get an error for
it then use conda manually:

$ conda install pygraphviz

Then rerun the pip command.
""",
            file=sys.stderr,
        )
        sys.exit(1)
    parser = XGMMLParserHelper()
    with open(graph_file, "rb") as f:
        parser.parseFile(f)

    graph = parser.graph()
    gv = nx.nx_agraph.to_agraph(graph)
    dot_file = Path(graph_file).with_suffix(".dot")
    try:
        gv.write(dot_file)
        png_file = graphviz.render("dot", "png", dot_file)
        logger.info("Created image file {}", png_file)
    finally:
        if keep_dot_file:
            logger.info("Created {}", dot_file)
        else:
            dot_file.unlink()


graphs.add_command(plot)
graphs.add_command(plot_xgmml)
