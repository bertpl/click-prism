# 3.4.3. Public API Surface

Definitive answer to "what can a user import from `click_prism`?"
The earlier sections (sections 3.4.1, 3.4.2) describe components bottom-up;
this section assembles them into a stable, versioned contract.

## 3.4.3.1. Canonical public exports

Everything in `__init__.py`. These names are stable and follow
semantic versioning.

```python
# click_prism/__init__.py
from click_prism._config import (
    TreeConfig,
    UNLIMITED,
    TreeTheme,
    ThemeColumns,
    ThemeRows,
    ColumnStyle,
    RowStyle,
    BuiltinTheme,
    tree_theme_from_rich_click,
)
from click_prism._mixin import PrismMixin
from click_prism._group import PrismGroup
from click_prism._exceptions import PrismError
from click_prism._command import tree_command
from click_prism._show import show_tree, render_tree
```

| Name | Kind | Defined in |
|---|---|---|
| `TreeConfig` | dataclass | section 3.1.1 |
| `UNLIMITED` | constant | section 3.1.1 |
| `show_tree()` | function | section 3.4.2.4.1 |
| `render_tree()` | function | section 3.4.2.4.2 |
| `PrismError` | exception | section 3.4.1 |
| `PrismGroup` | class | section 3.4.1.2 |
| `tree_command()` | function | section 3.4.2.3 |
| `TreeTheme` | dataclass | section 3.1.3 |
| `ThemeColumns` | dataclass | section 3.1.3 |
| `ThemeRows` | dataclass | section 3.1.3 |
| `ColumnStyle` | dataclass | section 3.1.3 |
| `RowStyle` | dataclass | section 3.1.3 |
| `BuiltinTheme` | StrEnum | section 3.1.3 |
| `PrismMixin` | class | section 3.4.1.1 |
| `tree_theme_from_rich_click()` | function | section 3.5.4 |

## 3.4.3.2. Private names — not exported

These are internal. They may change at any minor or patch version
with no deprecation notice.

| Name | Why private |
|---|---|
| `build_tree()` | Internal model builder. Use `render_tree()` for string output. |
| `render()` | Internal dispatcher. Use `render_tree()` or `show_tree()`. |
| `_effective_config_for()` | Internal config helper (section 3.4.2.1.2). |
| `filter_tree()` | Internal post-build filter (section 3.2.5). Visual paths call it; JSON paths skip it. |
| `_resolve_tree_help()` | Internal `PrismMixin` method (section 3.4.2.1.1). |
| `_compat` module | Internal compatibility layer (section 3.0). |
| `_exceptions` module | Internal; `PrismError` is re-exported from root. |
| `TreeNode` | Internal model dataclass. Not part of the public contract. |

Do not import from `click_prism._*` modules directly. Import only
from the `click_prism` root package.

## 3.4.3.3. Stability guarantees

Everything listed in section 3.4.3.1 follows semantic versioning:

- **Breaking changes** (rename, removal, signature change) require a
  major version bump.
- **Additions** may ship in any minor version.
- **Bug fixes** ship in patch versions.

Private names (underscore-prefixed modules and functions) carry no
stability guarantee and may change at any version.

`TreeNode` and `build_tree()` are explicitly **not** public — do not
depend on them. `render_tree()` is the supported string-output
interface; `show_tree()` is the supported stdout interface. Both
are stable from their first release.
