# 5.10. Phase 9: Composability

**Version:** `0.9.0`
**Goal:** Ship the public `PrismMixin` and `PrismGroup.wrapping()`
factory. Integrate and test against the full ecosystem of Click
Group subclasses.

## 5.10.1. Scope

### 5.10.1.1. Public `PrismMixin` (`_mixin.py`)

- `PrismMixin` — **Completes (from phase 2)**: now a public
  export (was internal in phases 2–8).
- All tree behavior continues to live in the mixin; `PrismGroup`
  is just `PrismMixin + click.Group`.
- Existing cooperative `super()` calls (already in place since
  phase 2) are verified to correctly delegate to the next class
  in MRO, not hardwired to `click.Group`.

### 5.10.1.2. `PrismGroup.wrapping()` factory (`_group.py`)

- `PrismGroup.wrapping(base_class: type[click.Group])` — newly
  introduced (**Active**). Classmethod creating a new class with
  MRO `PrismMixin → base_class → click.Group`.
- Sets `group_class = <combined class>` so child groups inherit
  the combined class (not plain `PrismGroup`).
- Optimization: `wrapping(click.Group)` returns `PrismGroup` itself.
- Dynamically-named class: `Tree<BaseClassName>` (e.g.,
  `TreeRichGroup`, `TreeCloupGroup`).

### 5.10.1.3. `tree_theme_from_rich_click()` helper (`_config.py`)

Implements the conversion helper specified in section 3.5.4:

- Accepts a `RichHelpConfiguration` instance (duck-typed — no
  `rich-click` import at module level)
- Reads style fields from `config` via `getattr`; maps the
  overlapping subset to the corresponding `TreeTheme` columns
  and rows
- Exact field mapping decided during implementation
- Returns a `TreeTheme`; unknown or missing fields are silently
  skipped — the function never raises
- Developer opts in explicitly: `TreeConfig(theme=tree_theme_from_rich_click(rc_cfg))`

### 5.10.1.4. Ecosystem integration

Each of the following packages is tested via both integration
paths:

1. `PrismGroup.wrapping(SubclassGroup)` — full mixin combination
2. `cli.add_command(tree_command())` on an unmodified subclass
   instance (the subcommand-only fallback, R37)

Target packages (R32):

- `rich-click` — `RichGroup`
- `cloup` — `Group`
- `click-extra` — `ExtraGroup`
- `click-help-colors` — `HelpColorsGroup`
- `click-didyoumean` — `DYMGroup`
- `click-default-group` — `DefaultGroup`
- `click-aliases` — `ClickAliasedGroup`

### 5.10.1.5. Renderer extensions for neighbor metadata (`_render_plain.py`, `_render_rich.py`)

`TreeNode.section_name`, `TreeNode.is_default`, `TreeNode.aliases`
— **Completes (from phase 1)**: the fields have existed and been
populated (via duck-typed discovery) since phase 1, and are
consumed by the visual renderers (plain text and rich) here for
the first time — JSON has emitted them since phase 3 per section
3.3.3.1. `_render_plain.py` and `_render_rich.py` are extended to
emit:

- **Section headings** (section 3.3.1.4.1): when `section_name` is
  present, children are grouped by `section_name`, and an indented
  heading line without branch glyphs is emitted above each
  section's commands. This is the first phase where any child has
  a non-`None` `section_name` (discovery was already Active in
  phase 1; only `cloup` / `cloup`-based `ExtraGroup` populate it in
  practice).
- **Default command marker**: `*` suffix when `is_default` is
  true (follows the existing `[deprecated]` suffix pattern).
- **Alias display**: aliases shown in parentheses next to the
  command name when `aliases` is non-empty (follows the existing
  suffix pattern).

### 5.10.1.6. Information preservation (R35)

Tree output preserves information from combined packages:

- **`cloup` sections**: group labels preserved as section headings
  in the tree (section 5.10.1.5)
- **Default command markers**: `*` marker from
  `click-default-group` shown on the default command (section 5.10.1.5)
- **Command aliases**: aliases from `click-aliases` shown in
  parentheses next to the command name (section 5.10.1.5)

### 5.10.1.7. Documentation for manual MRO stacking

- Brief section in user docs explaining multi-plugin combinations
  (R36): how to manually create a class like
  `class MyGroup(PrismMixin, RichGroup, DYMGroup): pass`
- No ergonomic API for this case — the doc is the "API"

### 5.10.1.8. Public API additions

- `PrismMixin` exported from `click_prism`
- `PrismGroup.wrapping` available
- `tree_theme_from_rich_click` exported from `click_prism`

### 5.10.1.9. CI matrix changes

Per section 4.3.3, this phase adds three remaining tier 3 ecosystem
compatibility jobs to `_unit_tests.yml`: `click-help-colors`,
`click-default-group`, `click-aliases` (all on Python 3.14 /
Click 8.3). Combined with the four tier 3 jobs added in phase 2
(section 5.3.1.5), the full 7-package ecosystem matrix is now active.

### 5.10.1.10. Not in this phase

- No new features
- Everything after this phase is polish (phase 10)

## 5.10.2. Pull requests

Suggested split. Each PR ships code **with** its tests and leaves
the repo at 100% coverage.

1. **Public `PrismMixin` + `PrismGroup.wrapping()`** — promote
   `PrismMixin` to the public API, implement the `wrapping()`
   classmethod factory with `group_class` propagation, plus MRO
   verification tests and broad ecosystem compatibility tests
   against the packages that work via generic wrapping alone
   (`click-help-colors`, `click-didyoumean`, `click-default-group`,
   `click-aliases`, and a `rich-click` / `cloup` baseline that doesn't
   yet rely on PR 2/3 features).
2. **`tree_theme_from_rich_click()` helper** — implement the
   conversion function in `_config.py`, export it, decide and
   document the field mapping, plus tests with a real
   `RichHelpConfiguration` (fields mapped correctly), with a
   plain duck-typed object (matching attributes work), and
   verifying unknown fields are silently skipped.
3. **Information preservation** — `cloup` sections, default-command
   markers (`click-default-group`), command aliases
   (`click-aliases`) preserved in tree output, plus integration
   tests for each against real instances of those packages.
4. **Multi-plugin stacking documentation** — user-docs page
   showing manual MRO stacking for 3+ Group subclasses. Code-free
   (no coverage impact).

## 5.10.3. Tests

- `PrismGroup.wrapping(SubclassGroup)` tests for each target
  package:
    - Tree-as-help renders correctly
    - Non-tree help pages retain subclass formatting
    - Child groups created via `@cli.group()` inherit the combined
      class
    - `tree_help` modes work as expected
- `cli.add_command(tree_command())` on each target package:
    - Tree subcommand works without interfering with subclass
      behavior
- `wrapping(click.Group)` optimization: returns `PrismGroup` itself
- MRO verification for combined classes
- `group_class` propagation: child groups in a
  `wrapping(RichGroup)` CLI are also Tree-enabled `RichGroup`
- `tree_theme_from_rich_click()`:
    - Style fields from `RichHelpConfiguration` appear in the
      returned `TreeTheme`
    - Duck-typed: plain objects with matching attributes produce
      the same result as a real `RichHelpConfiguration`
    - Unknown or missing fields are silently skipped
    - Returned `TreeTheme` passes to `TreeConfig(theme=...)` and
      renders correctly
- Information preservation:
    - `cloup` section labels appear in tree output
    - `click-default-group` default marker `*` appears in tree
      output
    - `click-aliases` aliases appear in parentheses in tree output
- Manual MRO stacking sanity test: one test constructs a
  three-class combination and verifies it doesn't crash
- The existing tier 3 compatibility jobs in the test matrix
  (section 4.3.3) already run these integrations on the full Python ×
  Click combinations — these are the first releases where they
  actually test real behavior

## 5.10.4. Requirements newly satisfied

| Req | Notes |
|---|---|
| R32 | Combinable with all target Group subclasses |
| R33 | Non-interference — combined packages continue to work as before |
| R34 | Domain separation — `click-prism` owns tree output only |
| R35 | Information preservation (`cloup` sections, default markers, aliases) |
| R36 | Multi-plugin stacking via manual subclassing (documented, not automated) |

## 5.10.5. Exit criteria

- [ ] `from click_prism import PrismMixin` works
- [ ] `PrismGroup.wrapping(RichGroup)` produces a working combined
  class
- [ ] All seven target packages have integration tests passing
  in both paths (`wrapping` + `add_command`)
- [ ] `tree_theme_from_rich_click(rc_cfg)` returns a `TreeTheme`
  matching `rc_cfg`'s styles
- [ ] Information preservation tests pass for `cloup`,
  `click-default-group`, `click-aliases`
- [ ] Multi-plugin stacking example works and is documented
- [ ] All 41 requirements from section 2.3.4 are satisfied
- [ ] Coverage is 100% on merged runs
- [ ] Full release pipeline succeeds for `0.9.0`
