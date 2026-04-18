# 3.4.2. Integration Points

User-facing entry points built on the class architecture (section 3.4.1) and
renderers (section 3.3).

## 3.4.2.1. Tree-as-help

Two overrides work together: `format_help()` routes the help
pipeline; `format_commands()` renders the tree.

`PrismMixin.format_help()` — routes the help pipeline:

```python
def format_help(self, ctx, formatter):
    mode = self._resolve_tree_help(ctx)
    if mode == "all" or (mode == "root" and ctx.parent is None):
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        click.Command.format_options(self, ctx, formatter)
        self.format_commands(ctx, formatter)
        self.format_epilog(ctx, formatter)
    else:
        super().format_help(ctx, formatter)
```

When tree-as-help is active, `format_help()` calls
`click.Command.format_options` (options only) followed by
`self.format_commands()` (tree). The explicit base-class call
bypasses `click.Group.format_options()` — which internally calls
`format_commands()` and would double-render — and bypasses
wrapped-class overrides like `rich-click`'s `format_options()`
which bundles command rendering into its panel system and never
calls `format_commands()`. See section 3.3.0.0.3 for the full contract.

When tree-as-help is not active, `super().format_help()` runs
the wrapped class's full pipeline unmodified.

`PrismMixin.format_commands()` — renders tree or delegates:

```python
def format_commands(self, ctx, formatter):
    mode = self._resolve_tree_help(ctx)
    if mode == "all" or (mode == "root" and ctx.parent is None):
        config = _effective_config_for(self, ctx).resolve()
        tree = build_tree(self, ctx)
        tree.name = ctx.command_path          # root label (section 3.3.0.2.5)
        tree = filter_tree(tree, config)
        output = render(tree, config)
        formatter.write(output)
    else:
        super().format_commands(ctx, formatter)
```

The layer contract governing ownership between the model layer,
render layer, and output path (including when `super()` is and is
not called) is in section 3.3.0.0.

### 3.4.2.1.1. _resolve_tree_help()

Context-chain walk (precedence level 3 from section 3.1):

```python
def _resolve_tree_help(self, ctx: click.Context) -> str:
    # This group's explicit config
    if self.tree_config and self.tree_config.tree_help is not None:
        return self.tree_config.tree_help
    # Nearest ancestor with an opinion
    parent_ctx = ctx.parent
    while parent_ctx:
        cmd = parent_ctx.command
        if (isinstance(cmd, PrismMixin)
                and cmd.tree_config
                and cmd.tree_config.tree_help is not None):
            return cmd.tree_config.tree_help
        parent_ctx = parent_ctx.parent
    # Default
    return "root"
```

**Root detection**: `ctx.parent is None`. A PrismGroup on a subgroup
with `tree_help="root"` (default) does NOT show tree-as-help —
"root" means CLI entry point.

### 3.4.2.1.2. _effective_config_for()

Module-level helper that produces the effective (unresolved)
`TreeConfig` for a given group by walking the context chain and
merging each tree-aware ancestor's config as a fallback.

```python
def _effective_config_for(
    group: click.Group, ctx: click.Context | None
) -> TreeConfig:
    """Walk the context chain to produce the effective (unresolved)
    TreeConfig for `group`.

    `ctx` is the context *for `group`* — not for any child command.
    Works with plain click.Group instances too: non-PrismMixin
    groups simply contribute nothing to the walk.

    The returned config is pre-.resolve(); the caller applies
    defaults (and any runtime overrides like --depth) before use.
    """
    # Start with the group's own config, if any.
    result = TreeConfig()
    if isinstance(group, PrismMixin) and group.tree_config is not None:
        result = group.tree_config

    # Walk ancestors: for each tree-aware ancestor, merge its
    # config in as the fallback (child wins, parent fills gaps).
    parent_ctx = ctx.parent if ctx is not None else None
    while parent_ctx is not None:
        parent_cmd = parent_ctx.command
        if (isinstance(parent_cmd, PrismMixin)
                and parent_cmd.tree_config is not None):
            result = result.merge(parent_cmd.tree_config)
        parent_ctx = parent_ctx.parent

    return result
```

Called from two sites:

- `PrismMixin.format_commands()` (section 3.4.2.1 above) — `self` is the group
  being rendered, `ctx` is its own context:
  `_effective_config_for(self, ctx)`
- `tree_command()` factory (section 3.4.2.3 below) — the parent group comes
  from `ctx.parent.command`, and the context for that group is
  `ctx.parent`: `_effective_config_for(ctx.parent.command, ctx.parent)`

### 3.4.2.1.3. Rationale: module-level, not a PrismMixin method

`_effective_config_for` is a module-level function rather than a
`PrismMixin` method because call site 2 — the `tree_command()`
factory — must work on groups that are **not** PrismMixin
instances. R37 explicitly requires this: "`tree_command()` works
with any group regardless of its class, as a fallback when the
group subclass path is not feasible." A method on `PrismMixin`
could not serve that call site, so a module-level helper is the
only form that unifies both.

A thin method wrapper (e.g. `self._effective_config(ctx)` →
`return _effective_config_for(self, ctx)`) was considered and
rejected on two grounds:

1. It would misleadingly suggest the logic is PrismMixin-specific,
   when the whole point is that it handles plain `click.Group`
   ancestors gracefully (`isinstance` checks degrade to "no
   contribution").
2. Two entry points for one function is two places to keep in
   sync. The earliest review pass of this plan caught the method
   and the module-level helper having drifted to different
   signatures — a direct consequence of having both.

Contrast with `_resolve_tree_help()` (section 3.4.2.1.1), which **is** a
PrismMixin method. That asymmetry is deliberate:
`_resolve_tree_help()` is only ever called from
`format_help()` and `format_commands()` — both PrismMixin
methods — so `self` is guaranteed to be a PrismMixin by
construction. It cannot encounter a non-PrismMixin receiver. `_effective_config_for()`
has no such guarantee and therefore lives at module scope.

### 3.4.2.1.4. Coexistence with tree subcommand

Tree-as-help uses developer config (not adjustable at runtime).
The tree subcommand gives end users `--depth`. Both coexist when
present — the tree subcommand is never auto-created by PrismGroup;
it requires explicit `add_command(tree_command())`.

## 3.4.2.2. --help-json

Eager option on the root group. `PrismMixin.make_context()` (section 3.4.1)
appends the option to `self.params` when `parent is None` — before
`super().make_context()` parses args. This is the earliest point
where root status is known and the latest point before parsing.

```python
def _help_json_option(self) -> click.Option:
    return click.Option(
        ["--help-json"],
        is_eager=True,
        expose_value=False,
        is_flag=True,
        callback=self._help_json_callback,
        help="Output CLI structure as JSON and exit.",
    )

def _help_json_callback(self, ctx, param, value):
    if not value:
        return
    # Fresh default config — intentional. The JSON renderer does not
    # consult any TreeConfig fields; group config is irrelevant here.
    config = TreeConfig().resolve()
    tree = build_tree(self, ctx)
    click.echo(render(tree, config, format="json"))
    ctx.exit(0)
```

Full depth, all metadata included (section 3.3.3). The complete-tree
guarantee is architectural: `filter_tree()` is not called, so
`show_hidden` and `depth` are irrelevant — the renderer receives
every command and every level.

## 3.4.2.3. tree_command()

Factory returning a Click command. Works with any Group (R37).

```python
_TREE_CMD_MARKER = "_click_prism_cmd"

def tree_command(
    name: str = "tree",
    config: TreeConfig | None = None,
    **kwargs: Any,
) -> click.Command:
    if config is not None and config.tree_help not in (None, "none"):
        raise PrismError(
            f"tree_command() does not support tree_help={config.tree_help!r}; "
            "set tree_help on the parent PrismGroup instead."
        )

    @click.command(name=name, **kwargs)
    @click.option("--depth", type=int, default=None,
                  help="Limit tree depth.")
    @click.pass_context
    def _tree(ctx: click.Context, depth: int | None) -> None:
        parent = ctx.parent.command
        effective = _effective_config_for(parent, ctx.parent)
        if config is not None:
            effective = config.merge(effective)
        if depth is not None:
            effective = TreeConfig(depth=depth).merge(effective)
        effective = effective.resolve()

        tree = build_tree(parent, ctx.parent)
        tree.name = ctx.parent.command_path   # root label (section 3.3.0.2.5)
        tree = filter_tree(tree, effective)
        output = render(tree, effective)
        click.echo(output)

    setattr(_tree, _TREE_CMD_MARKER, True)

    if not _tree.help:
        _tree.help = "Display the command tree."

    return _tree

The merge-then-resolve ordering used above — and why the order
is an invariant (reversing it would corrupt `UNLIMITED`) — is
documented in section 3.1.4.
```

### 3.4.2.3.1. tree_help validation

`tree_help` modes (section 3.4.2.1) are not applicable to `tree_command()` —
the command is a leaf subcommand, not a group whose help text
`click-prism` intercepts. Passing a config with `tree_help` set to
anything other than `None` or `"none"` raises `PrismError` at
**definition time** (when `tree_command()` is called), not at
invocation. This surfaces the misconfiguration before the application
starts.

### 3.4.2.3.2. Subtree scoping

`ctx.parent.command` — the group this tree command belongs to.
`projex tree` shows full tree; `projex deploy tree` shows deploy
subtree.

### 3.4.2.3.3. Name collision

`PrismMixin.add_command()` (section 3.4.1) raises `PrismError` at
definition time whenever a tree command name and a regular command
name collide — regardless of which was registered first (section 2.2.1.3).
Both directions are covered:

- A `_click_prism_cmd`-marked command added to a group that already
  has a command with the same name.
- A regular command added to a group that already has a
  `_click_prism_cmd`-marked command with the same name.

For the R37 fallback path (non-PrismMixin groups), there is no
`add_command` override — Click's standard overwrite applies.

## 3.4.2.4. Standalone functions

Integration path 3 ("standalone") — the developer calls a Python
function from their own code without modifying the CLI. Two entry
points cover the two common shapes: print to stdout, or return
the rendered string. Both share semantics; only the output sink
differs.

### 3.4.2.4.1. show_tree()

```python
def show_tree(
    cli: click.Group,
    *,
    config: TreeConfig | None = None,
    format: Literal["text", "json"] = "text",
) -> None:
    click.echo(render_tree(cli, config=config, format=format))
```

- Synthetic context — no CLI invocation needed
- Hidden commands included by default (developer inspection tool)
- `format="json"` follows JSON inclusion rules (section 3.3.3)
- No side effects on the CLI object

### 3.4.2.4.2. render_tree()

```python
def render_tree(
    cli: click.Group,
    *,
    config: TreeConfig | None = None,
    format: Literal["text", "json"] = "text",
) -> str:
    ctx = click.Context(cli, info_name=cli.name or "cli")
    tree = build_tree(cli, ctx)
    if format == "json":
        effective = (config or TreeConfig()).resolve()
    else:
        tree.name = ctx.command_path          # root label (section 3.3.0.2.5)
        base = TreeConfig(show_hidden=True)
        effective = (config.merge(base) if config is not None else base).resolve()
        tree = filter_tree(tree, effective)
    return render(tree, effective, format=format)
```

Same behavior as `show_tree()` — synthetic context, JSON format
supported — but returns the rendered string instead of writing to
stdout. `show_tree()` is literally `click.echo(render_tree(cli))`.

For **text** output, hidden commands are included by default
(developer inspection tool — R4) via the `show_hidden=True` seed.
`filter_tree()` applies `show_hidden` and `depth` from the
resolved config.

For **JSON** output, `filter_tree()` is skipped — the complete
tree is rendered directly (section 3.2.5). The `show_hidden=True` seed
is unnecessary because no filtering step runs.

Useful for capturing tree output into tests (assertions,
snapshots), embedding in generated docs (MkDocs includes), and
piping through post-processors. `build_tree`, `filter_tree`, and
the `render` dispatcher (section 3.3) remain internal helpers —
`render_tree()` is the public one-liner that covers the string
use case without exposing the `TreeNode` model.
