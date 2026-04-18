# 5.3. Phase 2: PrismGroup

**Version:** `0.2.0`
**Goal:** Flagship integration path. `cls=PrismGroup` adds
tree-as-help in root mode, with child group inheritance and
per-group configuration.

## 5.3.1. Scope

### 5.3.1.1. Mixin (`_mixin.py`)

- `PrismMixin` class — all tree behavior as a cooperative-`super()`
  mixin (section 3.4.1). **Partial (→ phase 9: public export
  alongside `wrapping()`)**: internal in this phase, living at
  `click_prism._mixin.PrismMixin` and not re-exported from
  `click_prism/__init__.py`. Users who reach into the private
  module import it at their own risk; the API is not considered
  stable until phase 9.
- `format_help(ctx, formatter)` override (section 3.4.2.1) —
  **Partial (→ phase 5: `tree_help="all"` routing)**:
    - Routes the help pipeline based on `tree_help` mode. This
      phase handles `"root"` and `"none"`; `"all"` is deferred.
    - When tree-as-help is active: calls `format_usage`,
      `format_help_text`, `click.Command.format_options(self, ctx, formatter)`,
      `self.format_commands()` (tree), then `format_epilog`. The
      `format_options` call is an **explicit base call**, not
      `super().format_options()`: it bypasses the MRO so that
      wrapped classes (`RichGroup`, `cloup.Group`) do not inject
      their own option formatting into tree-as-help pages. The two
      forms are indistinguishable until phase 9 introduces
      composability; the explicit form is required from this phase
      to prevent a silent regression when wrapping lands (sections 3.4.1.1,
      3.5.1).
    - When tree-as-help is not active: `super().format_help()`
      delegates to the wrapped class's full pipeline.
- `format_commands(ctx, formatter)` override (section 3.4.2.1) —
  **Active**:
    - When called from the tree-active branch of `format_help()`:
      resolves config, renders tree, writes via
      `formatter.write()`.
    - When tree-as-help is not active: delegates to
      `super().format_commands()` (flat command list).
- Other `PrismMixin` methods from section 3.4.1 are **deferred**
  to later phases. They are not created in this phase — the class
  gains them when the phase that needs them implements them:
    - `make_context` override and `_help_json_option` /
      `_help_json_callback` helpers — deferred to phase 3 (they
      exist solely to inject `--help-json` on the root group).
    - `add_command` override — deferred to phase 4 (collision
      detection has nothing to detect until `tree_command()`
      exists).

### 5.3.1.2. PrismGroup (`_group.py`)

- `PrismGroup(PrismMixin, click.Group)` — convenience class
- `group_class = PrismGroup` so child groups inherit tree behavior
- `__init__` accepts `tree_config` kwarg, forwards remaining
  kwargs to `super().__init__()`

### 5.3.1.3. Configuration — wiring

- `TreeConfig.tree_help` — **Completes (from phase 1)** for the
  `"root"` and `"none"` modes, with a further **Partial
  (→ phase 5: `"all"` mode)** remaining.
- `.merge(base)` (shipped in phase 1) is now used for per-group
  precedence: child config overlaid onto parent config.
- Two context-chain walkers (section 3.4.2):
    - `PrismMixin._resolve_tree_help(ctx)` — newly introduced
      **Partial (→ phase 5: `"all"` branch)**: specialized walker
      for the `tree_help` field, short-circuits on the first
      non-`None` value. Handles `"root"` and `"none"` modes this
      phase.
    - `_effective_config_for(group, ctx)` — newly introduced
      **Partial (→ phase 4: non-`PrismMixin` parent branch)**:
      module-level helper returning the merged effective
      `TreeConfig` for a group. Introduced here because per-group
      precedence (level 3 from section 3.1.2) goes live. The
      non-`PrismMixin` parent branch (treat such parents as
      contributing nothing to the walk) is coded but not exercised
      this phase — first exercised by `tree_command()` on vanilla
      `click.Group` in section 5.5.1.1.
- Precedence (from section 3.1): per-group config > inherited config >
  built-in defaults (CLI flag layer lands in phase 4).

### 5.3.1.4. Public API additions

- `PrismGroup` exported from `click_prism`

See section 3.4.3 for the canonical public API surface. `PrismMixin`
remains unexported until phase 9 (composability).

### 5.3.1.5. CI matrix changes

Per section 4.3.3, this phase adds four tier 3 ecosystem compatibility
jobs to `_unit_tests.yml`: `rich-click`, `cloup`, `click-extra`,
`click-didyoumean` (all on Python 3.14 / Click 8.3). These run
the existing test suite with the ecosystem packages installed
alongside `click-prism` — no integration tests yet, just canary
detection for import-time conflicts. Real integration testing
lands in phase 9.

### 5.3.1.6. Not in this phase

- No `--help-json` (phase 3)
- No `tree_command()` (phase 4)
- No "all-groups" tree-as-help mode (phase 5)
- No `rich` rendering (phase 7)
- No composability (`PrismMixin` not public yet, no `wrapping()`)

## 5.3.2. Pull requests

Suggested split. Each PR ships code **with** its tests and leaves
the repo at 100% coverage.

1. **`PrismMixin` + `PrismGroup`** — `_mixin.py` with
   `format_help` and `format_commands` overrides, `_resolve_tree_help`
   context-chain walk; `_group.py` with
   `PrismGroup(PrismMixin, click.Group)` and `group_class =
   PrismGroup`; plus integration tests covering `cls=PrismGroup`,
   child inheritance, tree-as-help root mode snapshot tests, and
   the explicit-base-call guard for `format_options` (section 5.3.3).
2. **Per-group precedence** — `_effective_config_for()` helper,
   precedence resolution chain (per-group > inherited > defaults)
   using `.merge()` (shipped in phase 1), plus integration tests
   for per-group config override behavior.

## 5.3.3. Tests

- Click integration tests:
    - `@click.group(cls=PrismGroup)` with default config renders
      tree on root `--help`
    - Child group created via `@cli.group()` inherits `PrismGroup`
      without explicit `cls=`
    - Child `--help` uses standard Click format (not tree) in
      "root" mode
    - `tree_help="none"`: `PrismGroup` with
      `TreeConfig(tree_help="none")` produces standard Click help
      on root `--help` (no tree)
    - Per-group `tree_config` overrides parent
- Precedence tests: child overrides parent where fields are set,
  inherits otherwise
- `_effective_config_for()` unit test: directly exercise the
  non-`PrismMixin` parent branch (a context whose `parent.command`
  is a plain `click.Group`) and verify the branch contributes
  nothing to the walk. Required to reach 100% coverage on the
  helper in phase 2; the branch is first used by production code
  in phase 4 when `tree_command()` lands on vanilla groups.
- Zero-config test: `@click.group(cls=PrismGroup)` without any
  config produces expected output
- Snapshot tests for tree-as-help output (plain text only — `rich`
  not yet)
- Explicit-base-call guard for `format_options` (section 5.3.1.1):
  construct a synthetic `class TestGroup(PrismMixin, Wrapped)` where
  `Wrapped` is a `click.Group` subclass whose `format_options()`
  records its invocation. Invoke `--help` with tree-as-help active
  and assert `Wrapped.format_options` is **not** called. This
  guards against a `super().format_options()` regression in
  phases 3–8, which would produce identical output to the explicit
  base call (wrapped `format_options` only enters an actual MRO
  once `wrapping()` lands in phase 9) and therefore silently pass
  every other test.

## 5.3.4. Requirements newly satisfied

| Req | Notes |
|---|---|
| R1 | **Partial** — tree-as-help works via `cls=PrismGroup`. `--help-json` completes R1 in phase 3. |
| R5 | Child group inheritance via `group_class` |
| R17 | **Partial** — `"root"` and `"none"` modes; `"all"` mode completes in phase 5. |
| R18 | Root-only tree-as-help (default behavior) |
| R22 | Per-group configuration with `.merge()` precedence |
| R24 | Zero-config default: `cls=PrismGroup` alone works with sensible defaults |

## 5.3.5. Exit criteria

- [ ] `from click_prism import PrismGroup` works
- [ ] `@click.group(cls=PrismGroup)` adds tree-as-help to root
  `--help` with no other code changes
- [ ] Child groups inherit tree behavior automatically
- [ ] All snapshot + integration tests pass
- [ ] Coverage is 100% on merged runs
- [ ] Full release pipeline succeeds for `0.2.0`
