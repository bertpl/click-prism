# 5.6. Phase 5: Tree-as-help modes

**Version:** `0.5.0`
**Goal:** Complete R17 by adding the `"all"` mode.
Also locks in coexistence with `tree_command()` from phase 4.

## 5.6.1. Scope

### 5.6.1.1. `tree_help` mode expansion (`_mixin.py`)

- `PrismMixin._resolve_tree_help(ctx)` — **Completes (from
  phase 2)**: adds the `"all"` branch. The context-chain walk
  itself is unchanged.
- `TreeConfig.tree_help` — **Completes (from phase 2)**: the
  `"all"` mode is now functional end-to-end (phase 2 supported
  `"root"` and `"none"`).
- `PrismMixin.format_help` override — **Completes (from phase 2)**:
  the `tree_help="all"` routing branch is now active.
- `"all"` mode: every group's `--help` shows a tree from that
  point down.
- Context-chain inheritance: setting `tree_help="all"` on the
  root propagates to all tree-enabled child groups without any of
  them needing explicit config.

### 5.6.1.2. Coexistence with `tree_command()`

- R20: when `tree_command()` is added alongside `PrismGroup`,
  tree-as-help and the tree subcommand coexist without conflict
- Tree-as-help uses the developer's configured settings (no
  runtime flags)
- The tree subcommand accepts `--depth` for runtime scope control
  (already from phase 4)
- Both paths coexist on the same group

### 5.6.1.3. Developer-controlled (`format_help` + `format_commands`)

- R21: tree-as-help output is determined entirely by the
  developer's `TreeConfig`, not by end-user flags
- `format_commands()` does not inspect any runtime flag — it uses
  the resolved config at render time

### 5.6.1.4. `tree_help="none"` on `tree_command()`

Already implemented in phase 4 (section 5.5.1.1) — `tree_command()`
rejects `tree_help` values other than `None` or `"none"` at
definition time.

### 5.6.1.5. Not in this phase

- No parameter display columns (phase 6)
- No `rich` (phase 7)

## 5.6.2. Pull requests

Suggested split. Each PR ships code **with** its tests and leaves
the repo at 100% coverage.

1. **`"all"` mode support** — `_mixin.py` updates to activate
   `"all"` mode, context-chain inheritance for `tree_help`
   resolution, plus tests for `"all"` mode and `PrismGroup` ×
   `tree_command()` coexistence (covers R17, R19, R20, R21).

## 5.6.3. Tests

- Mode tests:
    - `tree_help="root"` (default): only root shows tree
    - `tree_help="all"`: every group shows tree from that point
    - Child override: parent `"all"`, child `"none"` → child uses
      standard Click help
- Context-chain inheritance:
    - Parent sets `"all"`, child has `None` → child inherits `"all"`
    - Parent sets `"all"`, child sets `"root"` → child does **not**
      show tree (it is not the root group, so `"root"` mode has no
      effect — standard Click help is produced)
- Coexistence tests:
    - `PrismGroup(tree_config=TreeConfig(tree_help="all"))` +
      `cli.add_command(tree_command())` both work on the same CLI
    - `--help` shows tree (dev config), `mycli tree --depth 2` shows
      depth-limited tree (runtime override)

## 5.6.4. Requirements newly satisfied

| Req | Notes |
|---|---|
| R17 | **Completes** — `"all"` mode (all three modes now active: `"root"`, `"none"` from phase 2; `"all"` from this phase) |
| R19 | All-groups mode |
| R20 | Coexistence of tree-as-help with `tree_command()` |
| R21 | Developer-controlled tree-as-help (no runtime flags influence it) |

## 5.6.5. Exit criteria

- [ ] `"all"` mode works as specified; all three `tree_help` modes
  verified end-to-end
- [ ] Context-chain inheritance tested in both directions
  (inherit from parent, override in child)
- [ ] Coexistence test: `--help` and `mycli tree --depth N` both
  work on the same `PrismGroup` + `tree_command()` CLI
- [ ] Coverage is 100% on merged runs
- [ ] Full release pipeline succeeds for `0.5.0`
