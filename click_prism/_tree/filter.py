"""Post-build tree filtering: depth limit + hidden-command exclusion.

`filter_tree()` applies structural filtering to a complete tree built by
`build_tree()`. Returns a new tree if anything changed; otherwise returns
the input unchanged (input is never mutated either way). JSON call paths
skip this and pass the full tree directly to the renderer.
"""

from __future__ import annotations

import dataclasses

from click_prism._config import TreeConfig
from click_prism._tree.node import TreeNode


def filter_tree(tree: TreeNode, config: TreeConfig) -> TreeNode:
    """Apply structural filtering to a complete tree.

    Excludes hidden commands when `config.show_hidden` is False, and prunes
    children beyond `config.depth`.
    """
    return _filter_node(tree, depth=config.depth, show_hidden=bool(config.show_hidden))


def _filter_node(node: TreeNode, *, depth: int | None, show_hidden: bool) -> TreeNode:
    """Recursive helper for `filter_tree`: prune children below `depth` and drop hidden ones when `show_hidden=False`.

    Args:
        node: The TreeNode to filter (input is never mutated).
        depth: Maximum remaining depth to keep. None = unlimited;
            0 = drop all children; positive = keep that many levels.
        show_hidden: When False, hidden child nodes are dropped.

    Returns:
        A new TreeNode with filtered children if anything changed;
        otherwise the input `node` instance unchanged (copy-on-write).
    """
    if depth is not None and depth <= 0:
        return dataclasses.replace(node, children=[]) if node.children else node

    child_depth = (depth - 1) if depth is not None else None
    new_children: list[TreeNode] = []
    changed = False
    for child in node.children:
        if child.hidden and not show_hidden:
            changed = True
            continue
        filtered = _filter_node(child, depth=child_depth, show_hidden=show_hidden)
        if filtered is not child:
            changed = True
        new_children.append(filtered)

    return dataclasses.replace(node, children=new_children) if changed else node
