# 5.7. Phase 6: Parameter display

**Version:** `0.6.0`
**Goal:** 4-column layout with Arguments and Options columns
alongside the tree and description. Also wires the `show_hidden`
config field that was default-only in phase 1.

## 5.7.1. Scope

### 5.7.1.1. 4-column layout (shared — lands in plain text)

Per section 3.3.0.2.2, 4-column mode is a pure positional-layout concern
shared across visual renderers. This phase ships it in the plain
text renderer (the only visual renderer that exists at this
point — `rich` lands in phase 7 and will pick up the same layout
primitives for free). Concretely:

- Extend the shared column-layout code (used by
  `_render_plain.py` today, and by `_render_rich.py` from phase 7
  onwards) to optionally show two additional columns:
    - **Arguments** column: fixed max width (e.g., 22 chars)
    - **Options** column: fills remaining terminal width
- Column header row when `show_params=True`, anchored above the
  4 columns (R25 explicitly requires the header)
- Arguments formatted as `UPPERCASE` with `[OPTIONAL]` for
  non-required
- Options formatted as long-form name preferred (`--env`), short
  form only when no long form exists
- `--[no-]flag` syntax for boolean flags
- Respects terminal width; degradation order per section 3.3.0.2.2
  (Options clips first, then Arguments, then Description)
- Re-uses `ParamInfo` from phase 3 for the extracted metadata

### 5.7.1.2. `show_hidden` wiring

- `TreeConfig.show_hidden` filtering has been Active since phase 1
  via `filter_tree()` (section 3.2.5) in visual paths. JSON paths
  skip `filter_tree()` entirely and always include hidden commands.
  This phase adds a `[hidden]` suffix marker in the plain text
  renderer when hidden commands are included, making developer
  configuration of `show_hidden` visually meaningful.
- When `show_hidden=True`, hidden commands are included in the
  tree with a `[hidden]` suffix marker.
- Completes R9: hidden commands can be included (mechanically
  supported since phase 1) and are now visually distinguishable.

### 5.7.1.3. Configuration — wiring

- `TreeConfig.show_params` — **Completes (from phase 1)**; consumed
  by the 4-column renderer (section 5.7.1.1).
- `TreeConfig.show_hidden` — **Completes (from phase 1)** for the
  visual-marker part: filtering was Active since phase 1, and this
  phase adds the `[hidden]` visual marker (section 5.7.1.2) that
  makes developer configuration meaningful.

### 5.7.1.4. Not in this phase

- No `rich` rendering of the new columns. `rich` itself lands in
  phase 7; because the layout primitives are shared, phase 7's
  `rich` renderer will inherit 4-column support automatically —
  it only needs to add styling, not reimplement the layout.

## 5.7.2. Pull requests

Suggested split. Each PR ships code **with** its tests and leaves
the repo at 100% coverage.

1. **4-column layout** — extend `_render_plain.py` with Arguments
   and Options columns, column header row, `show_params` wiring,
   plus snapshot tests for `show_params=True` across all fixtures
   and terminal-width clipping for the Options column.
2. **`show_hidden` wiring** — activate the `TreeConfig.show_hidden`
   field, add visual marker for hidden commands in the renderer,
   plus snapshot tests for `show_hidden=True`/`False` variations.

## 5.7.3. Tests

- Snapshot tests with `show_params=True`:
    - Flat CLI with arguments and options
    - Nested CLI with varying argument counts
    - Terminal width clipping: narrow terminal → Options column
      clipped first
    - Boolean flags: `--verbose`, `--no-verbose`, `--[no-]verbose`
    - Short-form-only options (e.g., `-v`): rendered without long
      form
- `show_hidden` toggle tests:
    - Default (`False`) excludes hidden commands
    - `True` includes them with visual marker
    - Preserves the "default-exclude" behavior from phase 1 for
      existing snapshots
- Coexistence with existing tree-as-help, tree_command,
  `--help-json`

## 5.7.4. Requirements newly satisfied

| Req | Notes |
|---|---|
| R9 | **Completes** — `show_hidden` now a developer-configurable TreeConfig field with visual marker |
| R25 | 4-column parameter display with Arguments and Options columns, header row, developer-controlled |

## 5.7.5. Exit criteria

- [ ] `TreeConfig(show_params=True)` produces a 4-column tree
- [ ] Column header row renders correctly
- [ ] Argument and option formatting matches R25 (uppercase,
  long-form preferred, `--[no-]flag` syntax)
- [ ] Terminal width clipping works (Options column clips first)
- [ ] `TreeConfig(show_hidden=True)` includes hidden commands
  with visual marker
- [ ] Snapshot tests cover all fixture CLIs with both
  `show_params` and `show_hidden` variations
- [ ] Coverage is 100% on merged runs
- [ ] Full release pipeline succeeds for `0.6.0`
