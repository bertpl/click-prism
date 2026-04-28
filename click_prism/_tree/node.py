"""TreeNode dataclass + error-node helper."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from click_prism._tree.params import ParamInfo


@dataclass
class TreeNode:
    """A node in the rendered tree — group, command, or error."""

    name: str
    help: str | None
    node_type: Literal["group", "command", "error"]
    hidden: bool = False
    deprecated: bool = False
    params: list[ParamInfo] = field(default_factory=list)
    children: list[TreeNode] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    section_name: str | None = None
    is_default: bool = False
    error_message: str | None = None


def _make_error_node(name: str, message: str) -> TreeNode:
    """Construct an error TreeNode (`node_type="error"`) carrying a load-failure message."""
    return TreeNode(name=name, help=None, node_type="error", error_message=message)
