# 2.3.4. UX: Requirements

Consolidated requirements derived from the scenarios in sections 2.3.1–2.3.3.
Each requirement traces to one or more scenarios. Numbered for
reference in later design sections.

## 2.3.4.0. Setting exposure overview

Who controls each setting — the developer (at definition time via
`TreeConfig` or function arguments) or the end user (at runtime via
CLI flags on the tree subcommand).

| Setting | Developer | End user | Notes |
|---|---|---|---|
| `charset` (unicode/ascii) | `TreeConfig(charset=...)` | — | R7 — auto-detected from terminal capabilities when unset (section 2.2.2.1); developer overrides the default |
| `depth` | `TreeConfig(depth=...)` | `--depth` on tree subcommand | R15, R23 — runtime overrides developer default |
| `show_hidden` | `TreeConfig(show_hidden=...)` | — | R9 — developer-configurable only |
| Deprecated display | *(always shown)* | — | R10 — not configurable; deprecated commands are always included with a visual marker |
| `show_params` | `TreeConfig(show_params=...)` | — | R25 — developer-configured, not an end-user toggle |
| `tree_help` | `TreeConfig(tree_help=...)` | — | R17–R21 — developer-controlled |
| `theme` | `TreeConfig(theme=...)` | — | R30 — developer customization |
| Tree subcommand name | `tree_command(name=...)` | — | R13 |
| `--help-json` | Auto-added by `PrismGroup` | Available as CLI flag | R2 — always present on root when using `PrismGroup` |

`--depth` is the only setting with end-user runtime override.
All other tree behavior is determined by the developer at
definition time. This is deliberate: tree output is a curated
view of the CLI's structure, and the developer controls the
curation (R21).

**JSON is always complete.** `--help-json` and
`render_tree(format="json")` include all commands (hidden,
deprecated), all parameters, and full depth regardless of these
settings (R2). The visual tree is the developer's curated view
for humans; the JSON output is the unfiltered machine-readable
surface for tooling and agents. This separation is architectural:
JSON call paths skip `filter_tree()` entirely (section 3.2.5).

## 2.3.4.1. Integration

**R1. Group subclass path.** A single `cls=PrismGroup` on the root
group adds tree-as-help and `--help-json` to the CLI without any
other code changes. No tree subcommand is created automatically.
*(section 2.3.1.1)*

**R2. `--help-json` option.** Eager option on the root group, added
automatically by `PrismGroup`. Outputs the complete CLI hierarchy as
structured JSON and exits — no help or tree visualization is shown.
Root-only. Ignores depth limits and configuration filters. Includes
all commands (including hidden and deprecated) and all parameters.
*(section 2.3.1.5)*

**R3. Tree subcommand (opt-in).** `add_command(tree_command())`
explicitly adds a tree subcommand with runtime controls (`--depth`).
Works with or without `PrismGroup`. *(section 2.3.1.1)*

**R4. Standalone functions.** `show_tree(cli)` prints the tree
to stdout; `render_tree(cli)` returns it as a string. Neither
modifies the CLI or requires a Click context. Both include
hidden commands by default. Both support `format="json"` for
machine-readable output following the same rules as `--help-json`
(R2). *(sections 2.3.1.1, 2.3.1.5)*

**R5. Child group inheritance.** Child groups created via
`@cli.group()` automatically inherit tree behavior from a
tree-enabled parent. *(section 2.3.1.1)*

## 2.3.4.2. Tree output

**R6. Hierarchy display.** Tree output shows the full command
hierarchy with box-drawing characters and aligned help text.
*(section 2.3.1.1)*

**R7. Output styles.** At minimum, unicode (with rounded arc
corners) and ASCII styles. Unicode is the default. *(section 2.3.1.3)*

**R8. True columnar layout.** Descriptions start at a fixed column
position determined by the widest tree+name entry. Nested commands
use a 1-character indent within the description column. *(sections 2.3.1.1,
2.3.1.3)*

**R9. Hidden commands.** Excluded by default (matching Click's
`--help`). Developer-configurable to include them, with a visual
marker. *(section 2.3.1.3)*

**R10. Deprecated commands.** Always shown (matching Click), with a
visual marker. *(section 2.3.1.3)*

**R11. Error nodes.** Commands that fail to load are shown with an
error indicator and diagnostic message, not silently dropped or
crashed on. *(section 2.3.1.6)*

**R12. Terminal width.** Tree output respects the terminal's
available width. *(section 2.3.2.2)*

## 2.3.4.3. Tree subcommand (opt-in)

**R13. Default name.** `tree`. Developer-configurable to a different
name via `tree_command(name=...)`. *(section 2.3.1.3)*

**R14. Name collision.** If the tree command name conflicts with an
existing command, `click-prism` raises a clear error at definition
time. *(sections 2.3.1.3, 2.3.1.6)*

**R15. `--depth` flag.** End user can limit tree depth at runtime.
Overrides developer-configured depth. *(section 2.3.1.2)*

**R16. Subtree scoping.** A tree subcommand added to a child group
shows only that group's subtree. The subtree root shows the full
command path (`ctx.command_path`, e.g. `projex deploy`) so the
user can identify where the subtree sits in the hierarchy.
*(section 2.3.1.6)*

## 2.3.4.4. Tree-as-help

**R17. Three modes.** `"root"` (default — root group only), `"all"`
(every group), or `"none"` (disabled). *(section 2.3.1.4)*

**R18. Root only.** Tree replaces the command list in the root
group's `--help`. Subgroups keep standard Click help. *(section 2.3.1.4)*

**R19. All groups.** Every group's `--help` shows a tree from that
point down. *(section 2.3.1.4)*

**R20. Coexistence.** When `tree_command()` is added alongside
`PrismGroup`, tree-as-help and the tree subcommand coexist. The
subcommand provides runtime control (`--depth`); tree-as-help uses
the developer's configured settings. *(section 2.3.1.4)*

**R21. Developer-controlled.** Tree-as-help output is determined by
the developer's configuration, not by end-user flags. *(section 2.3.1.4)*

## 2.3.4.5. Configuration

**R22. Per-group configuration.** Each group can have its own tree
settings. Child settings override parent settings for fields that
are explicitly set. *(section 2.3.1.3)*

**R23. Runtime override.** End-user `--depth` flag on the tree
subcommand (when added) overrides developer-configured depth.
*(section 2.3.1.2)*

**R24. Zero-config default.** Everything works with sensible
defaults. No configuration is required for the common case.
*(section 2.2.1)*

**R25. Parameter display.** Developer-configurable 4-column mode
showing Arguments and Options columns alongside the tree and
description. Arguments in uppercase, options as long-form option
name (`--env`, not `-e/--env`; short form when no long form
exists; boolean flag pairs as `--[no-]flag`). Column positions
anchored to a header row. Developer-configured, not an end-user
toggle. *(section 2.3.1.3)*

## 2.3.4.6. Rich integration

**R26. Auto-detection.** `rich` styling is enabled automatically when
`rich` is installed. No code changes required. *(section 2.3.2.1)*

**R27. Graceful absence.** When `rich` is not installed, output is
plain Unicode text. No errors, no warnings. *(section 2.3.2.1)*

**R28. Terminal adaptation.** `rich` output adapts to the terminal's
capabilities: color system, width, and TTY detection. `NO_COLOR`
handling is delegated entirely to `rich`'s Console (colors stripped,
bold/dim/italic preserved — `click-prism` does not inspect `NO_COLOR`
itself). *(section 2.3.2.2)*

**R29. Bold group rows.** When `rich` is available, group rows are
rendered bold across all columns, creating visual section headers
that communicate hierarchy through weight. *(section 2.3.2.1)*

**R30. Theme customization.** Theming uses two orthogonal axes: a
vertical axis (color and dim per column — *guides, group names,
command names, description, arguments, options*) and a horizontal
axis (bold, italic, dim per row type — *title, group, command*).
These italicized names are English category labels; the concrete
Python field names are pinned down in section 3.1.3. A cell's style is the
composition of both; dim merges as OR. Color is vertical only. The
API makes the column-vs-row split explicit: each axis exposes only
the modifiers it owns, and the type system prevents invalid
combinations (e.g., setting color on a row) at definition time
rather than through runtime validation. Ease of use comes from
opt-in overrides: the developer only specifies fields where they
want to deviate from the default theme. Group and command names
are separate vertical entries so the developer can assign
different colors for terminals without bold support. `click-prism`
ships with a named-ANSI default theme and a catalog of additional
built-in themes. Developers can also define custom themes. The
built-in theme catalog — names and color values — is defined in
phase 8 (section 5.9). *(section 2.3.2.3)*

**R31. Theme portability.** Theme settings are silently ignored when
`rich` is not installed. The same configuration works in both
environments without conditional code. *(section 2.3.2.3)*

## 2.3.4.7. Plugin composability

**R32. Combinable with any Group subclass.** `click-prism` is
combinable with the Group subclasses from `rich-click`, `cloup`,
`click-extra`, `click-help-colors`, `click-didyoumean`,
`click-default-group`, and `click-aliases`. The ergonomic API
for the single-subclass combination case is the public
`PrismGroup.wrapping(OtherGroup)` classmethod factory. *(sections 2.3.3.2–2.3.3.8)*

**R33. Non-interference.** `click-prism` does not break the behavior
of any combined package. Non-tree help pages, command resolution,
and other features work as if `click-prism` were not present.
*(section 2.3.3.1)*

**R34. Domain separation.** `click-prism` owns tree output; other
packages own their respective domains (help formatting, command
resolution, typo suggestions, etc.). When tree-as-help is active on
a group, `click-prism` handles that group's `--help` entirely and
delegates other groups to the wrapped class — the two renderers
never share the same page. *(sections 2.3.3.2, 2.3.3.5, 2.3.3.6)*

**R35. Information preservation.** Information from combined
packages — section groupings (`cloup`), default command markers
(`*`), aliases in parentheses — is preserved in tree output.
*(sections 2.3.3.3, 2.3.3.7, 2.3.3.8)*

**R36. Multi-plugin stacking.** Combining `click-prism` with two or
more other Group subclasses is possible via manual subclassing
using the public `PrismMixin` (e.g.,
`class MyGroup(PrismMixin, RichGroup, DYMGroup): pass`). An
ergonomic helper for this case is out of scope for the initial
release. *(section 2.3.3.9)*

**R37. Subcommand-only fallback.** `tree_command()` works with any
group regardless of its class, as a fallback when the group subclass
path is not feasible. *(section 2.3.3.10)*

## 2.3.4.8. Robustness

**R38. Lazy groups.** Tree rendering works with lazy-loading groups
that implement `list_commands()` / `get_command()`. *(section 2.3.1.6)*

**R39. Large CLIs.** Tree renders correctly for CLIs with hundreds
of commands. Depth limiting is the management mechanism. *(section 2.3.1.6)*

**R40. Graceful failure.** Errors during traversal (import failures,
`None` commands) produce informative error nodes, not crashes.
*(section 2.3.1.6)*

**R41. Predictable behavior (invariant).** `click-prism` has no
import-time side effects and no module-level mutable state.
`import click_prism` performs no I/O, no network access, no
thread spawning, and no mutation of global state outside the
package's own modules. Detection of optional dependencies
(`rich`, `rich-click`) is lazy — computed on first use, not at
import time.

This is an invariant rather than a feature: it is satisfied
from phase 1 (where the first real code lands) onwards, and
the plan ticks it off as ✅ from that phase forward. A set of
enforcement tests in phase 1's test suite keeps it green through
every subsequent phase:

- `import click_prism` in a fresh subprocess writes nothing to
  stdout/stderr and makes no network or filesystem calls.
- After `import click_prism`, `sys.modules` does not contain
  `rich` or any other optional dependency (unless the test
  explicitly imported it first).
- A walk of `click_prism`'s module dict finds no module-level
  mutable state (no module-level `list`/`dict`/`set` that is
  meant to be mutated — constants, functions, classes, and
  type aliases are fine).

*(section 2.2.1.3)*
