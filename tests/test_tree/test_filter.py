from __future__ import annotations

import click
import pytest
from click_prism._config import TreeConfig
from click_prism._tree.build import build_tree
from click_prism._tree.filter import filter_tree

from tests.test_tree._helpers import _ctx, _names


@pytest.mark.parametrize(
    ("show_hidden", "expected_names"),
    [
        (False, ["visible"]),  # hidden excluded by default
        (True, ["secret", "visible"]),  # hidden included when opted in
    ],
)
def test_filter_tree_hidden_exclusion(show_hidden: bool, expected_names: list[str]) -> None:
    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    @cli.command()
    def visible() -> None:
        pass

    @cli.command(hidden=True)
    def secret() -> None:
        pass

    tree = build_tree(cli, _ctx(cli))

    # --- act --------------------------
    filtered = filter_tree(tree, TreeConfig(show_hidden=show_hidden).resolve())

    # --- assert -----------------------
    assert sorted(_names(filtered)) == expected_names


def test_filter_tree_does_not_mutate_input() -> None:
    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    @cli.command(hidden=True)
    def secret() -> None:
        pass

    tree = build_tree(cli, _ctx(cli))

    # --- act --------------------------
    filter_tree(tree, TreeConfig(show_hidden=False).resolve())

    # --- assert -----------------------
    assert _names(tree) == ["secret"]  # original untouched


def test_filter_tree_returns_input_when_no_changes() -> None:
    """Copy-on-write: if nothing was filtered, return the same tree object."""

    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    @cli.command()
    def alpha() -> None:
        pass

    tree = build_tree(cli, _ctx(cli))

    # --- act --------------------------
    filtered = filter_tree(tree, TreeConfig(show_hidden=True).resolve())  # depth=None, show_hidden=True

    # --- assert -----------------------
    assert filtered is tree


def test_filter_tree_depth_zero_keeps_only_root() -> None:
    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    @cli.command()
    def alpha() -> None:
        pass

    tree = build_tree(cli, _ctx(cli))

    # --- act --------------------------
    filtered = filter_tree(tree, TreeConfig(depth=0).resolve())

    # --- assert -----------------------
    assert filtered.children == []


def test_filter_tree_depth_zero_returns_input_when_no_children() -> None:
    """Copy-on-write at the depth-zero short-circuit too."""

    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    tree = build_tree(cli, _ctx(cli))

    # --- act --------------------------
    filtered = filter_tree(tree, TreeConfig(depth=0).resolve())

    # --- assert -----------------------
    assert filtered is tree


def test_filter_tree_depth_one_keeps_immediate_children_only() -> None:
    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    @cli.group()
    def sub() -> None:
        pass

    @sub.command()
    def leaf() -> None:
        pass

    tree = build_tree(cli, _ctx(cli))

    # --- act --------------------------
    filtered = filter_tree(tree, TreeConfig(depth=1).resolve())

    # --- assert -----------------------
    assert _names(filtered) == ["sub"]
    assert filtered.children[0].children == []


def test_filter_tree_depth_none_means_unlimited() -> None:
    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    @cli.group()
    def a() -> None:
        pass

    @a.group()
    def b() -> None:
        pass

    @b.command()
    def leaf() -> None:
        pass

    tree = build_tree(cli, _ctx(cli))

    # --- act --------------------------
    filtered = filter_tree(tree, TreeConfig().resolve())  # depth defaults to None

    # --- assert -----------------------
    assert filtered.children[0].children[0].children[0].name == "leaf"
