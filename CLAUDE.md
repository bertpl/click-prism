# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**click-prism** is a Python package (not yet implemented) that adds tree visualization of Click command hierarchies. It replaces the abandoned `click-command-tree` package.

## Project status

Pre-implementation. All work so far is planning documents under `design/`.

## Document hierarchy

- `design/` — **canonical plan documents** (the source of truth being built up); `1_analysis/`, `2_vision/`, `3_design/`, `4_infrastructure/`, `5_implementation/`
- `.local/_brainstorm/` — earlier iterations; inspiration only, will be deleted. Do not reference from plan documents.
- `design/_examples/cli/` — working example CLIs (plain Click, rich-click, Cloup, etc.) with their own venv
- `design/_examples/screenshots/` — WebP generation pipeline for all mocks and analysis screenshots; see [`README.md`](design/_examples/screenshots/README.md) for setup and usage.

  **You MUST regenerate screenshots proactively** whenever anything in the pipeline changes — mock scripts, the generation shell scripts, `_render.py`, `_capture.py`, `postprocess_svg.py`, or any pipeline parameter (zoom, format, title bar settings). Do not wait to be asked. After regenerating, move the output and delete stale files:
  ```bash
  # Mock screenshots (2.3 UX docs)
  cd design/_examples/screenshots && ./generate_mocks.sh && mv output/mock_*.{webp,txt} ../../2_vision/mocks/

  # Analysis screenshots (1.2 status quo docs)
  cd design/_examples/screenshots && ./generate.sh && mv output/{click,cloup,rich}_*.{webp,txt} ../../1_analysis/2_status_quo/screenshots/
  ```

The plan documents are self-contained and read in order of their header indexes. Each section builds on previous ones — later sections may reference earlier ones, but not vice versa.

## Key design decisions (from brainstorm docs)

- **TreeMixin + TreeGroup** architecture: tree behavior as a mixin with cooperative `super()` calls; `TreeGroup.wrapping(OtherGroup)` for combining with existing Group subclasses
- **Three integration paths**: `cls=TreeGroup`, `cli.add_command(tree_command())`, `show_tree(cli)`
- **TreeConfig dataclass**: all fields default to `None` (unset); `.resolve()` applies defaults; `.merge()` overlays
- **Compatibility**: Click >=8.0, Python >=3.10, Rich >=13.0 (optional)
- **Zero required dependencies** beyond Click; Rich is an optional extra
