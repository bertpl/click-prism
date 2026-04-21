# 4.3. Test Infrastructure

## 4.3.1. pytest configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
source = ["click_prism"]

[tool.coverage.report]
precision = 2
fail_under = 100
```

Target: **100% line coverage.** The `fail_under = 100` setting
makes `make coverage` and CI fail on any coverage drop.

No single test run can reach 100% — code paths depend on which
optional dependencies are present (`rich` renderer vs fallback,
`rich-click` style inheritance vs default). Coverage is measured by
running tests four times with different dependency configurations
and merging the results. See section 4.3.5.

## 4.3.2. Fixtures

Shared fixtures in `tests/conftest.py`:

```python
@pytest.fixture
def flat_cli():
    """Group with 3 leaf commands, no nesting."""

@pytest.fixture
def nested_cli():
    """Group → subgroup → commands, 2 levels deep."""

@pytest.fixture
def deep_cli():
    """4 levels of nesting with hidden and deprecated commands."""

@pytest.fixture
def empty_cli():
    """Group with no commands."""
```

Each fixture returns a `click.Group` instance. Tests that need
`PrismGroup`, `wrapping()`, or specific `TreeConfig` create their
own CLI inline — fixtures cover only the reusable base hierarchies.

## 4.3.3. Test matrix design

### 4.3.3.1. Dimensions

| Dimension | Values | Count |
|---|---|---|
| Python | 3.10, 3.11, 3.12, 3.13, 3.14 | 5 |
| `click` | 8.0, 8.1, 8.2, 8.3 | 4 |
| `rich` | absent, 13.0, latest | 3 |
| Related packages | `rich-click`, `cloup`, `click-extra`, `click-didyoumean` | 4 |
| Dependency resolution | highest, lowest-direct | 2 |

Full Cartesian product: **480 jobs.** Not viable.

### 4.3.3.2. Subset strategy

Three tiers, each targeting a different risk:

**Tier 1 — Core matrix** (Python x Click boundaries)

Tests the package itself across the version space. No `rich`, no
neighbor packages.

```yaml
strategy:
  matrix:
    python: ["3.10", "3.11", "3.12", "3.13", "3.14"]
    click: ["8.0", "8.3"]        # boundaries
    resolution: ["highest"]
  include:
    # Lowest-direct at both corners
    - python: "3.10"
      click: "8.0"
      resolution: "lowest-direct"
    - python: "3.14"
      click: "8.3"
      resolution: "lowest-direct"
    # Fill middle Click versions on latest Python
    - python: "3.14"
      click: "8.1"
      resolution: "highest"
    - python: "3.14"
      click: "8.2"
      resolution: "highest"
```

**14 jobs.** Covers every Python version, every Click version, and
both resolution strategies at the version boundaries.

**Tier 2 — `rich` variations** (fixed Python/Click)

Tests optional `rich` dependency behavior.

```yaml
jobs:
  - { python: "3.14", click: "8.3", rich: "none" }
  - { python: "3.14", click: "8.3", rich: "13.0" }    # oldest supported
  - { python: "3.14", click: "8.3", rich: "latest" }
  - { python: "3.10", click: "8.0", rich: "latest" }   # rich on oldest combo
```

**4 jobs listed, 3 net new.** The "none" case overlaps with tier 1
(Python 3.14 / Click 8.3 / highest). Covers `rich` absence, `rich`
floor version, and `rich` on both newest and oldest Python/Click
combos.

**Tier 3 — Ecosystem compatibility** (fixed Python/Click/`rich`)

Tests `PrismGroup.wrapping()` and `add_command(tree_command())`
against each neighbor package.

```yaml
jobs:
  - { python: "3.14", click: "8.3", package: "rich-click" }
  - { python: "3.14", click: "8.3", package: "cloup" }
  - { python: "3.14", click: "8.3", package: "click-extra" }
  - { python: "3.14", click: "8.3", package: "click-didyoumean" }
  - { python: "3.14", click: "8.3", package: "click-help-colors" }   # phase 9
  - { python: "3.14", click: "8.3", package: "click-default-group" } # phase 9
  - { python: "3.14", click: "8.3", package: "click-aliases" }       # phase 9
```

**7 jobs.** The first four are active from phase 2 (when `PrismGroup` ships);
the last three are added in phase 9 when `PrismGroup.wrapping()` and the
full ecosystem compatibility suite land. Each job tests both integration paths:

1. `PrismGroup.wrapping(SubclassGroup)` — tree + subclass coexist,
   child groups inherit combined class, non-tree help retains
   subclass formatting.
2. `add_command(tree_command())` on an unmodified subclass
   instance.

### 4.3.3.3. Total

| Tier | Jobs | Risk covered |
|---|---|---|
| Core | 14 | Python/Click version compatibility |
| `rich` | 3 | Optional dependency behavior |
| Compatibility | 7 | Ecosystem Group subclass coexistence |
| **Total** | **24** | |

The matrix tests **compatibility** (breadth). Coverage is a
separate concern — see section 4.3.5.

## 4.3.4. Dependency installation for matrix jobs

Each matrix cell installs a **single globally-consistent dependency
set** resolved from scratch — `uv.lock` is intentionally **not**
used. The cell's matrix coordinates (Click version, Rich version,
extra package, resolution strategy) are fed into `uv pip compile` as
overrides, so the resolver picks every transitive version under the
chosen strategy with the cell's pins honored.

```bash
# 1. Express the cell's pins as resolver overrides.
cat > /tmp/overrides.txt <<EOF
click==$CLICK_VERSION
rich==$RICH_VERSION   # only if pinned (omit for "latest" or "absent")
EOF

# 2. Optional: extra non-dependency package for the cell (Tier 3).
echo "$EXTRA_PACKAGE" > /tmp/extras.in   # only if set

# 3. Compile a globally-consistent requirements.txt.
uv pip compile pyproject.toml /tmp/extras.in \
  --group dev \
  --extra rich                  \   # only if rich is in scope
  --override /tmp/overrides.txt \
  --resolution "$RESOLUTION"    \   # highest | lowest-direct
  --python-version "$PY_VERSION" \
  -o /tmp/requirements.txt

# 4. Install exactly that set into a fresh venv.
uv venv --python "$PY_VERSION"
uv pip sync /tmp/requirements.txt
uv pip install -e . --no-deps

# 5. Run the tests.
.venv/bin/pytest tests --durations=20
```

**Why not start from `uv.lock`.** The previous approach (sync from
the lock, then layer `uv pip install <pin>` on top) produced
inconsistent state when overrides interacted with `--resolution
lowest-direct`: a cell labeled `(click=8.3, lowest-direct)` would
silently end up with Click 8.0 because the final
`uv pip install --resolution lowest-direct .` re-resolved against
`pyproject.toml`'s `click>=8.0` floor, overriding the earlier
explicit pin. Compiling the full set in one resolve eliminates that
class of bug — the requirements.txt is the single source of truth
for the cell, and the matrix label always matches the installed
versions.

**Notes:**

- `--python-version` must be passed explicitly to `uv pip compile`.
  Without it, transitive deps gated on Python-version markers (e.g.
  `exceptiongroup` for Python < 3.11) are dropped from the resolution
  when `--override` is used, causing pytest to fail to import.
- For Tier 3 the extra package is added as a separate input to the
  same `uv pip compile` call — that way it becomes part of the
  globally-resolved set rather than a layered `uv pip install`
  afterward.
- `lowest-direct` only affects the project's direct dependencies
  (those declared in `pyproject.toml`). Dev-group dependencies
  (`pytest`, `ruff`, etc.) are always resolved at "highest" since
  their pins exist for tooling, not user-facing version compatibility.

## 4.3.5. Coverage strategy

No single test run can reach 100% — optional dependencies create
mutually exclusive code paths. Coverage is measured by running
tests four times with different dependency configurations,
appending results into a single `.coverage` file.

### 4.3.5.1. Coverage runs

| Run | Dependencies | Code paths covered |
|---|---|---|
| 1 | Base (no `rich`) | Plain text renderer, `_compat.py` absent branch, fallback paths |
| 2 | + `rich` | `_render_rich.py`, `_compat.py` present branch, theme defaults |
| 3 | + `rich` + `rich-click` | `tree_theme_from_rich_click()` conversion helper code paths |
| 4 | + `cloup` + `click-extra` + `click-didyoumean` + `click-help-colors` + `click-default-group` + `click-aliases` | Any code gated on ecosystem-compat packages (`cloup` section headings, default markers, aliases, etc.) — full set active from phase 9 |

**Rationale for run 4.** The Tier 3 compat jobs in the test
matrix (section 4.3.3) exercise the full behavior of `click-prism` combined
with each ecosystem package on separate CI jobs, but those jobs do not feed
coverage. If any code path in `click-prism` only activates when one of those
packages is present — e.g., `cloup` section preservation (R35),
`click-default-group` default markers, `click-aliases` alias rendering, or
ecosystem-specific wrapping tweaks — that path has to be exercised inside the
coverage run for the `fail_under=100` gate to be meaningful.
Run 4 closes that loop. The three packages added in phase 9
(`click-help-colors`, `click-default-group`, `click-aliases`) are added to
this run at the same time. If no gated paths exist for a given package, its
presence in run 4 is a no-op at negligible cost.

### 4.3.5.2. Makefile target (single source of truth)

The `make coverage` target implements this. (The block below
is repeated from the Makefile in section 4.1.5 for clarity.)

```makefile
coverage:
	mkdir -p ./reports
	# 1. Without Rich — covers fallback paths
	uv sync --group dev
	COVERAGE_FILE=./reports/.coverage \
		uv run pytest ./tests --cov --durations=20
	# 2. With Rich — covers Rich renderer
	uv sync --group dev --extra rich
	COVERAGE_FILE=./reports/.coverage \
		uv run pytest ./tests --cov --cov-append --durations=20
	# 3. With Rich + rich-click — covers style inheritance
	uv pip install rich-click
	COVERAGE_FILE=./reports/.coverage \
		uv run pytest ./tests --cov --cov-append --durations=20
	# 4. + ecosystem compat — covers any code paths gated on
	#    ecosystem packages being present (full set from phase 9)
	uv pip install cloup click-extra click-didyoumean \
	               click-help-colors click-default-group click-aliases
	COVERAGE_FILE=./reports/.coverage \
		uv run pytest ./tests --cov --cov-append --durations=20
	# Report
	COVERAGE_FILE=./reports/.coverage \
		uv run coverage report --fail-under=100
	COVERAGE_FILE=./reports/.coverage \
		uv run coverage html -d ./reports/coverage
	# Restore base dev environment
	uv sync --group dev
```

`--cov-append` adds to the existing `.coverage` file rather than
replacing it. After all four runs the merged result is checked
against `fail_under=100`. The final `uv sync` restores the base
dev environment so the developer isn't left with `rich-click`
or ecosystem packages installed.

### 4.3.5.3. Usage

`make coverage` is the single source of truth for coverage
measurement. It is called in three contexts:

1. **Locally by the developer** — to verify 100% before pushing.
2. **By `make release`** — as its first step, before badge
   generation and tagging (section 4.4.4). Ensures the release has
   verified 100% coverage and provides the data for the frozen
   coverage badge.
3. **By CI (`push_to_main.yml`)** — uploads the merged result to
   Codecov for main's dynamic badge (section 4.4.2).

## 4.3.6. Snapshot tests

Rendered output (plain text, `rich`, JSON) is tested via
[`syrupy`](https://github.com/syrupy-project/syrupy) snapshots
stored as `.txt` files alongside the tests. `syrupy` is added to
`[dependency-groups] dev` (section 4.1).

This catches unintended formatting regressions in:

- Unicode/ASCII tree chrome
- Column alignment
- `rich` styled output
- JSON structure

### 4.3.6.1. Extension: single-file text snapshots

Rendered output is captured as UTF-8 text in one file per
snapshot, via a custom extension of `syrupy`'s
`SingleFileSnapshotExtension`:

```python
from syrupy.extensions.single_file import SingleFileSnapshotExtension, WriteMode

class TextSnapshotExtension(SingleFileSnapshotExtension):
    _write_mode = WriteMode.TEXT
    _file_extension = "txt"
```

This produces `.txt` files that diff cleanly in any tool, rather
than syrupy's default `.ambr` format (which wraps strings in
triple quotes and escapes single-line non-ASCII).

### 4.3.6.2. Rich tests: dual snapshot helper

`rich`-rendered output is captured **twice** per test — once as
plain text (no ANSI codes) and once with full ANSI. A single
helper drives both captures:

```python
# tests/_snapshot_helper.py
from rich.console import Console, RenderableType

def _render_plain(renderable: RenderableType) -> str:
    """Capture Rich output with styling stripped. Human-readable."""
    console = Console(color_system=None, force_terminal=False, width=80)
    with console.capture() as capture:
        console.print(renderable)
    return capture.get()

def _render_ansi(renderable: RenderableType) -> str:
    """Capture Rich output with full ANSI. Styling verification."""
    console = Console(color_system="truecolor", force_terminal=True, width=80)
    with console.capture() as capture:
        console.print(renderable)
    return capture.get()

def assert_rich_snapshot(renderable: RenderableType, snapshot) -> None:
    """Snapshot both plain and ANSI renderings."""
    assert _render_plain(renderable) == snapshot(name="plain")
    assert _render_ansi(renderable) == snapshot(name="ansi")
```

Usage:

```python
def test_render_nested_tree(nested_cli, snapshot):
    tree = render_tree(nested_cli)
    assert_rich_snapshot(tree, snapshot)

def test_render_with_theme(nested_cli, snapshot):
    theme = TreeTheme(
        columns=ThemeColumns(group_names=ColumnStyle(color="cyan")),
        rows=ThemeRows(groups=RowStyle(bold=True)),
    )
    config = TreeConfig(theme=theme)
    tree = render_tree(nested_cli, config=config)
    assert_rich_snapshot(tree, snapshot)
```

Each test produces two files:

- `tests/__snapshots__/test_render_nested_tree[plain].txt` — what a human sees
- `tests/__snapshots__/test_render_nested_tree[ansi].txt` — the exact styling

Reviewers look at the `[plain]` diff to understand visual changes;
the `[ansi]` diff confirms styling is intentional or flags a theme
regression. When `rich` changes something subtle (rare), only
`[ansi]` files update.

### 4.3.6.3. Pinned Console for determinism

Both captures use fully-pinned Console arguments (`color_system`,
`force_terminal`, `width`). This bypasses `rich` env-var and
terminal auto-detection, keeping output byte-identical across
machines and `rich` versions. Research (`rich` 13.0 → 14.3) found
zero CHANGELOG entries that would change the ANSI bytes for
styled text under these pinned settings — the brittleness concern
is near-hypothetical in practice.

### 4.3.6.4. Scope of the dual helper

| Output path | Snapshot mechanism |
|---|---|
| `rich` renderer (with or without theme) | `assert_rich_snapshot` (dual) |
| Plain text renderer (no `rich` involved) | single `snapshot` via `TextSnapshotExtension` |
| ASCII fallback (no `rich` involved) | single `snapshot` via `TextSnapshotExtension` |
| JSON output | single `snapshot` via `TextSnapshotExtension` |

The dual helper is used wherever output goes through the `rich`
rendering pipeline. Non-`rich` output paths use a single snapshot
because there's no styling dimension to verify.

**Implementation note**: expanding the dual helper to cover
*every* snapshot test (including plain-text and JSON paths, where
the two snapshots would happen to be identical) is a reasonable
consistency choice. The decision is deferred to implementation
once the actual test files exist and the tradeoff between
consistency and snapshot count can be judged concretely.

### 4.3.6.5. Updating snapshots

When output changes intentionally:

```bash
uv run pytest --snapshot-update
```

Review the diff in git and commit.
