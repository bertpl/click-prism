"""Theme type definitions — frozen dataclasses for visual styling.

Two orthogonal axes: per-column styles (color, dim) and per-row styles
(bold, italic, dim). A rendered cell composes one column style and one
row style — color from column only, bold/italic from row only,
dim = OR of both axes.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ColumnStyle:
    """Per-column visual style — color and dim, no bold/italic."""

    color: str | None = None
    dim: bool | None = None


@dataclass(frozen=True)
class RowStyle:
    """Per-row-type visual style — bold, italic, dim, no color."""

    bold: bool | None = None
    italic: bool | None = None
    dim: bool | None = None


@dataclass(frozen=True)
class ThemeColumns:
    """Per-column style buckets — guides, group/command names, description, arguments, options."""

    guides: ColumnStyle = field(default_factory=ColumnStyle)
    group_names: ColumnStyle = field(default_factory=ColumnStyle)
    command_names: ColumnStyle = field(default_factory=ColumnStyle)
    description: ColumnStyle = field(default_factory=ColumnStyle)
    arguments: ColumnStyle = field(default_factory=ColumnStyle)
    options: ColumnStyle = field(default_factory=ColumnStyle)


@dataclass(frozen=True)
class ThemeRows:
    """Per-row-type style buckets — title, groups, commands."""

    title: RowStyle = field(default_factory=RowStyle)
    groups: RowStyle = field(default_factory=RowStyle)
    commands: RowStyle = field(default_factory=RowStyle)


@dataclass(frozen=True)
class TreeTheme:
    """Complete tree theme — orthogonal column and row style axes."""

    columns: ThemeColumns = field(default_factory=ThemeColumns)
    rows: ThemeRows = field(default_factory=ThemeRows)
