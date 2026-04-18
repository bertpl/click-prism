# 5.9. Phase 8: Rich theming

**Version:** `0.8.0`
**Goal:** Customizable theming with the two-axis model from section 2.3.2
and R30. Ships the default theme plus at least one additional
built-in theme.

## 5.9.1. Scope

### 5.9.1.1. `TreeTheme` dataclass (`_config.py`)

- `TreeTheme`, `ThemeColumns`, `ThemeRows`, `ColumnStyle`,
  `RowStyle` — **Completes (from phase 1)**: placeholder types
  gain public export, the `built_in()` factory,
  `_fill_from_default()` helper, and the type-system constraints
  that prevent invalid axis combinations (color on rows, bold on
  columns). The dataclass shape itself is unchanged from phase 1 —
  the **five-type hierarchy defined in section 3.1.3** (R30)
  shipped with the phase 1 placeholders:
  `TreeTheme → ThemeColumns → ColumnStyle` and
  `TreeTheme → ThemeRows → RowStyle`. Field names per section
  3.1.3; in particular, the row-type fields on `ThemeRows` are
  `title` (singular — one row) and `groups` / `commands` (plural
  — row categories). The axis labels listed below use R30's
  English category names, not the Python field names.
- Axis categories (from R30):
    - **Vertical axis** (per column): guides, group names,
      command names, description, arguments, options
    - **Horizontal axis** (per row type): title, group, command
- Each axis exposes only the modifiers it owns:
    - Vertical: color + dim
    - Horizontal: bold + italic + dim
- Color is vertical-only (prevented by the type system at
  definition time, not runtime validation)
- Cell style is the composition of both axes
- `dim` merges as OR (vertical OR horizontal)
- Group and command names are separate vertical entries so
  developers can assign different colors to each (useful for
  terminals without bold support)
- Opt-in overrides: developers only specify fields where they
  want to deviate from the default theme

### 5.9.1.2. Default theme

- Already shipped in phase 7 with concrete named-ANSI values and
  bold group rows. This phase does not change `DEFAULT_THEME`
  itself — it adds `_fill_from_default()` so custom themes can
  inherit unset fields from it (section 3.1.3.3).

### 5.9.1.3. Built-in themes (additional)

- `BuiltinTheme` enum and `TreeTheme.built_in()` factory —
  **Completes (from phase 1)**: placeholders replaced by the real
  enum + factory. `TreeTheme.built_in()` raises `PrismError`
  when the name does not resolve to a `BuiltinTheme` value (design
  section 3.1.3.3).
- At least one additional built-in theme using RGB colors
  (example names: "ocean", "forest", "sunset" — pick one or two
  tasteful choices).
- Selected via `TreeConfig(theme=TreeTheme.built_in("ocean"))`,
  where the string is resolved by the `TreeTheme.built_in()`
  factory method through the `BuiltinTheme` enum (section 3.1.3.3).

### 5.9.1.4. Theme portability (R31)

- When `rich` is not installed, `TreeTheme` settings are silently
  ignored
- The same `TreeConfig(theme=TreeTheme(...))` config works in
  both `rich`-present and `rich`-absent environments without
  conditional code

### 5.9.1.5. Configuration — wiring

- `TreeConfig.theme` — custom-value path **Completes (from
  phase 1)**: non-`None` inputs are now handled by
  `_fill_from_default()`. The default-`None` case already returns
  `DEFAULT_THEME` since phase 7 completed the default path.

### 5.9.1.6. Public API additions

- `TreeTheme`, `ThemeColumns`, `ThemeRows`, `ColumnStyle`, `RowStyle`,
  `BuiltinTheme` exported from `click_prism`

### 5.9.1.7. Not in this phase

- No `rich-click` style conversion helper (phase 9 ships
  `tree_theme_from_rich_click()` as an opt-in helper, as part of
  the `rich-click` compatibility work)

## 5.9.2. Pull requests

Suggested split. Each PR ships code **with** its tests and leaves
the repo at 100% coverage.

1. **`TreeTheme` dataclass** — two-axis model (vertical +
   horizontal), type-safe API preventing invalid combinations
   (color on a row is a type error), opt-in override semantics,
   plus unit tests for composition logic (vertical × horizontal
   merging, `dim` OR-merge, custom overrides inheriting from
   default).
2. **Custom theme support + portability** — `_fill_from_default()`
   in `_config.py` (unset fields inherit from `DEFAULT_THEME`),
   plus tests for custom-theme composition, opt-in overrides, and
   theme portability (silent no-op when `rich` is absent — the
   same `TreeConfig` works in both environments).
3. **Built-in theme(s)** — at least one additional RGB-based
   built-in theme, selectable via `TreeTheme` API, plus
   dual-snapshot tests for each built-in theme.

## 5.9.3. Tests

- Theme composition unit tests:
    - Vertical color applied to correct columns
    - Horizontal bold/italic/dim applied to correct row types
    - `dim` merges as OR between axes
    - Invalid combinations (e.g., color on a row) rejected at
      type-checker / dataclass level, not at runtime
- Default theme snapshot test (verifies phase 7's default theme
  still renders correctly after custom-theme plumbing is added)
- Built-in theme snapshot tests (one per built-in theme)
- Custom theme test: developer specifies only a subset of fields,
  others inherit from default
- Unknown built-in theme name:
    - `TreeTheme.built_in("nonexistent")` raises `PrismError`
- `TreeTheme` silently ignored when `rich` absent:
    - Same `TreeConfig` works in both environments
    - No warnings, no errors, output falls back to plain text
- Dual-snapshot helper captures theme differences in the `[ansi]`
  file (plain output is identical across themes)

## 5.9.4. Requirements newly satisfied

| Req | Notes |
|---|---|
| R30 | Two-axis theme model, default + built-in themes, opt-in overrides, type-safe API |
| R31 | Theme portability (same config works with or without `rich`) |

## 5.9.5. Exit criteria

- [ ] `from click_prism import TreeTheme` works
- [ ] Default theme produces bold group rows with named ANSI
  colors
- [ ] At least one additional built-in theme is available and
  renders correctly
- [ ] Custom theme via opt-in overrides works
- [ ] Setting color on a row type is a type error (caught at
  definition time)
- [ ] `TreeTheme.built_in("nonexistent")` raises `PrismError`
- [ ] `TreeConfig(theme=TreeTheme(...))` is silently ignored
  when `rich` is not installed (no errors, no warnings)
- [ ] Theme snapshot tests pass for both plain and ANSI captures
- [ ] Coverage is 100% on merged runs
- [ ] Full release pipeline succeeds for `0.8.0`
