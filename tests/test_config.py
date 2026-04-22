from __future__ import annotations

import pytest
from click_prism._config import UNLIMITED, TreeConfig
from click_prism._exceptions import PrismError
from click_prism._theme import DEFAULT_THEME, ColumnStyle, ThemeColumns, TreeTheme


# ==================================================================================================
#  resolve()
# ==================================================================================================
def test_resolve_fills_defaults() -> None:
    # --- arrange / act ----------------
    cfg = TreeConfig().resolve()
    # --- assert -----------------------
    assert cfg.charset in {"unicode", "ascii"}  # depends on test runner's stdout encoding
    assert cfg.depth is None
    assert cfg.show_hidden is False
    assert cfg.show_params is False
    assert cfg.tree_help == "root"
    assert cfg.theme is DEFAULT_THEME


def test_resolve_preserves_explicit_values() -> None:
    # --- arrange / act ----------------
    cfg = TreeConfig(
        charset="ascii",
        depth=3,
        show_hidden=True,
        show_params=True,
        tree_help="all",
    ).resolve()

    # --- assert -----------------------
    assert cfg.charset == "ascii"
    assert cfg.depth == 3
    assert cfg.show_hidden is True
    assert cfg.show_params is True
    assert cfg.tree_help == "all"


@pytest.mark.parametrize(
    ("input_depth", "expected_depth"),
    [
        (None, None),  # unset → no limit
        (UNLIMITED, None),  # UNLIMITED sentinel normalised to None
        (0, 0),  # zero preserved (= show only root)
        (3, 3),  # positive passes through
    ],
)
def test_resolve_depth_handling(input_depth: int | None, expected_depth: int | None) -> None:
    # --- arrange / act ----------------
    cfg = TreeConfig(depth=input_depth).resolve()
    # --- assert -----------------------
    assert cfg.depth == expected_depth


def test_resolve_rejects_negative_depth() -> None:
    # --- arrange / act / assert -------
    with pytest.raises(PrismError, match="Invalid depth"):
        TreeConfig(depth=-2).resolve()


def test_resolve_uses_supplied_theme() -> None:
    # --- arrange ----------------------
    custom = TreeTheme(columns=ThemeColumns(guides=ColumnStyle(color="red")))
    # --- act --------------------------
    cfg = TreeConfig(theme=custom).resolve()
    # --- assert -----------------------
    assert cfg.theme is custom


# ==================================================================================================
#  merge_onto()
# ==================================================================================================
def test_merge_onto_child_wins_over_parent() -> None:
    # --- arrange ----------------------
    parent = TreeConfig(charset="ascii", show_hidden=True, depth=3)
    child = TreeConfig(depth=1)

    # --- act --------------------------
    merged = child.merge_onto(parent)

    # --- assert -----------------------
    assert merged.charset == "ascii"  # inherited
    assert merged.show_hidden is True  # inherited
    assert merged.depth == 1  # child wins


def test_merge_onto_unlimited_wins_over_parent_numeric() -> None:
    # --- arrange ----------------------
    parent = TreeConfig(depth=2)
    child = TreeConfig(depth=UNLIMITED)
    # --- act / assert -----------------
    assert child.merge_onto(parent).depth == UNLIMITED


def test_merge_onto_none_is_transparent() -> None:
    # --- arrange ----------------------
    parent = TreeConfig(depth=2, charset="unicode")
    child = TreeConfig()  # all None
    # --- act / assert -----------------
    assert child.merge_onto(parent) == parent


def test_merge_onto_then_resolve_preserves_unlimited_intent() -> None:
    """The canonical merge-then-resolve order: UNLIMITED at child wins,
    then resolve() normalises it to None (= no limit).
    """
    # --- arrange ----------------------
    parent = TreeConfig(depth=2)
    child = TreeConfig(depth=UNLIMITED)

    # --- act --------------------------
    final = child.merge_onto(parent).resolve()

    # --- assert -----------------------
    assert final.depth is None


def test_resolve_then_merge_onto_corrupts_unlimited() -> None:
    """Demonstrates why merge-then-resolve order matters: if you resolve first,
    UNLIMITED becomes None and a parent's numeric depth wins.
    """
    # --- arrange ----------------------
    parent = TreeConfig(depth=2)
    child = TreeConfig(depth=UNLIMITED)

    # --- act --------------------------
    wrong = child.resolve().merge_onto(parent)

    # --- assert -----------------------
    assert wrong.depth == 2  # parent's value leaked through
