# 3.1. Configuration

All behavior is parameterized through `TreeConfig` and `TreeTheme`.
Both use `None`-as-unset semantics for layered configuration with
clear precedence.

## 3.1.1. TreeConfig

```python
UNLIMITED: Final[int] = -1

@dataclass
class TreeConfig:
    style: Literal["unicode", "ascii"] | None = None
    depth: int | None = None       # None, UNLIMITED (-1), or >= 0
    show_hidden: bool | None = None
    show_params: bool | None = None
    tree_help: Literal["root", "all", "none"] | None = None
    theme: TreeTheme | None = None
```

All fields default to `None` (unset). An explicit value overrides;
`None` is transparent in merge and precedence resolution.

The tree subcommand name is not part of `TreeConfig` — it lives
on the `tree_command(name=...)` factory (section 3.4.2).

`UNLIMITED` (`-1`) is distinct from `None`: it means "explicitly no
depth limit." This matters when a child group needs to override a
parent's depth restriction:

```python
@click.group(cls=PrismGroup, tree_config=TreeConfig(depth=2))
def cli(): ...

@cli.group(tree_config=TreeConfig(depth=UNLIMITED))
def admin(): ...
```

`depth=None` on `admin` would inherit the parent's `depth=2`.
`depth=UNLIMITED` overrides it.

### 3.1.1.1. resolve()

Returns a fully-populated config with defaults applied:

```python
def resolve(self) -> TreeConfig:
    if (self.depth is not None
            and self.depth < 0
            and self.depth != UNLIMITED):
        raise PrismError(
            f"Invalid depth {self.depth!r}. "
            "Use None (inherit), UNLIMITED (-1), or a non-negative integer."
        )
    return TreeConfig(
        style=self.style if self.style is not None else _default_style(),
        depth=None if self.depth == UNLIMITED else self.depth,
        show_hidden=self.show_hidden if self.show_hidden is not None else False,
        show_params=self.show_params if self.show_params is not None else False,
        tree_help=self.tree_help if self.tree_help is not None else "root",
        theme=_resolve_theme(self.theme),
    )
```

After resolution, all fields except `depth` are guaranteed
non-`None`. `depth` of `None` means unlimited; `UNLIMITED` is
normalized to `None` during resolution.

`_default_style()` (from `_compat`, section 3.0) returns `"unicode"` or
`"ascii"` based on whether `sys.stdout.encoding` can represent
Unicode box-drawing characters (section 2.2.2). An explicit `style=`
set by the developer is never overridden — the encoding check
only applies when `style` is left unset.

### 3.1.1.2. merge()

`a.merge(b)` returns a new `TreeConfig` where `a`'s non-`None`
fields win and `b` provides the fallback for every field where
`a` is `None`. Read as: "`a` is the override, `b` is the base."

```python
def merge(self, base: TreeConfig) -> TreeConfig:
    return TreeConfig(**{
        f.name: (v if v is not None else getattr(base, f.name))
        for f in fields(self)
        for v in [getattr(self, f.name)]
    })
```

Example — a child group overrides only `depth`, inheriting the
parent's `style` and `show_hidden`:

```python
parent = TreeConfig(style="ascii", show_hidden=True, depth=3)
child  = TreeConfig(depth=1)

child.merge(parent)
# TreeConfig(style="ascii", depth=1, show_hidden=True, ...)
```

The same shape is used at the CLI-flag layer: `TreeConfig(depth=flag_value).merge(group_config)`
applies a runtime `--depth` override on top of the group's config
(section 3.4.2).

## 3.1.2. Precedence

From highest to lowest:

1. **CLI flags** on tree subcommand (runtime, end-user)
2. **Per-group config** on current group (developer)
3. **Inherited config** from nearest ancestor tree-enabled group
4. **Built-in defaults** (in `resolve()`)

Level 3 uses a **context-chain walk** at render time: walk
`ctx.parent` looking for the nearest `PrismMixin`-based ancestor
with a non-`None` value for the field being resolved. The walk
uses Click's public context API. Implementation in section 3.4.2.

## 3.1.3. TreeTheme

Two orthogonal axes — vertical (per-column) and horizontal
(per-row-type):

```python
@dataclass
class ColumnStyle:
    color: str | None = None    # "cyan", "bright_black", "#70c0a0"
    dim: bool | None = None

@dataclass
class RowStyle:
    bold: bool | None = None
    italic: bool | None = None
    dim: bool | None = None
    # No color — color is a vertical concern only

@dataclass
class ThemeColumns:
    guides: ColumnStyle = field(default_factory=ColumnStyle)
    group_names: ColumnStyle = field(default_factory=ColumnStyle)
    command_names: ColumnStyle = field(default_factory=ColumnStyle)
    description: ColumnStyle = field(default_factory=ColumnStyle)
    arguments: ColumnStyle = field(default_factory=ColumnStyle)
    options: ColumnStyle = field(default_factory=ColumnStyle)

@dataclass
class ThemeRows:
    title: RowStyle = field(default_factory=RowStyle)
    groups: RowStyle = field(default_factory=RowStyle)
    commands: RowStyle = field(default_factory=RowStyle)

@dataclass
class TreeTheme:
    columns: ThemeColumns = field(default_factory=ThemeColumns)
    rows: ThemeRows = field(default_factory=ThemeRows)

    @classmethod
    def built_in(cls, name: str | BuiltinTheme) -> TreeTheme:
        """Look up a built-in theme by name. See section 3.1.3.3."""
        ...
```

**On `ThemeRows` field names.** `title` is singular because the
title is literally one row in the output. `groups` and `commands`
are plural because each covers a *category* of rows — every group
row and every command row respectively. When R30 or other prose
in the plan refers to "title, group, command" as row-type labels,
those are the English category names; the Python field names for
the collection row-types are the plural forms on this class.

Group names and command names are separate column entries so the
developer can assign different colors for terminals that lack bold
support.

### 3.1.3.1. Composition

Cell style = column style + row style:

- **Color**: column only
- **Bold, italic**: row only
- **Dim**: OR of both axes

The types enforce this — `ColumnStyle` has no bold/italic,
`RowStyle` has no color.

### 3.1.3.2. Default theme

The values below are **indicative** — they capture the design intent
(muted guides, accented command names, dimmed descriptions) but the
exact colors and weights may be adjusted during implementation.

**Columns:**

| | guides | group_names | command_names | description | arguments | options |
|---|---|---|---|---|---|---|
| color | `bright_black` | `cyan` | `cyan` | — | `bright_blue` | `blue` |
| dim | yes | — | — | yes | — | — |

**Rows:**

| | title | groups | commands |
|---|---|---|---|
| bold | yes | yes | — |

### 3.1.3.3. Resolution

**`TreeTheme.built_in()` — factory method for named themes:**

```python
@classmethod
def built_in(cls, name: str | BuiltinTheme) -> TreeTheme:
    try:
        key = BuiltinTheme(name) if isinstance(name, str) else name
    except ValueError:
        raise PrismError(
            f"Unknown theme {name!r}. "
            f"Available: {', '.join(BuiltinTheme)}"
        )
    return _THEME_MAP[key]
```

Returns a complete `TreeTheme` for the named built-in. Passed to
`TreeConfig(theme=...)` like any other `TreeTheme` instance.

**`_resolve_theme()` — internal, called by `TreeConfig.resolve()`:**

```python
def _resolve_theme(raw: TreeTheme | None) -> TreeTheme:
    if raw is None:
        return DEFAULT_THEME
    return _fill_from_default(raw)  # unset fields inherit from default
```

Unset fields in a custom `TreeTheme` inherit from the **default**
theme, not from any parent group's theme. Theme inheritance is flat.

### 3.1.3.4. Portability

When `rich` is not installed (`_compat`, section 3.0.4), theme settings are
silently ignored. No conditional code needed — the same `TreeConfig`
works everywhere.

## 3.1.4. End-to-end resolution algorithm

This section specifies how the individual pieces — `merge()`,
`resolve()`, `UNLIMITED`, the precedence chain, flat theme
inheritance, and inert fields — compose into a single algorithm.
The pieces are defined separately above; their interaction is
pinned here.

### 3.1.4.1. Canonical call order

Always **merge first, resolve last**:

```
effective = child_config.merge(parent_config)   # 1. apply precedence
effective = effective.resolve()                  # 2. fill defaults
```

Reversing the order corrupts UNLIMITED: `resolve()` normalizes
`UNLIMITED` (`-1`) to `None`, so merging a resolved config loses
the "explicitly no limit" intent (the field becomes `None`, which
is transparent to `merge()` and allows a parent's numeric depth to
win). `merge()` must always operate on **unresolved** configs.

`_effective_config_for()` (section 3.4.2.1.2) returns an unresolved config
for exactly this reason — all callers resolve after any remaining
overrides are applied.

### 3.1.4.2. UNLIMITED in merge()

`UNLIMITED` (`-1`) is a non-`None` int. `merge()` treats it
identically to any other explicit value: the child wins.

```python
parent = TreeConfig(depth=2)
child  = TreeConfig(depth=UNLIMITED)

result = child.merge(parent)
# TreeConfig(depth=-1, ...)   <-- UNLIMITED wins; parent's 2 is ignored

result.resolve()
# TreeConfig(depth=None, ...)  <-- UNLIMITED normalized to None (= no limit)
```

Corollary: a child group that wants to lift a parent's depth
restriction must use `depth=UNLIMITED`. Using `depth=None` is
transparent and lets the parent's restriction propagate.

### 3.1.4.3. Inert fields

Fields whose consuming code is not yet active are silently ignored.
The field is present in the dataclass and participates in `merge()`
and `resolve()` normally — the consuming code simply does not read
it yet. No warning is raised, no error is thrown, the stored value
is preserved until its consumer wires it up.

Downstream code should not special-case inert fields. The silencing
is the consumer's responsibility, not the config layer's.

### 3.1.4.4. show_hidden default asymmetry

The default for `show_hidden` differs by call-site family:

| Call-site family | `show_hidden` | Mechanism |
|---|---|---|
| JSON paths (`--help-json`, `render_tree(format="json")`) | N/A | `filter_tree()` skipped — complete tree rendered |
| Standalone text (`render_tree()`, `show_tree()`) | `True` | Seeds `TreeConfig(show_hidden=True)` before `filter_tree()` |
| End-user visual (tree-as-help, `tree_command()`) | `False` | `resolve()` applies `False` default |

This is intentional, not an inconsistency. The mechanism is
architectural: JSON paths skip `filter_tree()` entirely (section 3.2.5),
so `show_hidden` is irrelevant — the complete tree is always
rendered. Visual standalone paths apply `filter_tree()` with
`show_hidden=True` seeded via `TreeConfig(show_hidden=True)`
(section 3.4.2.4.2). End-user visual paths rely on `resolve()` applying
the `False` default when `show_hidden` is left `None`.

### 3.1.4.5. theme in merge()

`theme` participates in `merge()` identically to every other field:
if the child's `theme` is non-`None`, it wins; if `None`, the
parent's `theme` fills in.

```python
parent = TreeConfig(theme=TreeTheme.built_in("dark"))
child  = TreeConfig(style="ascii")   # theme is None

child.merge(parent)
# TreeConfig(style="ascii", theme=<dark TreeTheme>, ...)
```

Once `_resolve_theme()` runs inside `.resolve()`, unset fields
within a custom `TreeTheme` inherit from the **default** theme
only — never from a parent group's `TreeTheme` instance. Theme
inheritance is flat within the theme object; the `theme` *field*
in `TreeConfig` follows the normal merge chain.

### 3.1.4.6. Complete worked example

Setup:

```python
# Root group: ascii style, depth 2
@click.group(cls=PrismGroup, tree_config=TreeConfig(style="ascii", depth=2))
def cli(): ...

# Admin subgroup: depth UNLIMITED (lifts root's restriction)
@cli.group(cls=PrismGroup, tree_config=TreeConfig(depth=UNLIMITED))
def admin(): ...

# tree_command() added to admin; end user passes --depth 1
admin.add_command(tree_command())
```

Execution: `projex admin tree --depth 1`

**Step 1 — `_effective_config_for(admin, admin_ctx)`**

Walk the context chain. `admin` has `TreeConfig(depth=UNLIMITED)`;
its parent `cli` has `TreeConfig(style="ascii", depth=2)`.

```python
result = TreeConfig(depth=UNLIMITED)          # admin's own config
result = result.merge(TreeConfig(style="ascii", depth=2))  # merge cli config as the fallback
# → TreeConfig(style="ascii", depth=UNLIMITED)
#   admin's depth=-1 wins; cli's style="ascii" fills the gap
```

**Step 2 — apply runtime `--depth 1`**

```python
effective = TreeConfig(depth=1).merge(result)
# → TreeConfig(style="ascii", depth=1)
#   flag's depth=1 wins over UNLIMITED
```

**Step 3 — `resolve()`**

```python
effective = effective.resolve()
# → TreeConfig(
#       style="ascii",      # explicit, passes through
#       depth=1,            # numeric, passes through (not UNLIMITED)
#       show_hidden=False,  # default
#       show_params=False,  # default
#       tree_help="root",   # default
#       theme=DEFAULT_THEME # None → default theme
#   )
```

Final result: ascii style, depth capped at 1, hidden commands
excluded, no params shown.

**What changes if the user omits `--depth`?**

Step 2 is skipped (`depth is None` in the command callback, so
`TreeConfig(depth=...).merge(...)` is not called). Step 3 then
normalizes `UNLIMITED` (`-1`) to `None`, yielding `depth=None` —
no depth limit.
