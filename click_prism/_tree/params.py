"""Parameter metadata — placeholder; real implementation pending.

`ParamInfo` is the CLI-parameter representation consumed by the tree model.
The shape is in place; `_extract_params()` is a stub until param extraction
lands.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import click


@dataclass
class ParamInfo:
    """Placeholder; real fields populated via `_extract_params()` once it ships."""

    name: str
    param_type: Literal["argument", "option"]
    declarations: list[str] = field(default_factory=list)
    type_name: str = ""
    required: bool = False
    is_flag: bool = False
    multiple: bool = False
    default: Any = None
    help: str | None = None
    choices: list[str] | None = None


def _extract_params(cmd: click.Command) -> list[ParamInfo]:
    """Return a `ParamInfo` for each parameter on `cmd` (currently a stub: always returns `[]`)."""
    return []
