# 5.2. Phase 1: Standalone rendering

**Version:** `0.1.0`
**Goal:** First "real" release. Ships the rendering engine as a
standalone API, with no Click integration beyond reading group
structure.

## 5.2.1. Scope

### 5.2.1.1. Tree model (`_model.py`)

- `TreeNode` dataclass (section 3.2), with all fields present. Field
  states:
    - `params` — **Partial (→ phase 3: real populator)**; empty
      list this phase, populated via the inline stub below
    - `aliases`, `is_default`, `section_name` — **Partial
      (→ phase 9: renderer consumption)**; populated from this
      phase onward by the discovery functions below, but no
      renderer reads them yet
    - All other fields — **Active**
- `_build_child()` — **Active**; follows the algorithm structure
  from section 3.2.2. Call-site states:
    - `_extract_params()` — **Partial (→ phase 3: real
      implementation in `_params.py`)**; inline stub returning
      `[]` this phase
    - `_discover_aliases()`, `_discover_default()`,
      `_discover_section()` — **Active**, duck-typed (return
      defaults when neighbor packages are absent)
- Recursive traversal via `list_commands()` / `get_command()`
- `filter_tree()` / `_filter_node()` (section 3.2.5) — **Active**
- Error handling: `TreeNode` with an `error_message` field for
  commands that fail to load, return `None`, or form circular
  references (no crashes, no silent drops)
- Support for lazy-loading groups

### 5.2.1.2. Plain text renderer (`_render_plain.py`)

- `Renderer` abstract base class (section 3.3.0.1) — **Active**:
  defined in `_render_plain.py` alongside `PlainRenderer`, which
  inherits from it. Phase 3's `JsonRenderer` and phase 7's
  `RichRenderer` inherit from the same ABC; phase 7 factors out
  the `select_renderer()` dispatcher that up to that point lives
  inline in `_show.py`.
- Unicode charset with rounded arc corners (default)
- ASCII fallback charset
- Auto-charset default: when `charset=None`, `_detect_charset()` (from
  `_compat`) selects `"unicode"` or `"ascii"` based on whether
  `sys.stdout.encoding` can represent box-drawing characters; an
  explicit `charset="unicode"` is never overridden (section 2.2.2.1)
- `_compat.py` is created in this phase with `_detect_charset()`
  (section 3.0.4); `_should_use_rich()` is added in phase 7 (section 5.8)
- Root label uses `ctx.command_path` (section 3.3.0.2.5) — shows the full
  command path for subtrees; for `show_tree()`'s synthetic context
  this is just the group name
- Columnar layout: tree chrome + name in column 1, description in
  column 2, aligned to the widest entry
- Terminal-width-aware sizing via `shutil.get_terminal_size()`
- Description clipping with `...` when terminal is too narrow
- Hidden commands excluded by default
- Deprecated commands shown with a `[deprecated]` suffix
- Error nodes rendered with a visible indicator

### 5.2.1.3. Configuration (`_config.py`)

- `TreeConfig` dataclass with all fields defined per section 3.1.
  Field states:
    - `charset`, `depth` — **Active**.
    - `show_hidden` — **Partial (→ phase 6: `[hidden]` visual
      marker)**. Filtering via `filter_tree()` is Active in this
      phase (visual paths exclude by default; standalone paths
      seed `show_hidden=True`); only the visual marker on
      included hidden commands is deferred.
    - `tree_help` — **Partial (→ phase 2: first consumer is
      `PrismMixin`)**.
    - `show_params` — **Partial (→ phase 6: 4-column layout
      consumer)**.
    - `theme` — **Partial (→ phase 7: default-path consumption;
      → phase 8: custom-value-path consumption)**.
- Placeholder type definitions — the five-type hierarchy
  (`TreeTheme`, `ThemeColumns`, `ThemeRows`, `ColumnStyle`,
  `RowStyle`) ships with the full field structure defined in
  section 3.1.3, but without the `built_in()` factory,
  `_fill_from_default()` helper, `BuiltinTheme` enum, public
  exports, or the type-system constraints that prevent invalid
  axis combinations (color on rows, bold on columns):
    - `TreeTheme`, `ThemeColumns`, `ThemeRows`, `ColumnStyle`,
      `RowStyle`, `BuiltinTheme` — **Partial (→ phase 8:
      `built_in()` factory, `BuiltinTheme` enum,
      `_fill_from_default()` helper, public exports, type-system
      axis constraints)**.
    - `DEFAULT_THEME` — **Partial (→ phase 7: concrete
      named-ANSI values)**.
    - `ParamInfo` — **Partial (→ phase 3: real dataclass
      relocates to `_params.py`; `_model.py`'s import switches
      accordingly)**.
- `.resolve()` method with default values — **Active**.
- `.merge(base)` method for overlaying one config onto another
  (needed by `render_tree()` to overlay user-supplied config onto
  the standalone `show_hidden=True` default — see section 3.4.2.4.2) —
  **Active**.

### 5.2.1.4. Exceptions (`_exceptions.py`)

- `PrismError(click.ClickException)` — the single exception
  type `click-prism` introduces (section 3.4.1)
- Defined and exported here so the public API surface is stable
  from `0.1.0` onwards. Raised by `resolve()` for invalid depth
  values (section 3.1.1.1); also used by the name-collision check that
  lands in phase 4.

### 5.2.1.5. Invariant enforcement (R41)

Phase 1 lands the test suite that enforces R41 ("no import-time
side effects, no module-level mutable state") as an invariant.
The tests live alongside the unit tests and stay green through
every subsequent phase:

- **Subprocess import test**: `python -c "import click_prism"` in
  a clean subprocess produces empty stdout and empty stderr,
  exit code 0.
- **No optional-dependency imports at import time**: after
  `import click_prism`, `sys.modules` must not contain `rich`
  (and other optional deps) unless they were imported before
  `click_prism`.
- **No module-level mutable state**: a walk of `click_prism`'s
  module dict asserts no module-level mutable containers
  (`list`, `dict`, `set`) that are meant to be mutated —
  read-only constants, functions, classes, and type aliases
  are fine.

These tests are trivial to write on a near-empty package in
phase 1 and grow more meaningful as later phases add code. They
are also the enforcement mechanism for the "Predictable
behavior" principle from section 2.2.1.

### 5.2.1.6. Public API

- `render_tree(cli, *, config=None, format="text") -> str` —
  returns the rendered tree string; second entry point on
  integration path 3 (section 3.4.2.4). The `format` parameter accepts
  `Literal["text", "json"]`; only `"text"` is functional in this
  phase — **Partial (→ phase 3: `format="json"` branch wires the
  JSON path; `"json"` raises `PrismError` until then)**.
- `show_tree(cli, *, config=None, format="text") -> None` — thin
  wrapper around `render_tree`, writes the result via `click.echo`;
  first entry point on integration path 3. Shares the `format`
  parameter's **Partial (→ phase 3: `format="json"` branch)**
  state with `render_tree`.
- Both functions are implemented in `_show.py` (section 3.0.4) and
  re-exported from `__init__.py`
- `TreeConfig`, `UNLIMITED`, `PrismError` — public
  data/constant/exception types
- `build_tree` and `TreeNode` stay internal (not exported from
  `__init__.py`) — the tree model shape is free to evolve in
  later phases

The canonical public API surface and private names are in section 3.4.3.

### 5.2.1.7. Not in this phase

- No `PrismGroup`, no `tree_command()`, no `--help-json`
- No PrismMixin
- No `rich`
- No parameter display columns
- No developer-configurable `show_hidden` yet — `filter_tree()`
  (section 3.2.5) handles hidden-command exclusion in visual paths;
  `render_tree()` / `show_tree()` include hidden commands by
  default by seeding `show_hidden=True` (R4 satisfied); JSON
  paths skip `filter_tree()` entirely. Developer-configurable
  `show_hidden` through `tree_config=` on a group wires in phase 6

## 5.2.2. Pull requests

Suggested split. Each PR ships code **with** its tests and leaves
the repo at 100% coverage.

1. **Tree model + TreeConfig** — `_model.py` (`TreeNode`,
   `build_tree` with error handling), `_compat.py`
   (`_detect_charset()`), `_config.py` (`TreeConfig` dataclass with
   all fields defined + `.resolve()` + `.merge()`), plus unit tests
   for traversal, error nodes, lazy groups, config resolution, and
   merge semantics (plain assertions — no snapshot infra needed
   yet).
2. **Plain text renderer + snapshot infrastructure** —
   `_render_plain.py` (unicode + ASCII styles, columnar layout,
   terminal width, clipping), `tests/conftest.py` fixtures,
   `syrupy` + `TextSnapshotExtension` setup (section 4.3.6), and the full
   snapshot test suite for the renderer (all fixtures × styles,
   error nodes, clipping).
3. **Public API** — `_show.py` (`render_tree`, `show_tree` —
   section 3.0.4), `__init__.py` re-exports (`render_tree`, `show_tree`,
   `TreeConfig`, `UNLIMITED`, `PrismError`), plus integration
   tests exercising the public API surface end-to-end.

## 5.2.3. Tests

- Fixtures (section 4.3.2): `flat_cli`, `nested_cli`, `deep_cli`, `empty_cli`
- Traversal unit tests including lazy groups
- Error node tests: `get_command` returning `None`,
  `get_command` raising, circular references
- Snapshot tests (section 4.3.6, `assert_rich_snapshot` not yet needed —
  plain text only) for:
    - Unicode charset
    - ASCII charset
    - Columnar alignment with varying tree widths
    - Error nodes
    - Deep nesting
    - Empty groups
    - Terminal width clipping
- Coverage sanity (the `make coverage` 4-run sequence will work
  here: run 1 is the only one with meaningful content; runs 2, 3,
  and 4 just exercise the same code paths since `rich`, `rich-click`,
  and the ecosystem packages don't affect anything yet)

## 5.2.4. Requirements newly satisfied

| Req | Notes |
|---|---|
| R4 | **Partial** — rendering + stdout path. JSON format path lands in phase 3. |
| R6 | Hierarchy display with box-drawing characters |
| R7 | Unicode (rounded arcs) + ASCII styles |
| R8 | Columnar layout |
| R9 | **Partial** — `render_tree()` / `show_tree()` include hidden commands by default (section 3.4.2.4); tree-as-help path excludes hidden. Developer-configurable `show_hidden` on groups wires in phase 6. |
| R10 | Deprecated commands shown with marker |
| R11 | Error nodes |
| R12 | Terminal width respected |
| R38 | Lazy groups (traversal uses `list_commands`/`get_command`) |
| R39 | Large CLIs (no structural limits; depth limiting is the management mechanism — phase 4 adds runtime override) |
| R40 | Graceful failure |
| R41 | Predictable behavior invariant (import-time side effects, module-level state) — enforcement test lands here and stays green through subsequent phases |

## 5.2.5. Exit criteria

- [ ] `from click_prism import show_tree, render_tree, TreeConfig,
  UNLIMITED, PrismError` works
- [ ] All snapshot tests pass (snapshot infra lands in PR 2 —
  PR 1 uses plain assertions and has no snapshots to run yet; the
  criterion applies once PR 2 is merged)
- [ ] Coverage is 100% on merged runs
- [ ] `show_tree(some_cli)` prints a correct tree to stdout for
  every fixture
- [ ] Full release pipeline (phase 0) succeeds for `0.1.0`
- [ ] All `0.0.x` releases yanked from PyPI
