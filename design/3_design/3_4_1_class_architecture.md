# 3.4.1. Class Architecture

Tree behavior lives in `PrismMixin`. `PrismGroup` is the convenience
class; `wrapping()` combines it with any Group subclass.
`PrismError` is the single exception type `click-prism`
introduces.

```python
# _exceptions.py
class PrismError(click.ClickException):
    """Raised by click-prism for user-facing configuration errors
    (name collisions, invalid config combinations, etc.).

    Subclassing click.ClickException means Click formats the error
    and exits with a non-zero status automatically.
    """
```

Lives in `_exceptions.py` (section 3.0) and is re-exported from `click_prism`.

## 3.4.1.1. PrismMixin

```python
class PrismMixin:
    """Mixin: tree visualization for any click.Group subclass.
    
    Uses cooperative super() — next class in MRO handles
    non-tree behavior.
    """

    def __init__(
        self, *args: Any, tree_config: TreeConfig | None = None, **kwargs: Any
    ) -> None:
        self.tree_config: TreeConfig | None = tree_config
        super().__init__(*args, **kwargs)

    def make_context(
        self,
        info_name: str | None,
        args: list[str],
        parent: click.Context | None = None,
        **extra: Any,
    ) -> click.Context:
        """Add --help-json on root group. See section 3.4.2.2."""
        # Guard: CliRunner.invoke() reuses the group object, so
        # make_context may be called multiple times.
        if parent is None and not any(p.name == "help_json" for p in self.params):
            self.params.append(self._help_json_option())
        return super().make_context(info_name, args, parent=parent, **extra)

    def add_command(self, cmd: click.Command, name: str | None = None) -> None:
        """Detect tree command name collisions. See section 3.4.2.3.3."""
        cmd_name = name or cmd.name
        existing = (self.commands or {}).get(cmd_name)
        if getattr(cmd, "_click_prism_cmd", False) and existing is not None:
            raise PrismError(
                f"Cannot add tree command {cmd_name!r}: a command with"
                f" that name already exists. Use tree_command(name=...)"
                f" to choose a different name."
            )
        if getattr(existing, "_click_prism_cmd", False):
            raise PrismError(
                f"Cannot add command {cmd_name!r}: it would overwrite the"
                f" tree command with that name. Use tree_command(name=...)"
                f" to give the tree command a different name."
            )
        super().add_command(cmd, name)

    def format_help(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """Tree-aware help pipeline. See section 3.3.0.0.3."""
        mode = self._resolve_tree_help(ctx)
        if mode == "all" or (mode == "root" and ctx.parent is None):
            # Tree-as-help active: this page is owned by click-prism.
            # click.Command.format_options (not self.format_options)
            # renders options only — bypasses Group.format_options()
            # which would also call format_commands(), and bypasses
            # wrapped-class overrides that may bundle command rendering
            # into format_options() (e.g. rich-click).
            self.format_usage(ctx, formatter)
            self.format_help_text(ctx, formatter)
            click.Command.format_options(self, ctx, formatter)
            self.format_commands(ctx, formatter)
            self.format_epilog(ctx, formatter)
        else:
            super().format_help(ctx, formatter)

    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        """Tree-as-help or delegate. See section 3.4.2.1."""
        ...
```

### 3.4.1.1.1. tree_config capture

`__init__` intercepts `tree_config` from kwargs before
`super().__init__()`. Click's `Group.__init__` accepts `**attrs`
which would silently store unknown kwargs — `PrismMixin` intercepts
first to keep the attribute typed and accessible.

### 3.4.1.1.2. Cooperative super()

`make_context()`, `add_command()`, `format_help()`, and
`format_commands()` call `super()`. Python's MRO routes it to
whatever class comes next:

- `PrismGroup`: `super()` -> `click.Group`
- Wrapped class: `super()` -> `RichGroup` (or `cloup`, DYMGroup, etc.)

`format_help()` is the routing layer: when tree-as-help is not
active, `super().format_help()` delegates to the wrapped class —
its full help pipeline runs unmodified. When tree-as-help is
active, `format_help()` takes over the page, calling
`click.Command.format_options()` (options only) followed by
`self.format_commands()` (tree). The full contracts are in
section 3.3.0.0.

## 3.4.1.2. PrismGroup

```python
class PrismGroup(PrismMixin, click.Group):
    pass

PrismGroup.group_class = PrismGroup
```

MRO: `PrismGroup -> PrismMixin -> click.Group`

`group_class` ensures children created via `@cli.group()`
inherit `PrismGroup` automatically (R5). This is Click's built-in
propagation mechanism.

## 3.4.1.3. wrapping()

Factory for combining tree behavior with another Group subclass:

```python
@classmethod
def wrapping(cls, base_class: type[click.Group]) -> type[PrismGroup]:
    if base_class is click.Group:
        return cls

    combined = type(
        f"Tree{base_class.__name__}",
        (PrismMixin, base_class),
        {},
    )
    combined.group_class = combined
    return combined
```

`PrismGroup.wrapping(RichGroup)` produces:

MRO: `TreeRichGroup -> PrismMixin -> RichGroup -> ... -> click.Group`

`group_class` is set to the combined class itself — children
inherit the full combination (PrismMixin + base class), not just
plain `PrismGroup`.

`wrapping()` creates a fresh class on every call. Callers that
need a stable type (e.g. for `isinstance` checks or reuse across
multiple `@click.group` decorators) should assign the result once:

```python
TreeRichGroup = PrismGroup.wrapping(RichGroup)  # assign once, reuse
```

## 3.4.1.4. Manual subclassing

Power users who need full MRO control:

```python
class MyGroup(PrismMixin, RichGroup):
    pass

MyGroup.group_class = MyGroup
```

Both `PrismMixin` and `PrismGroup` are public exports (section 3.4.3).
`PrismGroup` is the primary integration path; `PrismMixin` supports
manual subclassing for composability (section 3.5).
