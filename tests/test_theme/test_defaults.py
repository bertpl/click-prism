from __future__ import annotations

from click_prism._theme import (
    DEFAULT_THEME,
    ColumnStyle,
    RowStyle,
    ThemeColumns,
    ThemeRows,
    TreeTheme,
    _resolve_theme,
)


def test_resolve_theme_returns_default_when_unset() -> None:
    # --- arrange / act / assert -------
    assert _resolve_theme(None) is DEFAULT_THEME


def test_resolve_theme_returns_input_when_set() -> None:
    # --- arrange ----------------------
    custom = TreeTheme()
    # --- act / assert -----------------
    assert _resolve_theme(custom) is custom


def test_default_theme_has_full_structure() -> None:
    # --- arrange / act / assert -------
    assert isinstance(DEFAULT_THEME.columns, ThemeColumns)
    assert isinstance(DEFAULT_THEME.rows, ThemeRows)
    assert isinstance(DEFAULT_THEME.columns.guides, ColumnStyle)
    assert isinstance(DEFAULT_THEME.rows.title, RowStyle)
