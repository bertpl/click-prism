# 5.0. Implementation Plan Overview

> This section defines the implementation order: which features ship
> in which phase, mapped to the requirements in section 2.3.4. It does not
> introduce new design decisions — those all live in sections 3 and 4.

## 5.0.1. Scope

Each phase ships as a PyPI release. Phases are strictly sequential:
each builds on the previous. A phase is "done" when all its exit
criteria are met and the release is successfully published.

**Phase 0** is infrastructure only — no user-visible functionality.
It exists to validate the full CI/CD + release pipeline (section 4)
before any feature work begins. Phase 0 ships as a series of
throwaway `0.0.x` releases; these are yanked from PyPI before the
first real release (`0.1.0`).

**Phase 10** is a polish release — no new requirements satisfied.
By phase 9 all 41 requirements are satisfied; phase 10 completes the
documentation, README, hero assets, and final bug sweep, then ships
as `0.10.0`.

## 5.0.2. Phasing philosophy

- **Small phases over big ones.** Each phase is scoped to a single
  coherent concern. This keeps releases reviewable and rollbacks
  surgical.
- **Standalone before Click-integrated.** Phase 1 ships the
  rendering engine behind the standalone functions (`show_tree`,
  `render_tree`) before any Click integration. This de-risks the
  core rendering logic.
- **PrismGroup before `tree_command()`.** The Group subclass path is
  the flagship UX (R1). It ships first, with the opt-in subcommand
  following.
- **`rich` split into two phases.** Basic rendering (auto-detection,
  bold groups, terminal adaptation) in phase 7; theming (two-axis
  model, built-in themes) in phase 8. Theming is substantial enough
  to deserve its own phase.
- **Composability is late.** Phase 9 tests against `rich-click`,
  `cloup`, `click-extra`, etc. It requires all other features to be
  stable so the integration tests exercise real behavior.
- **0.10.0 is a polish release.** No new features. All 41 requirements
  are satisfied by the end of phase 9.
- **Each phase is explicit about what it implements and what it
  defers.** Modules grow across phases: a module introduced in
  phase M may gain new members, branches, or fields in later
  phases, and phase M is not required to pre-declare members that
  do not yet exist in any form. What each phase's scope MUST do is
  label every cross-phase element it touches with one of:

    - **Active** — fully implemented for the scope this phase
      covers; no deferrals.
    - **Partial (→ phase N: &lt;what's deferred&gt;)** — this phase
      implements part of the element; the rest is deferred to
      phase N. Include a short description of what's deferred.
      Multiple deferrals on one element are written as
      `→ phase N: X; → phase P: Y`.
    - **Completes (from phase M)** — this phase finishes work a
      previous phase labelled Partial.

  Symmetry rule: every `Partial (→ phase N)` in phase M must be
  matched by a `Completes (from phase M)` in phase N. A deferral
  without a completion, or a completion without a deferral, is
  a plan bug.

  If a later phase broadens an element that an earlier phase
  shipped as Active (a new branch or feature was not anticipated
  upstream), update the earlier phase's scope to Partial so the
  symmetry invariant holds. Do not leave the relationship
  implicit in prose.

## 5.0.3. Phases

| Phase | Version | Focus | New requirements |
|---|---|---|---|
| 0 | 0.0.x (throwaway) | Manual setup + CI/CD shakedown | *(none — infra only)* |
| 1 | 0.1.0 | Standalone rendering | R4 (partial), R6, R7, R8, R9 (default), R10, R11, R12, R38, R39, R40, R41 |
| 2 | 0.2.0 | `PrismGroup` + tree-as-help root mode | R1 (partial), R5, R17 (partial), R18, R22, R24 |
| 3 | 0.3.0 | `--help-json` + parameter extraction | R1 (completes), R2, R4 (completes) |
| 4 | 0.4.0 | Opt-in `tree_command()` | R3, R13, R14, R15, R16, R23, R37 |
| 5 | 0.5.0 | Tree-as-help modes expansion | R17 (completes), R19, R20, R21 |
| 6 | 0.6.0 | 4-column parameter display | R9 (completes), R25 |
| 7 | 0.7.0 | `rich` rendering | R26, R27, R28, R29 |
| 8 | 0.8.0 | `rich` theming | R30, R31 |
| 9 | 0.9.0 | Composability | R32, R33, R34, R35, R36 |
| 10 | 0.10.0 | Polish release | *(all requirements already satisfied)* |

## 5.0.4. Requirements coverage

Every requirement in section 2.3.4 is addressed. The table below shows
the status of each requirement after each phase:

- (empty) — not yet addressed
- 🔧 — partially ready
- ✅ — fully ready

| Req | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R1  |   |   | 🔧 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R2  |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R3  |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R4  |   | 🔧 | 🔧 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R5  |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R6  |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R7  |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R8  |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R9  |   | 🔧 | 🔧 | 🔧 | 🔧 | 🔧 | ✅ | ✅ | ✅ | ✅ | ✅ |
| R10 |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R11 |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R12 |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R13 |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R14 |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R15 |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R16 |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R17 |   |   | 🔧 | 🔧 | 🔧 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R18 |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R19 |   |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R20 |   |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R21 |   |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R22 |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R23 |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R24 |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R25 |   |   |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ |
| R26 |   |   |   |   |   |   |   | ✅ | ✅ | ✅ | ✅ |
| R27 |   |   |   |   |   |   |   | ✅ | ✅ | ✅ | ✅ |
| R28 |   |   |   |   |   |   |   | ✅ | ✅ | ✅ | ✅ |
| R29 |   |   |   |   |   |   |   | ✅ | ✅ | ✅ | ✅ |
| R30 |   |   |   |   |   |   |   |   | ✅ | ✅ | ✅ |
| R31 |   |   |   |   |   |   |   |   | ✅ | ✅ | ✅ |
| R32 |   |   |   |   |   |   |   |   |   | ✅ | ✅ |
| R33 |   |   |   |   |   |   |   |   |   | ✅ | ✅ |
| R34 |   |   |   |   |   |   |   |   |   | ✅ | ✅ |
| R35 |   |   |   |   |   |   |   |   |   | ✅ | ✅ |
| R36 |   |   |   |   |   |   |   |   |   | ✅ | ✅ |
| R37 |   |   |   |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R38 |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R39 |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R40 |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| R41 |   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## 5.0.5. Phase 0: throwaway releases

Phase 0 will ship several `0.0.x` releases (best case 2–3, worst
case 10–15) while the CI/CD pipeline is shaken out. These contain
no meaningful functionality — they exist only to exercise the full
release flow end-to-end.

**Before 0.1.0 ships:**

- All `0.0.x` releases are **yanked** from PyPI (the `yank` action
  hides them from `pip install` without deleting them from history).
- Git tags for `v0.0.x` remain in the repo as a record of the
  infrastructure shakedown.
- `0.1.0` is the first release anyone should install.

## 5.0.6. Sub-sections

- [5.1. Phase 0: Infrastructure](5_1_phase_0_infrastructure.md)
- [5.2. Phase 1: Standalone rendering](5_2_phase_1_standalone_rendering.md)
- [5.3. Phase 2: PrismGroup](5_3_phase_2_prism_group.md)
- [5.4. Phase 3: `--help-json`](5_4_phase_3_help_json.md)
- [5.5. Phase 4: `tree_command()`](5_5_phase_4_tree_command.md)
- [5.6. Phase 5: Tree-as-help modes](5_6_phase_5_tree_as_help_modes.md)
- [5.7. Phase 6: Parameter display](5_7_phase_6_parameter_display.md)
- [5.8. Phase 7: `rich` rendering](5_8_phase_7_rich_rendering.md)
- [5.9. Phase 8: `rich` theming](5_9_phase_8_rich_theming.md)
- [5.10. Phase 9: Composability](5_10_phase_9_composability.md)
- [5.11. Phase 10: Polish & 0.10.0](5_11_phase_10_polish.md)
