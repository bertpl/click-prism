"""Built-in default theme + resolution.

Frozen so DEFAULT_THEME can be safely shared across resolved configs
without callers accidentally mutating the singleton.
"""

from __future__ import annotations

from typing import Final

from click_prism._theme.types import TreeTheme

DEFAULT_THEME: Final[TreeTheme] = TreeTheme()


def _resolve_theme(raw: TreeTheme | None) -> TreeTheme:
    """Return DEFAULT_THEME when `raw` is None, else `raw` unchanged (per-field default-fill not yet implemented)."""
    if raw is None:
        return DEFAULT_THEME
    return raw
