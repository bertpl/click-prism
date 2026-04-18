# 1.1.3. Related Packages

> Research date: 2026-04-05
>
> Download figures: pypistats.org rolling 30-day totals, retrieved 2026-04-05.

Click plugins and extensions that modify help formatting or provide custom Group
subclasses. Organized by adoption and how extensively they modify Click's internals.

## 1.1.3.1. Tier 1 — Widely used, modify help formatting or Group behavior

### 1.1.3.1.1. rich-click

| Field | Value |
|---|---|
| Package | `rich-click` |
| PyPI | https://pypi.org/project/rich-click/ |
| GitHub | https://github.com/ewels/rich-click |
| Author | Phil Ewels |
| License | MIT |
| Latest version | 1.9.7 (2026-01-31) |
| Python requires | >=3.8 |
| GitHub stars | ~798 |
| Monthly downloads | ~41M |

**What it does:** Drop-in replacement that renders Click help with `rich`. Colorized
panels, tables, 100+ themes. Can be used as `import rich_click as click` or via
`cls=RichGroup`.

**Custom classes:** [`RichCommand`](https://github.com/ewels/rich-click/blob/7f554a3f048917f17ea5089ae7332c46951136f0/src/rich_click/rich_command.py#L51) (`click.Command`),
[`RichGroup`](https://github.com/ewels/rich-click/blob/7f554a3f048917f17ea5089ae7332c46951136f0/src/rich_click/rich_command.py#L352) (`RichCommand, click.Group`),
[`RichCommandCollection`](https://github.com/ewels/rich-click/blob/7f554a3f048917f17ea5089ae7332c46951136f0/src/rich_click/rich_command.py#L577) (`click.CommandCollection, RichGroup`)

**Methods overridden on `RichCommand`:** `format_help()`, `format_options()`,
`format_help_text()`, `format_epilog()`, `get_help_option()`, `main()`

**Methods overridden on `RichGroup`:** `format_help()`, `format_commands()` (stub),
`get_command()`, `add_command()`, `command()`, `group()`

**Maintenance status:** Very active. 888 commits, 63 releases.

**Notable:** The most popular Click help extension. Replaces the entire help rendering
pipeline. `format_commands()` is stubbed out — the command list is rendered through a
different code path inside `format_help()`.

### 1.1.3.1.2. Cloup

| Field | Value |
|---|---|
| Package | `cloup` |
| PyPI | https://pypi.org/project/cloup/ |
| GitHub | https://github.com/janluke/cloup |
| Author | Gianluca Gippetto (janluke) |
| License | BSD-3-Clause |
| Latest version | 3.0.9 (2026-04-04) |
| Python requires | >=3.9 |
| GitHub stars | ~127 |
| Monthly downloads | ~898k |

**What it does:** Option groups, parameter constraints, subcommand sections, aliases,
help themes, "did you mean?" suggestions. Near-100% test coverage, strict `mypy`.

**Group subclasses:** `cloup.Group` (via [`SectionMixin, Command, click.Group`](https://github.com/janluke/cloup/blob/d53d04f51846e3dbfe6a1b97ad677bfc5cdda47f/cloup/_commands.py#L136)),
`cloup.Command` (via `ConstraintMixin, OptionGroupMixin, click.Command`),
custom `HelpFormatter`

**Methods overridden:** `SectionMixin` overrides `format_commands()` for named sections.
Custom `HelpFormatter` with `HelpTheme` and `Style` system. `command()`, `group()`
decorators overridden.

**Maintenance status:** Very active. 749 commits, 29 releases.

**Notable:** Foundation that `click-extra` builds on. Uses a custom `HelpFormatter`
subclass, not the plain `click.HelpFormatter`.

### 1.1.3.1.3. click-extra

| Field | Value |
|---|---|
| Package | `click-extra` |
| PyPI | https://pypi.org/project/click-extra/ |
| GitHub | https://github.com/kdeldycke/click-extra |
| Author | Kevin Deldycke |
| License | **GPL-2.0-or-later** |
| Latest version | 7.10.0 (2026-04-02) |
| Python requires | >=3.10 |
| GitHub stars | ~113 |
| Monthly downloads | ~70k |

**What it does:** "Ready-to-use wrapper around Click" built on `cloup`. Config file
loading (TOML/YAML/JSON/XML), colorized help, `--show-params`, `--color`/`--no-color`,
telemetry flags.

**Group subclasses:** `ExtraGroup` (inherits `cloup.Group` + mixins), `ExtraCommand`

**Methods overridden:** Inherits all `cloup` overrides plus adds colorization layers.

**Maintenance status:** Very active. 3,365 commits, 123 releases.

**Notable:** GPL-2.0 license. Built on `cloup`.

### 1.1.3.1.4. click-help-colors

| Field | Value |
|---|---|
| Package | `click-help-colors` |
| PyPI | https://pypi.org/project/click-help-colors/ |
| GitHub | https://github.com/click-contrib/click-help-colors |
| Author | r-m-n (click-contrib org) |
| License | MIT |
| Latest version | 0.9.4 |
| GitHub stars | ~91 |
| Monthly downloads | ~1.2M |

**What it does:** ANSI colorization of help headers, option names, and custom elements.

**Group subclasses:** `HelpColorsGroup`, `HelpColorsCommand`, `HelpColorsMultiCommand`,
`HelpColorsMixin`, `HelpColorsFormatter`

**Methods overridden:** `get_help()` (formatter swap), `write_usage()`, `write_heading()`,
`write_dl()` on formatter. `command()`, `group()` for color propagation. `resolve_command()`
on MultiCommand variant.

**Maintenance status:** Low activity. No new releases in 12+ months. Effectively
maintenance-mode.

**Notable:** Uses a mixin pattern (`HelpColorsMixin`). Hooks at `get_help()` and
the formatter level, not at `format_commands()`.

### 1.1.3.1.5. click-didyoumean

| Field | Value |
|---|---|
| Package | `click-didyoumean` |
| PyPI | https://pypi.org/project/click-didyoumean/ |
| GitHub | https://github.com/click-contrib/click-didyoumean |
| Author | Timo Furrer |
| License | MIT |
| Latest version | 0.3.1 (2024-03-24) |
| Python requires | >=3.6.2 |
| GitHub stars | ~100 |
| Monthly downloads | ~44M |

**What it does:** Git-like "did you mean...?" suggestions on mistyped subcommands.

**Group subclasses:** `DYMGroup`, `DYMCommandCollection`

**Methods overridden:** `resolve_command()` only — catches `UsageError` and enhances
with suggestions.

**Maintenance status:** Stable, low activity.

### 1.1.3.1.6. click-default-group

| Field | Value |
|---|---|
| Package | `click-default-group` |
| PyPI | https://pypi.org/project/click-default-group/ |
| GitHub | https://github.com/click-contrib/click-default-group |
| Author | Heungsub Lee |
| License | BSD-3-Clause (per repo LICENSE file; PyPI `license` field incorrectly says "Public Domain") |
| Latest version | 1.2.4 (2023-08-04) |
| Python requires | >=2.7 |
| GitHub stars | ~77 |
| Monthly downloads | ~7.9M |

**What it does:** Invoke a default subcommand when no subcommand is specified.

**Group subclasses:** `DefaultGroup`

**Methods overridden:** `parse_args()`, `get_command()`, `resolve_command()`,
`format_commands()` (wraps formatter to add `*` mark on default command),
`command()`. Sets `ignore_unknown_options = True`.

**Maintenance status:** Stable, low activity.

## 1.1.3.2. Tier 2 — Moderate adoption or narrower scope

### 1.1.3.2.1. click-aliases

| Field | Value |
|---|---|
| Package | `click-aliases` |
| PyPI | https://pypi.org/project/click-aliases/ |
| GitHub | https://github.com/click-contrib/click-aliases |
| Author | Robbin Bonthond |
| License | MIT |
| Latest version | 1.0.5 (2024-10-17) |
| GitHub stars | ~56 |
| Monthly downloads | ~2.1M |

**What it does:** Alias support for Click commands. Aliases shown in help as
`foo (bar,baz)`.

**Group subclasses:** `ClickAliasedGroup`

**Methods overridden:** `get_command()`, `format_commands()` (adds alias suffixes).

**Maintenance status:** Active. Latest release Oct 2024.

### 1.1.3.2.2. click-option-group

| Field | Value |
|---|---|
| Package | `click-option-group` |
| PyPI | https://pypi.org/project/click-option-group/ |
| GitHub | https://github.com/click-contrib/click-option-group |
| Author | Eugene Prilepin |
| License | BSD-3-Clause |
| Latest version | 0.5.9 (2025-10-09) |
| GitHub stars | ~119 |
| Monthly downloads | ~21M |

**What it does:** Option grouping (mutually exclusive, required groups, etc.).
Standalone predecessor to `cloup`'s option-group feature.

**Group subclasses:** None. Modifies Commands/Options, not Groups.

**Methods overridden:** `format_options()` on commands.

### 1.1.3.2.3. click-plugins

| Field | Value |
|---|---|
| Package | `click-plugins` |
| PyPI | https://pypi.org/project/click-plugins/ |
| GitHub | https://github.com/click-contrib/click-plugins |
| Author | Kevin Wurster, Sean Gillies |
| License | BSD |
| Latest version | 1.1.1.2 (2025-06-25) |
| GitHub stars | ~131 |
| Monthly downloads | ~50M |

**What it does:** Register CLI commands via setuptools entry points.
`@with_plugins()` decorator.

**Group subclasses:** None. Decorator pattern.

**Maintenance status:** Effectively discontinued upstream. Maintainers recommend vendoring.

**Notable:** Dependency of `click-command-tree`.

## 1.1.3.3. Tier 3 — Niche or inactive

### 1.1.3.3.1. click-rich-help

| Field | Value |
|---|---|
| Package | `click-rich-help` |
| PyPI | https://pypi.org/project/click-rich-help/ |
| GitHub | https://github.com/daylinmorgan/click-rich-help |
| Author | Daylin Morgan |
| License | MIT |
| Monthly downloads | ~2.2k |
| GitHub stars | ~7 |

**What it does:** Alternative to `rich-click`. `rich`-formatted help.

**Group subclasses:** `StyledGroup`, `StyledCommand`, `StyledMultiCommand`

**Maintenance status:** Inactive. Author acknowledges `rich-click` as the better alternative.

### 1.1.3.3.2. click-shell

| Field | Value |
|---|---|
| Package | `click-shell` |
| PyPI | https://pypi.org/project/click-shell/ |
| GitHub | https://github.com/clarkperkins/click-shell |
| Author | Clark Perkins |
| License | BSD |
| Monthly downloads | ~102k |
| GitHub stars | ~94 |

**What it does:** Interactive shell/REPL from a Click group.

**Group subclasses:** `Shell`

**Methods overridden:** `invoke()` only. Does not touch help formatting.

**Maintenance status:** Low activity. Historically broken with Click 8, fixed in v2.1 (2021-06).

### 1.1.3.3.3. click-repl

| Field | Value |
|---|---|
| Package | `click-repl` |
| PyPI | https://pypi.org/project/click-repl/ |
| GitHub | https://github.com/click-contrib/click-repl |
| License | MIT |
| Monthly downloads | ~41.9M |
| GitHub stars | ~237 |

**What it does:** REPL subcommand with tab-completion.

**Group subclasses:** None. Registers via `register_repl()`.

### 1.1.3.3.4. asyncclick

| Field | Value |
|---|---|
| Package | `asyncclick` |
| PyPI | https://pypi.org/project/asyncclick/ |
| GitHub | https://github.com/python-trio/asyncclick |
| License | BSD-3-Clause |
| Monthly downloads | ~1.35M |

**What it does:** Async-compatible fork of Click (trio/asyncio).

**Group subclasses:** Async mirrors of all Click classes.

## 1.1.3.4. Summary: Group subclass registry

Every known `click.Group` subclass in the ecosystem:

| Package | Class | Inherits from |
|---|---|---|
| `rich-click` | `RichGroup` | `RichCommand, click.Group` |
| `cloup` | `cloup.Group` | `SectionMixin, cloup.Command, click.Group` |
| `click-extra` | `ExtraGroup` | `cloup.Group` + mixins |
| `click-help-colors` | `HelpColorsGroup` | `HelpColorsMixin, click.Group` |
| `click-didyoumean` | `DYMGroup` | `click.Group` |
| `click-default-group` | `DefaultGroup` | `click.Group` |
| `click-aliases` | `ClickAliasedGroup` | `click.Group` |
| `click-shell` | `Shell` | `click.Group` |
| `click-rich-help` | `StyledGroup` | `click.Group` |

## 1.1.3.5. Summary: Method override matrix

Which `click.Group` methods each package overrides. The matrix
covers six of the nine subclasses from the registry above — the
subset whose override profiles contribute distinct data. The
other three are excluded by design:

- **`click-extra`** inherits its entire override profile from
  `cloup.Group` and adds colorization on top; its row would
  duplicate `cloup`'s.
- **`click-shell`** overrides `invoke()` only and does not touch
  help formatting or command resolution (see its entry above) —
  nothing to show in a help-override matrix.
- **`click-rich-help`** is Tier 3 and marked inactive by its own
  author ("acknowledges `rich-click` as the better alternative"),
  and no per-method detail was captured during research — not
  worth a dedicated row.

| Method | rich-click | cloup | click-help-colors | click-didyoumean | click-default-group | click-aliases |
|---|---|---|---|---|---|---|
| `format_help()` | **YES** | via formatter | via `get_help()` | - | - | - |
| `format_commands()` | **YES** (stub) | **YES** (sections) | - | - | **YES** (`*` mark) | **YES** (aliases) |
| `format_options()` | **YES** | **YES** | - | - | - | - |
| `get_help()` | - | - | **YES** | - | - | - |
| `get_command()` | **YES** | - | - | - | **YES** | **YES** |
| `list_commands()` | - | - | - | - | - | - |
| `resolve_command()` | - | - | **YES** | **YES** | **YES** | - |
| `parse_args()` | - | - | - | - | **YES** | - |
| `add_command()` | **YES** | - | - | - | - | - |
| `command()` / `group()` | **YES** | **YES** | **YES** | - | **YES** | - |

## 1.1.3.6. Summary: Architectural categories

The packages fall into three categories by how they modify Click:

1. **Help-pipeline replacers** (`rich-click`): Replace the entire help rendering pipeline.
   Override `format_help()` and stub out `format_commands()`.

2. **Help-pipeline enhancers** (`cloup`, `click-extra`, `click-help-colors`, `click-aliases`):
   Extend the existing formatter or override specific formatting methods. Stay within
   Click's formatting architecture.

3. **Behavior modifiers** (`click-didyoumean`, `click-default-group`): Override command
   resolution (`resolve_command()`, `get_command()`, `parse_args()`) but don't touch
   help formatting.
