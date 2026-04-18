# 3.5. Composability

How `click-prism` coexists with the neighbor packages from section 1.1.4,
built on `wrapping()` (section 3.4.1) and cooperative `super()`.

## 3.5.1. Domain separation

`click-prism` owns help pages where tree-as-help is active; the
wrapped class owns everything else:

```python
# In PrismMixin.format_help() — see section 3.4.2:
if should_render_tree:
    # click-prism owns the entire page:
    # Click-standard Usage/Options + tree as Commands
    ...
else:
    super().format_help(ctx, formatter)
    # → RichGroup / cloup.Group / HelpColorsGroup / click.Group
```

Two renderers never share the same page.

## 3.5.2. Click's base help pipeline

Click 8.x routes `--help` through `get_help()` →
`format_help()`:

```
Command.format_help()          # inherited by Group, NOT overridden
  ├── self.format_usage()
  ├── self.format_help_text()
  ├── self.format_options()    # Group overrides this ↓
  │     ├── Command.format_options()     # renders Options section
  │     └── self.format_commands()       # renders Commands section
  └── self.format_epilog()
```

Key fact: `format_commands()` is called from *inside*
`Group.format_options()`, not from `format_help()`.

## 3.5.3. PrismMixin's override surface

`PrismMixin` overrides `format_help()` and `format_commands()`
(section 3.4.1). When tree-as-help is active, `format_help()` takes
over the page:

```
PrismMixin.format_help()
  ├── self.format_usage()
  ├── self.format_help_text()
  ├── click.Command.format_options(self, ...)   # explicit base call
  ├── self.format_commands()                    # PrismMixin → tree
  └── self.format_epilog()
```

The explicit `click.Command.format_options()` call bypasses two
problematic overrides:

- `click.Group.format_options()` — would call
  `self.format_commands()` internally, double-rendering.
- Wrapped-class overrides — may bundle command rendering into
  `format_options()` (e.g. `rich-click`), or never call
  `format_commands()`.

When tree-as-help is not active: `super().format_help()` →
wrapped class's full pipeline.

## 3.5.4. rich-click

`PrismGroup.wrapping(RichGroup)`

MRO: `TreeRichGroup → PrismMixin → RichGroup → RichCommand → click.Command`

- Root `--help` (tree-as-help active): `PrismMixin.format_help()`
  takes over the page. Usage/Options use Click's standard
  formatting (via explicit `click.Command.format_options()`),
  bypassing `rich-click`'s `format_options()` which bundles
  command rendering into its panel system and never calls
  `format_commands()`. `PrismMixin.format_commands()` renders the
  tree.
- Subgroup `--help` (tree-as-help not active):
  `super().format_help()` → `RichGroup.format_help()` → full
  `rich-click` panels.
- Recommended: "root only" mode (default). "All groups" bypasses
  `rich-click` entirely.

**Help-pipeline overrides (section 1.1.3):**

| Method | `RichGroup` | `RichCommand` |
|---|---|---|
| `format_help()` | YES | YES |
| `format_options()` | — | YES (renders options AND commands via panels) |
| `format_commands()` | YES (stub, no-op) | — |

**Tree-active trace:**

```
format_help() → PrismMixin  ✓  (first in MRO)
  format_usage()    → Command          (not overridden at Group level)
  format_help_text()→ RichCommand      (overridden; rich-styled description)
  EXPLICIT click.Command.format_options → options only  ✓
    bypasses RichCommand.format_options which bundles commands
  format_commands() → PrismMixin        → tree  ✓
  format_epilog()   → RichCommand      (overridden; rich-styled epilog)
```

`format_help_text()` and `format_epilog()` resolve to
`RichCommand`'s overrides via MRO, so the description and epilog
may carry `rich-click` styling. Usage and Options use Click's
standard rendering. This is an acceptable mix — domain separation
(section 3.5.1) requires that `click-prism` owns the Commands section,
not that it strips all other styling.

**Tree-inactive trace:**

```
format_help() → PrismMixin → super().format_help()
  → RichGroup.format_help()  ✓  (full rich-click pipeline)
```

**`tree_theme_from_rich_click()` utility**

For developers using `rich-click`'s `RichHelpConfiguration` to
style their CLI, a conversion helper maps its style fields to a
`TreeTheme`:

```python
# _config.py; exported from click_prism
def tree_theme_from_rich_click(config) -> TreeTheme: ...
```

`config` is duck-typed — `rich-click` is not imported at module
level. Fields are read via `getattr`; the overlapping subset is
mapped to the corresponding `TreeTheme` columns and rows. The
exact field mapping is determined at implementation (section 5.10).

```python
rc_cfg = RichHelpConfiguration(style_command="bold cyan", ...)

@click.group(
    cls=TreeRichGroup,
    tree_config=TreeConfig(theme=tree_theme_from_rich_click(rc_cfg)),
)
def cli(): ...
```

The developer opts in explicitly — nothing changes automatically
when `rich-click` is installed.

## 3.5.5. Cloup

`PrismGroup.wrapping(cloup.Group)`

MRO: `TreeCloupGroup → PrismMixin → cloup.Group → ... → click.Group`

Sections preserved in tree output. Traversal discovers section
metadata via duck-typed attribute access (section 3.2). Section headings
appear as structural labels in the tree (section 3.3.1).

**Help-pipeline overrides (section 1.1.3):**

| Method | `cloup.Group` |
|---|---|
| `format_help()` | — (uses custom formatter, no override) |
| `format_options()` | YES (option groups) |
| `format_commands()` | YES (sections) |

**Tree-active trace:**

```
format_help() → PrismMixin  ✓
  EXPLICIT click.Command.format_options → options only  ✓
    bypasses cloup's format_options (option groups not rendered)
  format_commands() → PrismMixin → tree  ✓
```

`cloup`'s option group formatting is bypassed on tree-as-help
pages — consistent with domain separation (section 3.5.1). Section
metadata is preserved in the tree via traversal (section 3.2), not via
`cloup.Group.format_commands()`.

**Tree-inactive trace:**

```
format_help() → PrismMixin → super().format_help()
  → cloup doesn't override format_help → Command.format_help()
  → self.format_options() → cloup.Group.format_options()  ✓
    → Command.format_options() + self.format_commands()
    → PrismMixin.format_commands() → inactive → super()
    → cloup.Group.format_commands()  ✓  (sectioned output)
```

Full cloup behavior preserved (option groups + command sections).

## 3.5.6. click-extra

Same as cloup — `ExtraGroup` inherits `cloup.Group`. Injected
flags (`--color`, `--config`) are added via `add_command()` /
`parse_args()`, not through the help pipeline. Same traces apply.

## 3.5.7. click-help-colors

`PrismGroup.wrapping(HelpColorsGroup)`

**Help-pipeline overrides (section 1.1.3):**

| Method | `HelpColorsGroup` |
|---|---|
| `get_help()` | YES (installs `HelpColorsFormatter`) |
| `format_help()` | — |
| `format_options()` | — |
| `format_commands()` | — |

Domain separation by extension point: `click-help-colors` hooks
at `get_help()` / formatter level; `click-prism` hooks at
`format_help()`.

**Tree-active trace:**

```
get_help() → HelpColorsGroup  ✓  (PrismMixin doesn't override get_help)
  creates HelpColorsFormatter, passes to format_help()
format_help() → PrismMixin  ✓
  EXPLICIT click.Command.format_options → options via HelpColorsFormatter  ✓
  format_commands() → PrismMixin → tree written via formatter.write()  ✓
```

`HelpColorsFormatter` is in place for the entire page. Options
are colorized through the formatter. The tree is a pre-formatted
string passed through `formatter.write()`.

**Tree-inactive trace:**

```
get_help() → HelpColorsGroup → creates HelpColorsFormatter
format_help() → PrismMixin → super().format_help()
  → Command.format_help() (HelpColorsGroup doesn't override)
  → Group.format_options() → format_commands()
  → PrismMixin.format_commands() → inactive → super()
  → Group.format_commands()  ✓  (colorized flat list)
```

Full colorization preserved via formatter.

## 3.5.8. click-didyoumean

`PrismGroup.wrapping(DYMGroup)`

Non-interference. `DYMGroup` overrides `resolve_command()` only
(section 1.1.3) — no help-pipeline overrides. Both tree-active and
tree-inactive paths are trivially correct.

## 3.5.9. click-default-group

`PrismGroup.wrapping(DefaultGroup)`

**Help-pipeline overrides (section 1.1.3):**

| Method | `DefaultGroup` |
|---|---|
| `format_commands()` | YES (`*` mark on default command) |

Default marker preserved: traversal detects `default_cmd_name`
(section 3.2), rendering shows `*` suffix. `DefaultGroup`'s
`parse_args()` / `resolve_command()` overrides work unchanged.

**Tree-active trace:**

```
format_help() → PrismMixin  ✓
  format_commands() → PrismMixin → tree  ✓
    DefaultGroup.format_commands() NOT reached
    (default marker via traversal: section 3.2 detects default_cmd_name)
```

**Tree-inactive trace:**

```
format_help() → PrismMixin → super().format_help()
  → Command.format_help() → Group.format_options()
  → format_commands() → PrismMixin → inactive → super()
  → DefaultGroup.format_commands()  ✓  (flat list with * mark)
```

## 3.5.10. click-aliases

`PrismGroup.wrapping(ClickAliasedGroup)`

**Help-pipeline overrides (section 1.1.3):**

| Method | `ClickAliasedGroup` |
|---|---|
| `format_commands()` | YES (alias suffixes) |

Aliases preserved: traversal discovers alias metadata (section 3.2),
rendering shows `config (cfg, conf)`. `ClickAliasedGroup`'s
`get_command()` resolves aliases — `PrismMixin` does not override
`get_command()`, so the wrapped class handles it directly.

**Tree-active trace:**

```
format_help() → PrismMixin  ✓
  format_commands() → PrismMixin → tree  ✓
    ClickAliasedGroup.format_commands() NOT reached
    (aliases via traversal: section 3.2 discovers alias metadata)
```

**Tree-inactive trace:**

```
format_help() → PrismMixin → super().format_help()
  → format_commands() → PrismMixin → inactive → super()
  → ClickAliasedGroup.format_commands()  ✓  (aliases in parens)
```

## 3.5.11. Multi-plugin stacking

Out of scope for the initial release. Manual subclassing works
as a documented workaround:

```python
class MyGroup(PrismMixin, DYMGroup, RichGroup):
    pass

MyGroup.group_class = MyGroup
```

`PrismMixin` must come first so it controls `format_help()`.
Most Click Group subclasses inherit directly from `click.Group`
— C3 linearization rarely causes conflicts. Not tested or
officially supported; a future release may add ergonomic
multi-class `wrapping()`.

## 3.5.12. Subcommand-only fallback

`tree_command()` works with any Group — no wrapping needed:

```python
@click.group(cls=RichGroup)
def cli(): ...

cli.add_command(tree_command())
```

No tree-as-help, no `--help-json`. Just the tree subcommand.
Universal escape hatch when wrapping isn't feasible.

## 3.5.13. Summary

| Package | Tree-active | Tree-inactive | Notes |
|---|---|---|---|
| `rich-click` | ✓ | ✓ | Requires `click.Command.format_options` bypass |
| `cloup` | ✓ | ✓ | Option groups bypassed on tree pages (domain separation) |
| `click-extra` | ✓ | ✓ | Same as `cloup` |
| `click-help-colors` | ✓ | ✓ | Formatter colorization applies to both paths |
| `click-didyoumean` | ✓ | ✓ | No help-pipeline overrides |
| `click-default-group` | ✓ | ✓ | Default marker via traversal, not `format_commands` |
| `click-aliases` | ✓ | ✓ | Aliases via traversal, not `format_commands` |
