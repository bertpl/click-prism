# 3.0. Design Overview

> This section translates the requirements from section 2.3.4 (R1–R41) into
> concrete technical design decisions.

## 3.0.1. Scope and approach

**Final state.** All requirements implemented. Phasing is section 5's
concern.

**Critical decisions only.** Python patterns, data structures, and
APIs where a wrong choice would be expensive to reverse. No prose
where a code block suffices; no explanation where the code is
self-evident. If it doesn't need to be pinned down to avoid a costly
mistake, it doesn't belong here.

**Shipping code only.** CI/CD, test infrastructure, and documentation
tooling are defined in section 4 (Infrastructure Design).

## 3.0.2. Contents

Section 3 defines:

- The configuration data model that parameterizes all behavior (section 3.1)
- The intermediate tree representation and traversal algorithm (section 3.2)
- How tree data becomes output: plain text, `rich`, and JSON (section 3.3)
- The class architecture and how it hooks into Click (section 3.4)
- How `click-prism` coexists with the Click ecosystem (section 3.5)

## 3.0.3. Package identity

| Field | Value |
|---|---|
| PyPI name | `click-prism` |
| Import name | `click_prism` |
| License | BSD-3-Clause |

BSD-3-Clause aligns with Click and the Pallets ecosystem (Flask,
Werkzeug, Jinja). `rich` uses MIT. Both are permissive and compatible —
the choice is ecosystem consistency with our primary dependency.

## 3.0.4. Module layout

```
click_prism/
├── __init__.py          # Public API exports
├── _compat.py           # Environment detection (Rich availability, cached)
├── _exceptions.py       # PrismError
├── _config.py           # TreeConfig, TreeTheme, style types
├── _model.py            # TreeNode, traversal
├── _params.py           # ParamInfo, parameter extraction
├── _render_plain.py     # Plain text renderer (Unicode/ASCII)
├── _render_rich.py      # Rich renderer (conditional import)
├── _render_json.py      # JSON renderer
├── _mixin.py            # PrismMixin
├── _group.py            # PrismGroup, wrapping()
├── _command.py          # tree_command() factory
├── _show.py             # show_tree(), render_tree() standalone functions
└── py.typed             # PEP 561 marker
```

Shared rendering helpers (e.g., `_build_prefix`, two-pass width
calculation) live in `_render_plain.py` and are imported by
`_render_rich.py`.

Internal modules are prefixed with `_` — the public API is exclusively
through `__init__.py` exports. This keeps the internal structure free
to evolve without breaking importers. The canonical list of public
exports and private names is in section 3.4.3.

`_compat.py` provides two environment-detection helpers:

- `_should_use_rich() -> bool` — returns `True` when `rich` is
  importable **and** stdout is a TTY. Used by `select_renderer()`
  (section 3.3) to choose between `RichRenderer` and `PlainRenderer`.
  The `rich` availability check is lazy-cached — it runs once on
  first access and subsequent calls return the cached result.
  Tests mock this single function rather than patching individual
  checks.

- `_detect_charset() -> Literal["unicode", "ascii"]` — attempts
  `"╰".encode(sys.stdout.encoding or "ascii")`; success returns
  `"unicode"`, `UnicodeEncodeError` or `LookupError` returns
  `"ascii"`. Used by `TreeConfig.resolve()` when `charset=None`
  (section 2.2.2).

## 3.0.5. Dependency declarations

| Dependency | Version | Type |
|---|---|---|
| `click` | >=8.0 | Required |
| `rich` | >=13.0 | Optional extra (`pip install click-prism[rich]`) |

No other runtime dependencies. `rich` is imported lazily at render time —
it is never imported at module level, so `import click_prism` has zero
import-time cost beyond Click.

## 3.0.6. Project standards

- **Test coverage**: 100% line coverage
- **Type annotations**: written for IDE support and consumers (no
  type checker in CI — see section 4.2.2)
- **Formatting and linting**: `ruff`
- **Pre-commit hooks**: enforced locally and in CI
- **Test matrix**: Python versions (3.10–3.14), Click versions
  (8.0, 8.1, 8.2, 8.3), dependency combinations (with/without `rich`,
  with/without neighbor packages)

## 3.0.7. Requirements traceability

Every requirement from section 2.3.4 is addressed in this section:

| Section | Requirements |
|---|---|
| 3.0 Overview (this doc) | R41 (invariant — satisfied by the module layout: internal-prefix modules, lazy `rich` import, no module-level mutable state) |
| 3.1 Configuration | R22–R25, R30–R31 |
| 3.2 Tree Model | R6, R9–R11, R38–R40 |
| 3.3 Rendering | R7–R8, R12, R25–R29 |
| 3.4 Architecture & Integration | R1–R5, R13–R21, R23 |
| 3.5 Composability | R32–R37 |

R25 (parameter display) spans two sections: section 3.1 defines the
configuration field, section 3.3 defines the column layout.

## 3.0.8. Sub-sections

- [3.1. Configuration](3_1_configuration.md)
- [3.2. Tree Model](3_2_tree_model.md)
- [3.3. Rendering](3_3_rendering.md)
    - [3.3.1. Plain Text](3_3_1_plain_text.md)
    - [3.3.2. Rich](3_3_2_rich.md)
    - [3.3.3. JSON](3_3_3_json.md)
- [3.4. Architecture & Integration](3_4_architecture.md)
    - [3.4.1. Class Architecture](3_4_1_class_architecture.md)
    - [3.4.2. Integration Points](3_4_2_integration_points.md)
    - [3.4.3. Public API Surface](3_4_3_public_api.md)
- [3.5. Composability](3_5_composability.md)
