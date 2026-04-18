# 3.2. Tree Model

Intermediate representation between Click's hierarchy and rendered
output. All renderers (section 3.3) consume the same `TreeNode` tree.

## 3.2.1. Data structures

```python
# _params.py
@dataclass
class ParamInfo:
    name: str
    param_type: Literal["argument", "option"]
    declarations: list[str]    # ["--env"] or ["-e", "--env"]
    type_name: str             # "TEXT", "Choice", etc.
    required: bool
    is_flag: bool
    multiple: bool
    default: Any
    help: str | None
    choices: list[str] | None  # populated for Choice types only

# _model.py
@dataclass
class TreeNode:
    name: str
    help: str | None
    node_type: Literal["group", "command", "error"]
    hidden: bool = False
    deprecated: bool = False
    params: list[ParamInfo] = field(default_factory=list)
    children: list[TreeNode] = field(default_factory=list)
    # Neighbor metadata (used by rendering; discovery details in section 3.5)
    aliases: list[str] = field(default_factory=list)
    section_name: str | None = None
    is_default: bool = False
    error_message: str | None = None
```

`ParamInfo` captures enough for both the visual parameter columns
(R25) and JSON export (R2). The display form is derived from
`declarations` at render time: arguments are uppercased; options
use the longest declaration string (`max(declarations, key=len)`),
except boolean flag pairs (`--verbose/--no-verbose`) which render
as `--[no-]flag` (the common stem with a bracketed negation
prefix).

## 3.2.2. Traversal

Recursive walk using Click's public API (`list_commands`,
`get_command`). Works identically with lazy-loading groups (R38).

```python
def build_tree(
    group: click.Group,
    ctx: click.Context,
) -> TreeNode:
    return _walk(group, ctx, visited=frozenset([id(group)]))
```

`build_tree()` always produces the **complete** tree — all
commands (including hidden), full depth, no filtering. Structural
filtering (hidden-command exclusion, depth limiting) is applied
afterwards by `filter_tree()` (section 3.2.5). JSON call paths skip
`filter_tree()` entirely, which is how "JSON always includes
everything" is guaranteed architecturally rather than by
call-site config seeding.

```python
def _walk(
    group: click.Group,
    ctx: click.Context,
    *,
    visited: frozenset[int] = frozenset(),
) -> TreeNode:
    node = TreeNode(
        name=ctx.info_name or group.name or "",
        help=group.get_short_help_str() or None,
        node_type="group",
        hidden=getattr(group, "hidden", False),
        deprecated=getattr(group, "deprecated", False),
        params=_extract_params(group),
    )

    for cmd_name in group.list_commands(ctx):
        child = _build_child(group, ctx, cmd_name, visited)
        if child is not None:
            node.children.append(child)

    return node
```

### 3.2.2.1. Child construction and error handling

```python
def _build_child(group, ctx, cmd_name, visited) -> TreeNode | None:
    try:
        cmd = group.get_command(ctx, cmd_name)
    except Exception as exc:
        return TreeNode(
            name=cmd_name, help=None, node_type="error",
            error_message=f"{type(exc).__name__}: {exc}",
        )

    if cmd is None:
        return TreeNode(
            name=cmd_name, help=None, node_type="error",
            error_message="get_command returned None",
        )

    if isinstance(cmd, click.Group):
        if id(cmd) in visited:
            return TreeNode(
                name=cmd_name, help=None, node_type="error",
                error_message="circular reference detected",
            )
        child_ctx = click.Context(cmd, info_name=cmd_name, parent=ctx)
        child = _walk(cmd, child_ctx, visited=visited | {id(cmd)})
    else:
        child = TreeNode(
            name=cmd_name,
            help=cmd.get_short_help_str() or None,
            node_type="command",
            hidden=cmd.hidden,
            deprecated=getattr(cmd, "deprecated", False),
            params=_extract_params(cmd),
        )

    child.aliases = _discover_aliases(group, cmd_name)
    child.is_default = _discover_default(group, cmd_name)
    child.section_name = _discover_section(group, cmd_name)

    return child
```

Hidden commands are always included in the tree — `_build_child`
does not filter. Structural filtering (hidden exclusion, depth
limiting) is a separate post-build step: `filter_tree()` (section 3.2.5).

Errors produce error nodes (R11, R40) — never crash the tree.

## 3.2.3. Neighbor metadata discovery

All detection uses duck typing — `getattr` checks for known
attributes. No neighbor packages are imported.

```python
def _discover_default(group: click.Group, cmd_name: str) -> bool:
    """click-default-group: check default_cmd_name attribute."""
    return getattr(group, "default_cmd_name", None) == cmd_name
```

The same pattern applies for `click-aliases` and `cloup` — the exact
attribute names are determined by inspecting their source during
implementation. The design decision is the approach: duck-typed
attribute access, no imports, no `isinstance` checks against
neighbor classes.

## 3.2.4. Parameter extraction

```python
# _params.py
def _extract_params(cmd: click.Command) -> list[ParamInfo]:
    return [
        ParamInfo(
            name=p.name,
            param_type="argument" if isinstance(p, click.Argument) else "option",
            declarations=[p.name] if isinstance(p, click.Argument) else list(p.opts),
            type_name=p.type.name,
            required=p.required,
            is_flag=getattr(p, "is_flag", False),
            multiple=getattr(p, "multiple", False),
            default=p.default,
            help=getattr(p, "help", None),
            choices=list(p.type.choices) if isinstance(p.type, click.Choice) else None,
        )
        for p in cmd.params
        if p.name != "help"  # exclude Click's built-in --help
    ]
```

## 3.2.5. Post-build filtering

`build_tree()` always produces the complete tree. Structural
filtering — hiding commands and limiting depth — is a separate
step applied between the model and render layers.

```python
# _model.py
def filter_tree(tree: TreeNode, config: TreeConfig) -> TreeNode:
    """Apply structural filtering to a complete tree.

    - Excludes hidden commands when config.show_hidden is False
    - Prunes children beyond config.depth (groups at the depth
      limit are kept but their children are removed)

    Returns a new TreeNode tree. The input is not mutated.

    JSON call paths skip this function — they pass the complete
    tree from build_tree() directly to the renderer.
    """
    return _filter_node(tree, config, depth=config.depth)
```

`depth=N` means "show N levels of children below the starting
node." `depth=0` shows only the starting node itself. `depth=1`
shows the starting node and its immediate children. `depth=None`
(or `UNLIMITED` after resolution) means no limit.

```python
def _filter_node(node, config, *, depth):
    if depth is not None and depth <= 0:
        return dataclasses.replace(node, children=[])

    child_depth = (depth - 1) if depth is not None else None
    children = [
        _filter_node(child, config, depth=child_depth)
        for child in node.children
        if not (child.hidden and not config.show_hidden)
    ]
    return dataclasses.replace(node, children=children)
```

### 3.2.5.1. Why filtering is separate from traversal

Keeping `build_tree()` free of filtering logic provides an
architectural guarantee for JSON output: JSON call paths get
the complete CLI surface by *not calling* `filter_tree()`. The
guarantee is the absence of a step, not the presence of the
right config values. This eliminates a class of bugs where a
new call site forgets to seed `show_hidden=True` and
silently produces incomplete JSON.

The pipeline for each call-site family:

```python
# Visual paths (tree-as-help, tree subcommand, standalone text):
tree = build_tree(group, ctx)
tree = filter_tree(tree, config)        # ← applies show_hidden, depth
output = render(tree, config)

# JSON paths (--help-json, standalone JSON):
tree = build_tree(group, ctx)
                                        # ← no filter_tree()
output = render(tree, config, format="json")
```

### 3.2.5.2. Failure modes

- Forgetting `filter_tree()` on a visual path: hidden commands
  appear in end-user output. Too much information — visible and
  easily caught.
- The reverse bug (forgetting to include hidden in JSON) is
  structurally impossible — JSON paths never call `filter_tree()`.
