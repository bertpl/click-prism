# 3.3. Rendering

How the tree model (section 3.2) becomes output. Three renderers share the
same `TreeNode` input and `TreeConfig` (section 3.1). This overview defines
the renderer interface and shared column layout; sub-documents cover
each renderer.

## 3.3.0. Preamble

### 3.3.0.0. Layer contracts

Three layers participate in every render path. This section defines
what each layer owns and what it does not touch.

#### 3.3.0.0.1. Model layer (section 3.2)

`build_tree()` returns a `TreeNode` tree. Every non-error node has:

| Field | Type | Notes |
|---|---|---|
| `name` | `str` | |
| `help` | `str \| None` | `None` when `get_short_help_str()` returns `""` |
| `node_type` | `Literal["group", "command", "error"]` | |
| `children` | `list[TreeNode]` | |
| `hidden` | `bool` | |
| `deprecated` | `bool` | |
| `is_default` | `bool` | |
| `section_name` | `str \| None` | |
| `params` | `list[ParamInfo]` | |
| `aliases` | `list[str]` | |

Error nodes additionally carry `error_message: str`. All other fields
on error nodes are present but carry their zero/default values (at the
model layer — JSON output omits them, see section 3.3.0.0.4) — renderers
must branch on `node_type == "error"` rather than inspecting other
fields.

**Model layer owns:** traversal, child ordering, circular-reference
detection, error node creation. `build_tree()` always produces a
**complete** tree — all commands (including hidden), full depth.

**Model layer does NOT own:** structural filtering (hidden, depth),
formatting, column widths, ANSI codes.

**Post-build filtering:** `filter_tree()` (section 3.2.5) applies
`show_hidden` exclusion and `depth` limiting between the model
and render layers. Visual call paths invoke it; JSON call paths
skip it — this is the architectural guarantee that JSON always
produces the complete CLI surface.

#### 3.3.0.0.2. Render layer (section 3.3)

Each renderer takes a `TreeNode` tree and a resolved `TreeConfig` and
returns `str`.

**Render layer owns:** all formatting decisions, column layout, ANSI
codes, format-specific field inclusion/exclusion, output encoding.

**Render layer does NOT:** write to stdout, call `click.echo()`, or
interact with any formatter. It only returns strings.

#### 3.3.0.0.3. Output path (section 3.4.2)

Callers in section 3.4.2 receive the string from the render layer and decide
where it goes:

| Caller | Output sink |
|---|---|
| `format_commands()` | `formatter.write(output)` |
| `_help_json_callback()` | `click.echo(output)` |
| `show_tree()` | `click.echo(output)` |
| `render_tree()` | returned to caller |

**Output path owns:** the decision to write to stdout, pass to
Click's formatter, or return the string.

**`format_help()` contract:** `PrismMixin.format_help()` is the
routing layer that ensures `format_commands()` is reached
regardless of what the wrapped class does with `format_help()`.
When tree-as-help is active, `format_help()` takes over the
page: it calls `click.Command.format_options(self, ctx,
formatter)` for the Options section, then
`self.format_commands()` for the tree. The explicit base-class
call `click.Command.format_options` renders options only —
bypassing `click.Group.format_options()` (which internally calls
`format_commands()`, causing double-rendering) and bypassing
wrapped-class overrides that may bundle command rendering into
`format_options()` (e.g. `rich-click`). When tree-as-help is not
active, `super().format_help()` delegates to the wrapped class —
its full pipeline runs unmodified.

**`format_commands()` contract:** when tree mode is active,
`PrismMixin.format_commands()` writes the tree output via
`formatter.write(output)` and returns — it does **not** call
`super().format_commands()`. The tree replaces Click's standard
command list entirely. When tree mode is not active (`mode="none"`,
or `mode="root"` on a non-root group), `super().format_commands()` is
called and Click's standard output is produced.

**ANSI safety:** when `RichRenderer` produces ANSI codes,
`formatter.write()` may mangle them through Click's wrapping. This
must be validated during implementation. If mangling is confirmed,
the fix is to bypass `formatter.write()` and write directly to stdout
for the tree portion. The chosen approach must be documented back
into this section.

#### 3.3.0.0.4. JSON error node schema

Error nodes in JSON output contain exactly three fields:

```json
{
  "name": "failing-cmd",
  "type": "error",
  "error_message": "ExceptionType: message text"
}
```

Fields absent from this list (`children`, `params`, `hidden`,
`deprecated`, `is_default`, `section_name`) are **omitted** — not
set to `null`. Consumers must handle error nodes as a distinct
structural variant, not as a standard node with optional nulls.

### 3.3.0.1. Renderer interface

```python
class Renderer(ABC):
    @abstractmethod
    def render(self, tree: TreeNode) -> str: ...
```

All renderers return `str`. The `rich` renderer uses
`Console.capture()` (section 3.3.2) to produce a string containing ANSI
escape codes, rather than printing directly to stdout.

```python
def render(tree: TreeNode, config: TreeConfig, format: Literal["text", "json"] = "text") -> str:
    return select_renderer(config, format).render(tree)

def select_renderer(config: TreeConfig, format: Literal["text", "json"] = "text") -> Renderer:
    if format == "json":
        return JsonRenderer()
    if _should_use_rich():
        return RichRenderer(config)
    return PlainRenderer(config)
```

`_should_use_rich()` from `_compat` (section 3.0.4) — true when `rich` is
available and stdout is a TTY. Selection is automatic — the developer
does not choose a renderer.

### 3.3.0.2. Column layout

Shared by plain text (section 3.3.1) and `rich` (section 3.3.2). `rich` adds styling on
top of the same positional layout.

#### 3.3.0.2.1. 2-column mode (default)

```
projex
├── config        Manage configuration settings
│   ├── get        Get a configuration value
```

| Column | Content | Width |
|---|---|---|
| Tree + Name | Glyphs + command name | Widest entry |
| Description | Short help text | Remaining |

When the description would exceed the remaining terminal width, it
is truncated with `...`.

#### 3.3.0.2.2. 4-column mode (`show_params=True`)

```
projex            Description                              Arguments  Options
├── config        Manage configuration settings
│   ├── get        Get a configuration value                KEY
│   ├── run        Run a deployment                                    --env, --dry-run
```

Header row: root name labels column 0; `Description`, `Arguments`,
`Options` label the rest.

**Shared across visual renderers.** 4-column mode is a pure
positional-layout concern and lives in shared width/packing code.
Both the plain text renderer (section 3.3.1) and the `rich` renderer (section 3.3.2)
consume the same layout primitives — `rich` adds styling on top,
but the column positions, header row, and overflow behavior are
identical between them. JSON (section 3.3.3) is unaffected: it carries
arguments and options as structured arrays per node, not columns.

**Overfull-column fallback.** When terminal width is too narrow
to fit every column at its natural size, the renderer degrades
in a fixed priority order: Options column clips first, then the
Arguments column, then the Description column. The exact
packing/truncation/wrapping algorithm — whether columns are
clipped to a minimum width, hidden entirely, or wrapped — is
intentionally left to the implementer. The design
constraints are: degradation order is deterministic (Options →
Arguments → Description), the header row stays aligned with the
body, and no row ever exceeds terminal width.

#### 3.3.0.2.3. Width calculation

Two-pass:
1. Walk all visible nodes, compute max `len(tree_prefix + name)`.
2. That maximum sets column 0 width; remaining terminal width is
   distributed to other columns.

#### 3.3.0.2.4. Description indent

Nested commands get a 1-character indent in the description column,
echoing tree depth within the columnar layout.

#### 3.3.0.2.5. Root label

The root row displays `ctx.command_path` (R16) — the full
command path from the CLI entry point to the rendered group
(e.g. `projex deploy` rather than `deploy`). This is the same
path Click uses in `Usage:` lines. For `show_tree()` /
`render_tree()` with a synthetic context, the path naturally
contains only the group name since no parent context exists.

**Mechanism:** `build_tree()` (section 3.2) stores the bare command
name in `TreeNode.name`. Visual call paths set
`tree.name = ctx.command_path` on the root node before passing
it to the renderer. JSON call paths leave `tree.name`
unchanged — the bare name is the stable, machine-readable
identifier. This follows the same pattern as the
`show_hidden=True` seed in `render_tree()` (section 3.4.2.4.2): the
call site adjusts the data for its output mode before entering
the shared pipeline.

#### 3.3.0.2.6. Terminal width

- TTY: detected terminal width
- Piped: 80 columns (Click and `rich` default)

### 3.3.0.3. Markers

| State | Plain text | Rich | JSON |
|---|---|---|---|
| Hidden | `[hidden]` suffix | Dim text | `"hidden": true` |
| Deprecated | `[deprecated]` suffix | Strikethrough | `"deprecated": true` |
| Error | `(error: msg)` | Red, with message | `"type": "error"`, `error_message` field |
| Default | `*` suffix | `*` suffix | `"is_default": true` |

### 3.3.0.4. Sub-sections

- [3.3.1. Plain Text](3_3_1_plain_text.md) — character sets, prefix
  construction, section headings
- [3.3.2. Rich](3_3_2_rich.md) — auto-detection, Console, theme
  application, degradation
- [3.3.3. JSON](3_3_3_json.md) — schema, inclusion rules
