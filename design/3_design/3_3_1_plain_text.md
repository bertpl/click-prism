# 3.3.1. Rendering: Plain Text

Unstyled output using box-drawing characters. Used when `rich` is
absent or stdout is not a TTY.

## 3.3.1.1. PlainRenderer

```python
class PlainRenderer(Renderer):
    def __init__(self, config: TreeConfig) -> None:
        self._config = config
        self._chars = UNICODE if config.style == "unicode" else ASCII

    def render(self, tree: TreeNode) -> str:
        # Two-pass: width pass then render pass (see section 3.3.1.4).
        ...
```

`PlainRenderer` holds the resolved `TreeConfig` and the selected
`CharSet` (below). `render()` is a plain `str` producer — no ANSI
codes, no stdout writes. Callers decide where the string goes.

## 3.3.1.2. Character sets

```python
@dataclass(frozen=True)
class CharSet:
    branch: str
    last_branch: str
    vertical: str
    space: str

UNICODE = CharSet(
    branch="├── ",
    last_branch="╰── ",
    vertical="│   ",
    space="    ",
)

ASCII = CharSet(
    branch="|-- ",
    last_branch="+-- ",
    vertical="|   ",
    space="    ",
)
```

Selected by `TreeConfig.charset` (section 3.1).

## 3.3.1.3. Tree prefix construction

Shared with `RichRenderer` — both renderers call `_build_prefix`
identically. `rich` adds `Style` objects to the surrounding text
segments; the prefix characters themselves are always plain.

Each node's prefix is built from its ancestry:

```python
def _build_prefix(
    ancestors: list[bool], is_last: bool, chars: CharSet
) -> str:
    parts = [
        chars.space if was_last else chars.vertical
        for was_last in ancestors
    ]
    parts.append(chars.last_branch if is_last else chars.branch)
    return "".join(parts)
```

`ancestors` tracks whether each ancestor was the last child at
its level — determines whether to draw a vertical guide or a
blank space.

## 3.3.1.4. Rendering

Two-pass over the `TreeNode` tree (section 3.2):

1. **Width pass**: compute max `len(prefix + name)` across all
   visible nodes. Sets column 0 width.
2. **Render pass**: for each node, emit
   `prefix + name + padding + description` (plus argument/option
   columns in 4-column mode, section 3.3).

Output is a plain string — no ANSI codes. Identical whether
displayed in a terminal or captured to a file.

### 3.3.1.4.1. Section headings

When `cloup` section metadata is present (section 3.2), section names are
rendered as indented non-tree lines:

```
projex
  Infrastructure:
  ├── config         Manage configuration settings
  ╰── deploy         Deployment commands
  Info:
  ╰── status         Show current project status
```

Section headings don't get branch glyphs — they are structural
labels, not tree nodes.
