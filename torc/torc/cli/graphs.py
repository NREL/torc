"""CLI commands for workflow graphs in the database"""

import logging
import sys
from pathlib import Path

import click

try:
    import graphviz
    import networkx as nx
    from networkxgmml import XGMMLParserHelper

    _has_plotting_libs = True
except ImportError:
    _has_plotting_libs = False

from .common import setup_cli_logging

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def graphs(ctx):
    """Graph commands"""
    setup_cli_logging(ctx, __name__)


@click.command()
@click.argument("graph_file", callback=lambda *x: Path(x[2]))
def plot(graph_file: Path):
    """Make a plot from an exported graph.

    \b
    Example:
    $ torc graphs plot export/job-blocks.xgmml
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
    gv.write(dot_file)
    print(f"Created {dot_file}", file=sys.stderr)
    png_file = graphviz.render("dot", "png", dot_file)
    print(f"Created dot file {dot_file} and image file {png_file}", file=sys.stderr)


graphs.add_command(plot)
