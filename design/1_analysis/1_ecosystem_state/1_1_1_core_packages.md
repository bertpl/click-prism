# 1.1.1. Core Packages

> Research date: 2026-04-05
>
> Download figures: pypistats.org rolling 30-day totals, retrieved 2026-04-05.

## 1.1.1.1. Click

| Field | Value |
|---|---|
| Package | `click` |
| PyPI | https://pypi.org/project/click/ |
| GitHub | https://github.com/pallets/click |
| Organization | Pallets |
| License | BSD-3-Clause |
| Latest version | 8.3.2 (2026-04-02) |
| Python requires | >=3.10 |
| Monthly downloads | ~708M |
| GitHub stars | ~17.4k |

### 1.1.1.1.1. Version history (8.x)

| Version | Date | Notable changes |
|---|---|---|
| 8.0.0 | 2021-05 | `Context.to_info_dict()`, `command_class`/`group_class` attributes |
| 8.1.x | 2022–2024 | Maintenance releases; still supports Python 3.7+ |
| 8.2.0 | 2025-05 | `MultiCommand` deprecated (merged into `Group`), `BaseCommand` deprecated (merged into `Command`), `OptionParser` deprecated. **Dropped Python 3.7–3.9.** |
| 8.3.0 | 2025-09 | Reworked `flag_value`/`default` relationship |
| 8.3.1 | 2025-11 | Bug fixes |
| 8.3.2 | 2026-04 | Bug fixes |

### 1.1.1.1.2. Key API surface

| Component | Status | Notes |
|---|---|---|
| `Group` | Active, primary class | Was merged with `MultiCommand` in 8.2 |
| `MultiCommand` | **Deprecated** in 8.2 | Alias only; will be removed in Click 9.0 |
| `Group.list_commands(ctx)` | Stable | Returns sorted list of subcommand names |
| `Group.get_command(ctx, name)` | Stable | Returns `Command` or `Group` instance |
| `Group.format_commands(ctx, formatter)` | Stable | Renders subcommand list in help output |
| `Command.format_help(ctx, formatter)` | Stable | Full help rendering pipeline |
| `Context` | Stable | `ctx.parent` for context-chain walking |
| `Context.to_info_dict()` | Stable (since 8.0) | Recursive CLI structure as dict |
| `group_class` attribute | Stable (since 8.0) | Default class for child groups |

### 1.1.1.1.3. Notes

- `MultiCommand` was deprecated in 8.2; `isinstance(cmd, click.Group)` is the correct check going forward
- `list_commands()` / `get_command()` API is stable across all 8.x versions
- Python >=3.10 since Click 8.2; Click 8.1.x users on 3.10+ are unaffected by this change

## 1.1.1.2. Rich

| Field | Value |
|---|---|
| Package | `rich` |
| PyPI | https://pypi.org/project/rich/ |
| GitHub | https://github.com/Textualize/rich |
| Author | Will McGugan / Textualize |
| License | MIT |
| Latest version | 14.3.3 (2026-02-19) |
| Python requires | >=3.8.0 |
| Monthly downloads | ~443M |
| GitHub stars | ~56k |

### 1.1.1.2.1. Version history (14.x)

| Version | Date | Notable changes |
|---|---|---|
| 14.0.0 | 2025-03 | `TTY_COMPATIBLE` env var; empty `NO_COLOR`/`FORCE_COLOR` treated as disabled |
| 14.1.0 | 2025-07 | Removed `typing_extensions` from runtime. Nested `Live` objects. |
| 14.2.0 | 2025-10 | Python 3.14 compatibility |
| 14.3.3 | 2026-02 | Bug fixes |

### 1.1.1.2.2. Key API surface

**`rich.tree.Tree`** — tree rendering:
```python
Tree(label, *, style="tree", guide_style="tree.line",
     expanded=True, highlight=False, hide_root=False)

Tree.add(label, *, style=None, guide_style=None,
         expanded=True, highlight=False) -> Tree  # returns child node
```

**`rich.console.Console`** — output and capture:
- `Console(color_system=..., theme=..., file=..., width=...)`
- `Console.print(*objects, ...)` — renders any `rich` renderable
- `Console.capture()` — context manager; `.get()` returns captured ANSI string

**Themes/styles:**
- `Theme` object at init, `push_theme()`/`pop_theme()`, `use_theme()` context manager
- Guide styles: `"tree.line"` (default thin), configurable per-node

### 1.1.1.2.3. Notes

The `rich.tree.Tree` API is stable across all 14.x versions, with no breaking changes.
