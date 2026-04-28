from __future__ import annotations

import click
from click_prism._tree.build import build_tree

from tests.test_tree._helpers import _ctx, _names


# ==================================================================================================
#  build_tree: basic shapes
# ==================================================================================================
def test_build_tree_flat_group() -> None:
    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    @cli.command()
    def alpha() -> None:
        """Alpha cmd."""

    @cli.command()
    def beta() -> None:
        """Beta cmd."""

    # --- act --------------------------
    tree = build_tree(cli, _ctx(cli))

    # --- assert -----------------------
    assert tree.node_type == "group"
    assert tree.name == "cli"
    assert _names(tree) == ["alpha", "beta"]
    assert all(child.node_type == "command" for child in tree.children)
    assert tree.children[0].help == "Alpha cmd."


def test_build_tree_nested_group() -> None:
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

    # --- act --------------------------
    tree = build_tree(cli, _ctx(cli))

    # --- assert -----------------------
    assert _names(tree) == ["sub"]
    sub_node = tree.children[0]
    assert sub_node.node_type == "group"
    assert _names(sub_node) == ["leaf"]


def test_build_tree_empty_group() -> None:
    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    # --- act / assert -----------------
    assert build_tree(cli, _ctx(cli)).children == []


def test_build_tree_includes_hidden_and_deprecated() -> None:
    """build_tree() never filters; hidden/deprecated commands appear in the
    raw model and are filtered later by filter_tree().
    """

    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    @cli.command(hidden=True)
    def secret() -> None:
        pass

    @cli.command(deprecated=True)
    def old() -> None:
        pass

    # --- act --------------------------
    tree = build_tree(cli, _ctx(cli))

    # --- assert -----------------------
    by_name = {c.name: c for c in tree.children}
    assert by_name["secret"].hidden is True
    assert by_name["old"].deprecated is True


def test_build_tree_uses_info_name_when_supplied() -> None:
    # --- arrange ----------------------
    @click.group()
    def cli() -> None:
        pass

    ctx = click.Context(cli, info_name="renamed")

    # --- act / assert -----------------
    assert build_tree(cli, ctx).name == "renamed"


def test_build_tree_falls_back_to_empty_string_when_no_name() -> None:
    """Both info_name and group.name unset → empty string root label."""
    # --- arrange ----------------------
    group = click.Group(name=None)
    ctx = click.Context(group, info_name=None)
    # --- act / assert -----------------
    assert build_tree(group, ctx).name == ""


# ==================================================================================================
#  build_tree: error nodes
# ==================================================================================================
def test_build_tree_error_when_get_command_raises() -> None:
    # --- arrange ----------------------
    class _BoomGroup(click.Group):
        def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
            raise RuntimeError("kaboom")

    cli = _BoomGroup(name="cli")
    cli.list_commands = lambda ctx: ["broken"]  # type: ignore[assignment]

    # --- act --------------------------
    tree = build_tree(cli, _ctx(cli))

    # --- assert -----------------------
    assert len(tree.children) == 1
    err = tree.children[0]
    assert err.node_type == "error"
    assert err.name == "broken"
    assert "RuntimeError" in (err.error_message or "")
    assert "kaboom" in (err.error_message or "")


def test_build_tree_error_when_get_command_returns_none() -> None:
    # --- arrange ----------------------
    class _NoneGroup(click.Group):
        def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
            return None

    cli = _NoneGroup(name="cli")
    cli.list_commands = lambda ctx: ["ghost"]  # type: ignore[assignment]

    # --- act --------------------------
    tree = build_tree(cli, _ctx(cli))

    # --- assert -----------------------
    err = tree.children[0]
    assert err.node_type == "error"
    assert err.error_message == "get_command returned None"


def test_build_tree_error_on_circular_reference() -> None:
    """A child group that refers back to itself produces an error node, not
    infinite recursion.
    """
    # --- arrange ----------------------
    cli = click.Group(name="cli")
    sub = click.Group(name="sub")
    cli.add_command(sub)
    # Make sub list itself, then resolve back to itself → circular reference.
    sub.add_command(sub, name="loop")

    # --- act --------------------------
    tree = build_tree(cli, _ctx(cli))

    # --- assert -----------------------
    sub_node = tree.children[0]
    loop_node = sub_node.children[0]
    assert loop_node.node_type == "error"
    assert loop_node.error_message == "circular reference detected"


# ==================================================================================================
#  build_tree: lazy groups
# ==================================================================================================
def test_build_tree_supports_lazy_groups() -> None:
    """A group that synthesises commands on-demand via list_commands /
    get_command (no static `commands` dict) traverses correctly.
    """
    # --- arrange ----------------------
    real = click.Command(name="dynamic", help="Synthesised on demand.")

    class LazyGroup(click.Group):
        def list_commands(self, ctx: click.Context) -> list[str]:
            return ["dynamic"]

        def get_command(self, ctx: click.Context, name: str) -> click.Command | None:
            return real if name == "dynamic" else None

    cli = LazyGroup(name="cli")

    # --- act --------------------------
    tree = build_tree(cli, _ctx(cli))

    # --- assert -----------------------
    assert _names(tree) == ["dynamic"]
    assert tree.children[0].help == "Synthesised on demand."


# ==================================================================================================
#  build_tree: neighbour metadata propagation
# ==================================================================================================
def test_build_tree_propagates_aliases_from_click_aliases_shape() -> None:
    # --- arrange ----------------------
    cli = click.Group(name="cli")
    cli.add_command(click.Command(name="alpha"))
    cli.add_command(click.Command(name="beta"))
    cli._aliases = {"alpha": ["a", "al"]}  # type: ignore[attr-defined]

    # --- act --------------------------
    by_name = {c.name: c for c in build_tree(cli, _ctx(cli)).children}

    # --- assert -----------------------
    assert by_name["alpha"].aliases == ["a", "al"]
    assert by_name["beta"].aliases == []


def test_build_tree_handles_plain_group_without_aliases_attribute() -> None:
    # --- arrange ----------------------
    cli = click.Group(name="cli")
    cli.add_command(click.Command(name="alpha"))
    # --- act / assert -----------------
    assert build_tree(cli, _ctx(cli)).children[0].aliases == []


def test_build_tree_marks_default_command() -> None:
    # --- arrange ----------------------
    cli = click.Group(name="cli")
    cli.add_command(click.Command(name="alpha"))
    cli.add_command(click.Command(name="beta"))
    cli.default_cmd_name = "alpha"  # type: ignore[attr-defined]

    # --- act --------------------------
    by_name = {c.name: c for c in build_tree(cli, _ctx(cli)).children}

    # --- assert -----------------------
    assert by_name["alpha"].is_default is True
    assert by_name["beta"].is_default is False


def test_build_tree_propagates_section_from_cloup_shape() -> None:
    # --- arrange ----------------------
    class _Section:
        def __init__(self, title: str, commands: dict[str, click.Command]) -> None:
            self.title = title
            self.commands = commands

    cli = click.Group(name="cli")
    cli.add_command(click.Command(name="alpha"))
    cli.add_command(click.Command(name="beta"))
    cli.add_command(click.Command(name="gamma"))  # not in any section
    cli.sections = [  # type: ignore[attr-defined]
        _Section("Common", {"alpha": cli.commands["alpha"]}),
        _Section("Advanced", {"beta": cli.commands["beta"]}),
    ]

    # --- act --------------------------
    by_name = {c.name: c for c in build_tree(cli, _ctx(cli)).children}

    # --- assert -----------------------
    assert by_name["alpha"].section_name == "Common"
    assert by_name["beta"].section_name == "Advanced"
    assert by_name["gamma"].section_name is None


def test_build_tree_section_index_skips_non_dict_commands_attribute() -> None:
    """Defensive: section objects whose `.commands` isn't a dict are ignored
    (we use `in` and `[]` on it, so a non-dict would crash without this guard).
    """

    # --- arrange ----------------------
    class _WeirdSection:
        def __init__(self) -> None:
            self.title = "Whatever"
            self.commands = ["alpha"]  # not a dict

    cli = click.Group(name="cli")
    cli.add_command(click.Command(name="alpha"))
    cli.sections = [_WeirdSection()]  # type: ignore[attr-defined]

    # --- act / assert -----------------
    assert build_tree(cli, _ctx(cli)).children[0].section_name is None
