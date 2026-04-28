"""Visual styling subpackage — types, defaults, builtin catalog, adapters."""

from click_prism._theme.defaults import DEFAULT_THEME, _resolve_theme
from click_prism._theme.types import (
    ColumnStyle,
    RowStyle,
    ThemeColumns,
    ThemeRows,
    TreeTheme,
)

__all__ = [
    "DEFAULT_THEME",
    "ColumnStyle",
    "RowStyle",
    "ThemeColumns",
    "ThemeRows",
    "TreeTheme",
    "_resolve_theme",
]
