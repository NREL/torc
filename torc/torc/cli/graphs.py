"""CLI commands for workflow graphs in the database"""

import logging
import sys
from pathlib import Path

import click
import matplotlib.pyplot as plt
import networkx as nx
from networkxgmml import XGMMLParserHelper

from .common import setup_cli_logging

logger = logging.getLogger(__name__)


@click.group()
@click.pass_context
def graphs(ctx):
    """Graph commands"""
    setup_cli_logging(ctx, __name__)


@click.command()
@click.argument("graph_file", callback=lambda *x: Path(x[2]))
@click.option(
    "-o",
    "--output-file",
    help="Output file. Defaults to stem of graph_file + .png. Will overwrite existing files.",
)
@click.option("-t", "--title", help="Title. Defaults to stem of graph_file.")
def plot(graph_file: Path, output_file, title):
    """Make a plot from an exported graph."""
    parser = XGMMLParserHelper()
    with open(graph_file, "rb") as f:
        parser.parseFile(f)

    if output_file is None:
        output_file = graph_file.stem + ".png"
    if title is None:
        title = graph_file.stem

    graph = parser.graph()
    labels = {k: v["label"] for k, v in graph.nodes().items()}
    fig = plt.Figure()
    nx.draw(
        graph,
        with_labels=True,
        font_weight="bold",
        labels=labels,
        ax=fig.add_subplot(title=title),
    )
    fig.savefig(output_file)
    print(f"Created {output_file}", file=sys.stderr)


graphs.add_command(plot)
