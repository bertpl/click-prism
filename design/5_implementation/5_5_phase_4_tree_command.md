# 5.5. Phase 4: `tree_command()`

**Version:** `0.4.0`
**Goal:** Opt-in tree subcommand with runtime controls. Ships
the last of the three integration paths — joining `PrismGroup`
(phase 2) and the standalone functions `show_tree()` /
`render_tree()` (phase 1).

## 5.5.1. Scope

### 5.5.1.1. `tree_command()` factory (`_command.py`)

- `tree_command(name="tree", config=None, **kwargs) -> click.Command`
- Returns a `click.Command` that can be added to any group via
  `cli.add_command(tree_command())`. This is ordinary Click:
  the tree subcommand lives in the group's normal command dict,
  no lazy-injection tricks (section 3.4.2.3).
- Works with vanilla `click.Group` — no `PrismGroup` required
  (R37)
- Also works alongside `PrismGroup` (coexistence with tree-as-help)
- CLI flags on the tree subcommand:
    - `--depth N` — limit traversal depth at runtime, overrides
      `TreeConfig.depth`
- Discovers its parent group at render time via
  `ctx.parent.command`
- Outputs rendered tree to stdout
- The returned command carries a `_click_prism_cmd` marker
  attribute (section 3.4.2.3), used downstream by the collision-detection
  override below
- `tree_help` validation: if `config` is provided and
  `config.tree_help` is anything other than `None` or `"none"`,
  the factory raises `PrismError` synchronously (before
  returning the command). `tree_help` modes are a group-level
  concept and have no meaning on a leaf command; the error surfaces
  the misconfiguration at definition time (section 3.4.2.3.1)

### 5.5.1.2. Name collision detection (`PrismMixin.add_command` override)

- `PrismMixin.add_command` override — **Active** (new in this
  phase; deferred from phase 2). This is the first phase where
  the override becomes useful — previous phases had no tree
  commands to collide with.
- Raises `PrismError` at definition time (immediately inside
  `add_command()`, before the group is wired up) whenever a tree
  command name and a regular command name collide — in either
  registration order (section 2.2.1.3): a marked command added over an
  existing regular command, or a regular command added over an
  existing marked command.
- Message identifies the conflict and directs the user to
  `tree_command(name=...)`.
- `PrismError` itself is already defined and exported from
  phase 1 (`_exceptions.py`), where `resolve()` raises it for
  invalid depth values. This phase adds the first
  integration-level raise site (collision detection).
- **R37 fallback path (non-`PrismMixin` groups):** no
  `add_command` override is in play — Click's standard behavior
  (silent overwrite) applies. Collision detection is a
  convenience of the `PrismMixin` integration paths only, not a
  guarantee of `tree_command()` itself.

### 5.5.1.3. Subtree scoping

- A tree subcommand added to a child group shows only that
  group's subtree (R16)
- Accomplished via `ctx.parent.command` lookup at render time

### 5.5.1.4. Configuration — wiring

- `TreeConfig` field active in this phase: no new fields (the
  `depth` field was already defined in phase 1; the CLI flag
  layer of the precedence chain is now live).
- Precedence now fully active (section 3.1): CLI flags > per-group config
  > inherited config > built-in defaults.
- `_effective_config_for()`'s non-`PrismMixin` branch —
  **Completes (from phase 2)**: `tree_command()` on vanilla
  `click.Group` (R37 fallback) exercises this path for the first
  time.

### 5.5.1.5. Public API additions

- `tree_command` exported from `click_prism` (`PrismError` was
  already exported in phase 1 and raised by `resolve()` — this
  phase adds the collision-detection raise site)

### 5.5.1.6. Not in this phase

- No `--help-json` on the tree subcommand (`--help-json` is a
  separate root-only option on `PrismGroup`, not a tree subcommand
  flag — see section 2.3.4 R2)
- No all-groups tree-as-help mode (phase 5)
- No parameter display columns (phase 6)

## 5.5.2. Pull requests

Suggested split. Each PR ships code **with** its tests and leaves
the repo at 100% coverage.

1. **`tree_command()` factory** — `_command.py` with the factory
   (including the `_click_prism_cmd` marker and `tree_help`
   validation), plus integration tests on vanilla `click.Group`
   exercising the R37 fallback path, coexistence tests with
   `PrismGroup`, and validation rejection/accept tests.
2. **`--depth` runtime flag** — CLI flag on the tree subcommand,
   precedence wiring so it wins over per-group config, plus tests
   verifying CLI-flag-wins behavior against a deep fixture.
3. **Collision detection + subtree scoping** — activate
   `PrismMixin.add_command` override raising the already-defined
   `PrismError` (from phase 1) on marker-matching name
   collisions, subtree scoping via `ctx.parent.command`, plus
   tests for collision cases (both directions — tree command
   added to a group that already has that name, and a user
   command added to a group that already has a tree subcommand
   with that name) and subtree rendering on nested groups.

## 5.5.3. Tests

- `tree_command()` on vanilla `click.Group`: produces tree output
  when invoked as `mycli tree` (R37 fallback path — no
  `PrismMixin` involved, no collision detection)
- `tree_command()` on `PrismGroup`: coexists with tree-as-help
  without conflict; tree subcommand lives in the group's normal
  command dict
- `--depth N` runtime override: tested against a deep fixture;
  verifies CLI flag wins over per-group config
- Name collision detection (via `PrismMixin.add_command` override):
    - `cli.add_command(tree_command())` on a `PrismGroup` that
      already has a command named `tree` → `PrismError`
    - `cli.add_command(tree_command())` followed by
      `cli.add_command(click.Command("tree"))` → `PrismError`
      (the check fires in both directions)
    - Child `PrismGroup` using a different tree-command name is
      **not** a collision (it's the config precedence mechanism
      working as designed; see sections 3.1 and 2.3.4 R14)
    - R37 path: `cli.add_command(tree_command())` on a vanilla
      `click.Group` with a pre-existing `tree` command produces
      Click's standard silent overwrite, **not** `PrismError`
      — documented non-guarantee of the fallback path
- Subtree scoping: `mycli admin tree` shows only the `admin`
  subtree
- Custom name via `tree_command(name="cmds")` works
- `tree_help` validation:
    - `tree_command(config=TreeConfig(tree_help="root"))` raises
      `PrismError` at call time
    - `tree_command(config=TreeConfig(tree_help="all"))` raises
      `PrismError` at call time (pins the whitelist against
      regressions; `"all"` is type-valid on `TreeConfig` from
      phase 1, even though the mode itself lands in phase 5)
    - `tree_command(config=TreeConfig(tree_help="none"))` does not
      raise (explicitly disabled is a valid and meaningful choice)
    - `tree_command(config=TreeConfig())` (all-`None`) does not raise

## 5.5.4. Requirements newly satisfied

| Req | Notes |
|---|---|
| R3 | `tree_command()` opt-in, works with or without `PrismGroup` |
| R13 | Default name `"tree"`, configurable via `tree_command(name=...)` |
| R14 | Name collision raises `PrismError` |
| R15 | `--depth` runtime flag |
| R16 | Subtree scoping |
| R23 | Runtime override precedence (CLI flag wins) |
| R37 | Subcommand-only fallback (works with any group subclass) |

## 5.5.5. Exit criteria

- [ ] `from click_prism import tree_command` works
  (`PrismError` was already importable from phase 1)
- [ ] `cli.add_command(tree_command())` works on a vanilla
  `click.Group` and produces tree output
- [ ] `mycli tree --depth 2` limits the rendered tree
- [ ] `mycli admin tree` shows only the admin subtree
- [ ] Collision tests all pass
- [ ] `tree_command(config=TreeConfig(tree_help="root"))` and
  `tree_command(config=TreeConfig(tree_help="all"))` both raise
  `PrismError`; `tree_command(config=TreeConfig(tree_help="none"))`
  and `tree_command(config=TreeConfig())` do not
- [ ] Coverage is 100% on merged runs
- [ ] Full release pipeline succeeds for `0.4.0`
