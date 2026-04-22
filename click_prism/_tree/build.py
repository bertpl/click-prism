"""Tree construction from a Click hierarchy.

`build_tree()` always produces the complete tree (all commands, full depth,
no filtering). Filtering lives in `filter.py` and is applied as a separate
post-build step. JSON call paths skip filtering entirely.

Traversal uses Click's `Group.list_commands(ctx)` and
`Group.get_command(ctx, name)` APIs throughout — never `group.commands`
directly. This supports lazy groups: subclasses that synthesise
commands on demand (plugin systems loading via entry points, large
CLIs that defer imports, generated subcommand sets) leave
`group.commands` empty and rely on the override pair to expose their
subcommands. Iterating `group.commands` would silently miss every
lazy-group subcommand.
"""

from __future__ import annotations

import click

from click_prism._tree.discover import (
    _build_aliases_index,
    _build_section_index,
    _get_default_cmd_name,
)
from click_prism._tree.node import TreeNode, _make_error_node
from click_prism._tree.params import _extract_params


def build_tree(group: click.Group, ctx: click.Context) -> TreeNode:
    """Build the complete tree for `group`. No filtering applied."""
    return _build_group(group, ctx, visited=frozenset([id(group)]))


def _build_group(group: click.Group, ctx: click.Context, *, visited: frozenset[int]) -> TreeNode:
    """Construct the TreeNode for `group`, recursing into children and attaching neighbour metadata.

    Args:
        group: The Click group to walk.
        ctx: The Click context for `group`; drives `info_name` and
            child-command resolution.
        visited: `id()`s of ancestor groups already on the path, used
            to detect circular references during recursion.

    Returns:
        A TreeNode representing `group` with children populated from
        `group.list_commands(ctx)`. Children carry neighbour-package
        metadata (aliases, default-cmd flag, section name).
    """
    node = TreeNode(
        name=ctx.info_name or group.name or "",
        help=group.get_short_help_str() or None,
        node_type="group",
        hidden=getattr(group, "hidden", False),
        deprecated=getattr(group, "deprecated", False),
        params=_extract_params(group),
    )

    aliases_index = _build_aliases_index(group)
    default_cmd_name = _get_default_cmd_name(group)
    section_by_cmd = _build_section_index(group)

    for cmd_name in group.list_commands(ctx):
        child = _build_child(group, ctx, cmd_name, visited)
        child.aliases = list(aliases_index.get(cmd_name, []))
        child.is_default = default_cmd_name == cmd_name
        child.section_name = section_by_cmd.get(cmd_name)
        node.children.append(child)
    return node


def _build_child(
    group: click.Group,
    ctx: click.Context,
    cmd_name: str,
    visited: frozenset[int],
) -> TreeNode:
    """Build the TreeNode for one child of `group`.

    Args:
        group: The parent Click group whose child we're loading.
        ctx: The Click context for `group`.
        cmd_name: Name of the child command to resolve via
            `group.get_command(ctx, cmd_name)`.
        visited: `id()`s of ancestor groups (passed through to
            `_build_group` for sub-groups).

    Returns:
        A TreeNode representing the child. Error nodes are returned
        for: load exceptions, `get_command` returning None, and
        circular references back to an ancestor group.
    """
    try:
        cmd = group.get_command(ctx, cmd_name)
    except Exception as exc:
        return _make_error_node(cmd_name, f"{type(exc).__name__}: {exc}")

    if cmd is None:
        return _make_error_node(cmd_name, "get_command returned None")

    if isinstance(cmd, click.Group):
        if id(cmd) in visited:
            return _make_error_node(cmd_name, "circular reference detected")
        child_ctx = click.Context(cmd, info_name=cmd_name, parent=ctx)
        return _build_group(cmd, child_ctx, visited=visited | {id(cmd)})

    return TreeNode(
        name=cmd_name,
        help=cmd.get_short_help_str() or None,
        node_type="command",
        hidden=cmd.hidden,
        deprecated=getattr(cmd, "deprecated", False),
        params=_extract_params(cmd),
    )
