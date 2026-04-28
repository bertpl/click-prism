from __future__ import annotations

import click
from click_prism._tree.node import TreeNode


def _ctx(group: click.Group) -> click.Context:
    return click.Context(group, info_name=group.name)


def _names(node: TreeNode) -> list[str]:
    return [child.name for child in node.children]
