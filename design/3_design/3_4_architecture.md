# 3.4. Architecture & Integration

How `click-prism` hooks into Click. The class hierarchy enables all
three integration paths (section 2.3.1):

| Path | What it needs | What it provides |
|---|---|---|
| `cls=PrismGroup` | PrismMixin, PrismGroup | Tree-as-help, `--help-json`, child inheritance |
| `tree_command()` | Any Group | Tree subcommand with `--depth` |
| `show_tree()` / `render_tree()` | Standalone | Inspect tree from Python — print to stdout or return as string, no CLI modification |

## 3.4.0. Preamble

### 3.4.0.1. Sub-sections

- [3.4.1. Class Architecture](3_4_1_class_architecture.md) — PrismMixin,
  PrismGroup, `wrapping()`, MRO
- [3.4.2. Integration Points](3_4_2_integration_points.md) — tree-as-help,
  `--help-json`, `tree_command()`, `show_tree()` / `render_tree()`
- [3.4.3. Public API Surface](3_4_3_public_api.md) — canonical exports,
  private names, stability guarantees
