# 5.8. Phase 7: Rich rendering

**Version:** `0.7.0`
**Goal:** Ship `rich` as an optional extra. Auto-detect availability,
render bold group rows, adapt to terminal capabilities, fall back
gracefully when `rich` is absent.

## 5.8.1. Scope

### 5.8.1.1. `rich` availability detection (`_compat.py`)

- `_should_use_rich() -> bool` (section 3.0.4) — newly introduced
  **Active**. Added to `_compat.py` alongside phase 1's
  `_detect_charset()`. Single import attempt, result cached for
  the process lifetime; checks both `rich` importability and TTY
  status.
- Used by renderer selection, tree-as-help rendering, and
  `show_tree()`.

### 5.8.1.2. `rich` renderer (`_render_rich.py`)

- `RichRenderer` — newly introduced (**Active** when `rich` is
  importable and stdout is a TTY). Reuses `PlainRenderer`'s
  `_build_prefix` and two-pass algorithm; `rich` is used only
  as a styling layer — text segments are wrapped in
  `rich.text.Text` with `Style` objects before
  `Console.capture()` produces the ANSI string. Tree structure
  is identical to plain output.
- Bold group rows across all columns (R29)
- Markers per section 3.3.0.3: hidden commands rendered dim, deprecated
  commands rendered with strikethrough, error nodes rendered in red
- `DEFAULT_THEME` in `_config.py` — **Completes (from phase 1)**:
  concrete named-ANSI values (section 3.1.3.2) replace the phase 1
  placeholder. `_resolve_theme(None)` returns it. `RichRenderer`
  reads from `config.theme` (already resolved by this point), so
  no hardcoded styles in the renderer itself.
- `TreeConfig.theme` — default path **Completes (from phase 1)**:
  `None` resolves to `DEFAULT_THEME`. Developer-supplied non-`None`
  `TreeTheme` values remain deferred — phase 8's
  `_fill_from_default()` lands the custom-theme inheritance logic.
- Terminal adaptation via `Console` configuration:
    - Respects terminal width, TTY detection, `NO_COLOR`
    - Handles truecolor / 256 / 8-bit color systems
- `Console.capture()` path for string output (used by
  `format_commands()` in tree-as-help mode and by `show_tree()`)

### 5.8.1.3. Renderer selection

- `select_renderer()` — newly introduced **Active**. Factors out
  the renderer dispatch that up to this point lived inline in
  `render_tree` / `show_tree`. Routes `format="json"` to
  `JsonRenderer`, and `format="text"` to `RichRenderer` when
  `_should_use_rich()` is true, otherwise to `PlainRenderer`.
- When `rich` is installed and stdout is a TTY: `rich` renderer.
- When `rich` is not installed OR stdout is not a TTY: plain
  text renderer.
- Selection is automatic — no end-user flag, no developer
  override. This matches section 3.3's `select_renderer()` contract
  ("the developer does not choose a renderer").

### 5.8.1.4. Optional dependency

- `rich>=13.0` is in `[project.optional-dependencies].rich`
  (section 4.1). No code change needed — `rich` is imported lazily at
  render time and guarded by `_should_use_rich()`.

### 5.8.1.5. ANSI safety validation

The design (section 3.3.0.0.3) flags a risk: `formatter.write()` may mangle
ANSI codes from `RichRenderer` through Click's wrapping or dedenting.
This phase validates whether this occurs in tree-as-help mode. If
mangling is confirmed, the fix is to bypass `formatter.write()` and
write directly to stdout for the tree portion. The chosen approach
must be documented back into section 3.3.0.0.3.

### 5.8.1.6. CI matrix changes

Per section 4.3.3, this phase adds three tier 2 `rich` variation jobs to
`_unit_tests.yml`: `rich: "13.0"`, `rich: "latest"`, and
`(python: "3.10", click: "8.0", rich: "latest")`. These are the
first matrix jobs that exercise the `rich` renderer with version
boundaries.

### 5.8.1.7. Not in this phase

- No custom `TreeTheme` overrides — `_fill_from_default()` and
  opt-in field inheritance land in phase 8
- No `TreeTheme.built_in()` / `BuiltinTheme` enum — built-in
  theme catalog is phase 8
- No `rich-click` style conversion helper (phase 9 —
  composability)

## 5.8.2. Pull requests

Suggested split. Each PR ships code **with** its tests and leaves
the repo at 100% coverage.

1. **`rich` availability detection** — `_compat.py` with lazy-cached
   `_should_use_rich()` helper, plus tests for both `rich`-present and
   `rich`-absent (via mocked import failure) cases.
2. **`rich` renderer + default theme** — `DEFAULT_THEME` concrete
   values in `_config.py` (section 3.1.3.2); `_render_rich.py` with bold
   group rows, columnar layout, `Console.capture()` path;
   `assert_rich_snapshot` test helper (section 4.3.6); plus dual-snapshot
   tests for every existing fixture in `rich` mode and terminal
   adaptation tests (`NO_COLOR`, width).
3. **Renderer selection wiring** — hook `select_renderer()` (section 3.3)
   up so it picks the `rich` renderer when `rich` is available and
   stdout is a TTY, and the plain renderer otherwise. Tests cover
   both branches of the selection logic.

## 5.8.3. Tests

- `assert_rich_snapshot` helper from section 4.3.6: every `rich`-involving
  test captures both plain and ANSI versions per snapshot
- `rich` present:
    - Auto-detected, `rich` renderer used
    - Bold group rows in the ANSI snapshot
    - Columnar layout preserved
    - Tree-as-help mode renders `rich` output into Click's formatter
- `rich` absent (mocked import failure):
    - Falls back to plain text renderer
    - No warnings, no errors
    - Same semantic output as phase 1–6 plain rendering
- Terminal adaptation:
    - `NO_COLOR=1` strips colors (delegated to `rich`'s Console)
    - `color_system="256"` vs `"truecolor"`
    - Width constraint honored
- The existing test matrix (section 4.3.3) already runs the "`rich`: none /
  13.0 / latest" dimension — these tests execute in the full
  matrix for the first time in phase 7

## 5.8.4. Requirements newly satisfied

| Req | Notes |
|---|---|
| R26 | `rich` auto-detection, no code changes required |
| R27 | Graceful absence: plain Unicode output when `rich` is not installed |
| R28 | Terminal adaptation (color system, width, TTY, `NO_COLOR`) |
| R29 | Bold group rows across all columns |

## 5.8.5. Exit criteria

- [ ] `pip install click-prism[rich]` installs `rich` as an extra
- [ ] With `rich` installed, `show_tree(cli)` produces bold-styled
  output
- [ ] Without `rich` installed, `show_tree(cli)` produces plain
  Unicode output with no errors or warnings
- [ ] Tree-as-help mode produces `rich` output when `rich` is
  installed
- [ ] Validated that `formatter.write()` does not mangle ANSI codes
  in tree-as-help output; if mangling is confirmed, the bypass
  approach is implemented and documented back into section 3.3.0.0.3
- [ ] `NO_COLOR=1` environment variable is honored
- [ ] The section 4.3.5 coverage target produces a fully-populated
  `.coverage` across runs 1 (no `rich`) and 2 (with `rich`) —
  this was already the intent, now it actually exercises the
  `rich` path
- [ ] All `assert_rich_snapshot` tests pass for both plain and
  ANSI variants
- [ ] Coverage is 100% on merged runs
- [ ] Full release pipeline succeeds for `0.7.0`
