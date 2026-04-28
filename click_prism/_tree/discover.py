"""Neighbour-package metadata discovery — duck-typed, no neighbour imports.

Probes Click groups for metadata added by sibling packages (click-aliases,
click-default-group, cloup) via `getattr` only. Absent attributes degrade
gracefully to "no metadata" defaults.
"""

from __future__ import annotations

import click


def _build_aliases_index(group: click.Group) -> dict[str, list[str]]:
    """Map `cmd_name -> aliases` for click-aliases-style groups; empty otherwise."""
    aliases_attr = getattr(group, "_aliases", None)
    return aliases_attr if isinstance(aliases_attr, dict) else {}


def _get_default_cmd_name(group: click.Group) -> str | None:
    """Return click-default-group's `default_cmd_name` attribute if set."""
    return getattr(group, "default_cmd_name", None)


def _build_section_index(group: click.Group) -> dict[str, str | None]:
    """Pre-compute a `cmd_name -> section title` map for cloup-style groups.

    Walking sections once per group is O(N+S); doing it per child would
    be O(N*S).

    Args:
        group: The Click group to probe for cloup `sections` metadata.

    Returns:
        Map of command name to its section title (or None if the
        section has no title). Empty dict if `group` has no `sections`
        attribute or it isn't iterable as expected.
    """
    sections = getattr(group, "sections", None) or []
    index: dict[str, str | None] = {}
    for section in sections:
        commands = getattr(section, "commands", None)
        if isinstance(commands, dict):
            title = getattr(section, "title", None)
            for name in commands:
                index[name] = title
    return index
