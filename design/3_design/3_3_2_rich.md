# 3.3.2. Rendering: Rich

What changes when `rich` is available. Styling is additive — the
structural layout is identical to plain text (section 3.3.1).

## 3.3.2.1. RichRenderer

```python
class RichRenderer(Renderer):
    def __init__(self, config: TreeConfig) -> None:
        self._config = config
        self._theme = config.theme  # already a TreeTheme after resolve()

    def render(self, tree: TreeNode) -> str:
        # Reuses PlainRenderer's _build_prefix and two-pass algorithm.
        # Text segments are wrapped in rich.text.Text with Style objects
        # (colors, bold, dim, strikethrough) before Console.capture()
        # produces the ANSI string. Tree structure is byte-for-byte
        # identical to plain text output. See sections 3.3.2.3 and 3.3.2.4.
        ...
```

`RichRenderer` mirrors `PlainRenderer`'s shape: holds the resolved
`TreeConfig` (and the resolved `TreeTheme`), and `render()` returns
a `str`. The difference is that the returned string contains ANSI
escape codes — the caller still decides where it goes. `rich` is
imported inside `_render_rich.py` (lazy) so `import click_prism` has
no `rich` cost when `rich` isn't installed.

## 3.3.2.2. Auto-detection

`rich` rendering activates when both hold:

1. `rich` is importable (`_compat`, section 3.0.4)
2. stdout is a TTY

Otherwise falls back to plain text. No errors, no warnings.
`NO_COLOR` is not checked by `click-prism` — `rich`'s Console handles
it internally (stripping colors while preserving bold/dim/italic).

## 3.3.2.3. Console

Created at render time:

```python
console = Console(width=terminal_width, highlight=False)
```

The renderer captures to a string, matching the `Renderer` ABC
(section 3.3):

```python
with console.capture() as capture:
    console.print(styled_output)
return capture.get()
```

The returned string contains ANSI escape codes that the terminal
interprets. The caller decides where it goes — `click.echo()` for
the tree subcommand and `show_tree()`, `formatter.write()` for
tree-as-help.

Risk for the `formatter.write()` path: Click's formatter may
mangle ANSI codes through wrapping or dedenting — validated during
implementation; fallback is direct stdout write for the tree
portion.

## 3.3.2.4. Theme application

Each cell's `rich` `Style` is composed from its column style and
row style (section 3.1):

```python
def _cell_style(col: ColumnStyle, row: RowStyle) -> Style:
    return Style(
        color=col.color,
        bold=row.bold or False,
        italic=row.italic or False,
        dim=(col.dim or False) or (row.dim or False),
    )
```

### 3.3.2.4.1. Bold group rows

Default theme sets `rows.groups.bold = True`. Every cell in a
group row is bold across all columns — the key visual cue for
hierarchy in columnar layout.

## 3.3.2.5. Graceful degradation

Handled by `rich`'s Console — `click-prism` does not implement terminal
detection.

| Condition | Behavior |
|---|---|
| TTY + truecolor | Full styling |
| TTY + 256-color | Closest palette matches |
| TTY + `NO_COLOR` | Bold/dim/italic preserved, colors stripped |
| Piped | Falls back to plain text renderer |
