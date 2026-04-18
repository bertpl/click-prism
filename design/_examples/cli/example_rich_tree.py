"""Standalone Rich tree rendering of a Click CLI.

Demonstrates the DIY approach: using rich.tree.Tree to visualize
a Click command hierarchy without any dedicated plugin.
"""

import click
from rich.console import Console
from rich.tree import Tree

from example_cli import cli


def build_tree(group: click.Group, ctx: click.Context, tree: Tree | None = None) -> Tree:
    if tree is None:
        tree = Tree(f"[bold]{group.name}[/bold]")
    for name in group.list_commands(ctx):
        cmd = group.get_command(ctx, name)
        if cmd is None or cmd.hidden:
            continue
        help_text = cmd.get_short_help_str()
        if isinstance(cmd, click.Group):
            branch = tree.add(f"[bold cyan]{name}[/bold cyan] [dim]— {help_text}[/dim]")
            child_ctx = click.Context(cmd, info_name=name, parent=ctx)
            build_tree(cmd, child_ctx, branch)
        else:
            tree.add(f"{name} [dim]— {help_text}[/dim]")
    return tree


if __name__ == "__main__":
    ctx = click.Context(cli, info_name="projex")
    tree = build_tree(cli, ctx)
    Console().print(tree)
