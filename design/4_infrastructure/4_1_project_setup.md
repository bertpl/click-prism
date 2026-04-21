# 4.1. Project Setup

## 4.1.1. Repository structure

Top-level layout. The internal structure of `click_prism/` is defined
in section 3.0 (Module Layout). `tests/` mirrors the package layout.

```
click-prism/
├── click_prism/                   # Package — see section 3.0 for module layout
├── tests/                        # Tests — see section 4.3 for structure
├── scripts/
│   ├── release.py                # Release automation (section 4.4.4)
│   └── extract_changelog.py      # Extracts the current version's section from CHANGELOG.md (section 4.4.2)
├── badges/                       # Generated badge SVGs, committed (section 4.4.5)
├── docs/                         # MkDocs source (section 4.5)
├── .github/
│   ├── workflows/
│   └── actions/
├── .python-version               # Default Python for local dev (pinned to 3.10, the minimum supported)
├── .python-versions              # Supported Python versions (CI matrix)
├── pyproject.toml
├── uv.lock                       # Committed; dev-only
├── Makefile
├── .pre-commit-config.yaml
├── .readthedocs.yaml
├── mkdocs.yml
├── .gitignore
├── LICENSE                       # BSD-3-Clause
├── README.md
├── CHANGELOG.md
└── CONTRIBUTING.md
```

Flat layout (no `src/` wrapper).

## 4.1.2. pyproject.toml

```toml
[project]
name = "click-prism"
version = "0.0.0"
description = "Tree visualization for Click command hierarchies."
readme = "README.md"
license = "BSD-3-Clause"
authors = [
    { name = "Bert Pluymers", email = "bert.pluymers@gmail.com" }
]
requires-python = ">=3.10"
dependencies = [
    "click>=8.0",
]
keywords = ["cli", "click", "tree", "command-tree", "terminal"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Topic :: Software Development :: Libraries",
    "Typing :: Typed",
]

[project.optional-dependencies]
rich = ["rich>=13.0"]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=6.0",
    "ruff>=0.14",
    "syrupy>=4.0",
    "genbadge[coverage]>=1.1",
    "pre-commit>=4.0",
]
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.0",
    "mkdocstrings[python]>=0.24",
]

[project.urls]
Documentation = "https://click-prism.readthedocs.io/"
Source = "https://github.com/bertpl/click-prism"
Changelog = "https://github.com/bertpl/click-prism/blob/main/CHANGELOG.md"
Issues = "https://github.com/bertpl/click-prism/issues"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.sdist]
packages = ["click_prism"]

[tool.hatch.build.targets.wheel]
packages = ["click_prism"]
```

Tool configuration for `ruff`, `pytest`, and coverage is defined in
their respective sections (sections 4.2.1, 4.3.1) and lives in the same
`pyproject.toml`.

Key decisions:

- **`hatchling`** as build backend.
- **Version** in `pyproject.toml` `[project] version` field — single
  source of truth. Bumped manually via `uv version` during
  `make release` (section 4.4.4).
- **Versioning scheme**: [SemVer](https://semver.org/) —
  `major.minor.patch` only. No pre-release or build suffixes
  (`-rc1`, `+build`, etc.).
- **`[dependency-groups]`** (PEP 735) for dev-only tools. These are
  not installable by end users — correct semantics for dev tooling.
- **`[project.optional-dependencies]`** for user-facing extras only
  (`rich`).
- **No entry points** — this is a library, not a CLI.

## 4.1.3. uv and uv.lock

`uv` is the package manager.

`uv.lock` is committed to the repo. It pins the full resolved
dependency graph (direct + transitive) for reproducible CI and
contributor environments. It has **zero effect on end users** — it
is never included in the sdist or wheel. `pip install click-prism`
resolves from `pyproject.toml` constraints only.

```bash
uv sync --group dev                # Install dev deps from lock
uv sync --extra rich               # Install with Rich extra
uv sync --all-extras --all-groups  # Everything
```

### 4.1.3.1. Lock vs test matrix

The lock file provides a single reproducible default environment
(e.g., `click` 8.3.2, `rich` 13.9.4). Local development and the default
CI jobs use this.

Test matrix jobs (section 4.3) deliberately **break out of the lock** to
test other version combinations. They sync from the lock first,
then override specific packages:

```bash
uv sync --group dev                          # Start from lock
uv pip install "click==8.0"                  # Override Click
uv pip install --resolution lowest-direct .  # Or re-resolve
```

This means the lock gives you fast, deterministic builds for
everyday work, while the matrix ensures compatibility across the
full version space.

### 4.1.3.2. Keeping the lock current

```bash
uv lock --upgrade    # Re-resolve everything to latest compatible versions
```

Run periodically (manually), review the diff, commit. This is how
dependency updates flow in — there is no automated tooling for
this yet.

## 4.1.4. .python-version and .python-versions

Two related files, different purposes:

**`.python-version`** (singular) — pins the default Python version
for local development and `uv run`. Ensures all contributors use
the same Python when working on the project.

```
3.10
```

**Pinned to the minimum supported version (3.10)**, not the latest.
Rationale: **local = minimum supported**. This keeps four numbers
in agreement:

| Location | Value | Purpose |
|---|---|---|
| `requires-python` in `pyproject.toml` | `>=3.10` | Floor for installs |
| `target-version` for `ruff` (section 4.2.1) | `py310` | Floor for lint/syntax |
| `.python-version` (this file) | `3.10` | Floor for local dev |
| `.python-versions` (below) | `3.10`–`3.14` | Full CI test matrix |

Using the minimum version locally catches forward-compatibility
mistakes immediately — any feature introduced in 3.11+ (e.g.,
`Self`, `ExceptionGroup`, `tomllib`, PEP 695 generic syntax,
`@override`, PEP 649 deferred annotations in 3.14) fails in the
local dev loop rather than only in CI.

The tradeoff is giving up newer Python amenities during local dev
(3.13's improved REPL, 3.11+'s fine-grained error locations, minor
performance gains). For a small library these don't matter much
day-to-day.

**`.python-versions`** (plural) — source of truth for the CI test
matrix. Read by humans maintaining the matrix in
`_unit_tests.yml` (section 4.4.2) and validated against
`pyproject.toml` classifiers by `scripts/release.py` (section 4.4.4).

```
3.10
3.11
3.12
3.13
3.14
```

`pyproject.toml` classifiers are kept in sync with `.python-versions`
manually; validated by `scripts/release.py` at release time (section 4.4.4).

## 4.1.5. Makefile

```makefile
.PHONY: help dev-setup build test coverage format lint update-deps release docs show-coverage show-docs

help:
	@echo 'Commands:'
	@echo '  dev-setup   One-time: sync dev deps + install pre-commit hooks'
	@echo '  build       Build package'
	@echo '  test        Run pytest'
	@echo '  coverage    Multi-run coverage report (./reports/coverage)'
	@echo '  format      Format and fix with ruff'
	@echo '  lint        Ruff check'
	@echo '  update-deps Re-resolve uv.lock to latest versions'
	@echo '  release     Bump version, validate, tag, push (section 4.4.4)'
	@echo '  docs        Build mkdocs site (./reports/docs)'

dev-setup:
	uv sync --group dev
	uv run pre-commit install

build:
	uv build

test:
	uv run pytest ./tests --durations=20

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
	#    cloup / click-extra / click-didyoumean / click-help-colors /
	#    click-default-group / click-aliases being present
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

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check .

update-deps:
	uv lock --upgrade

release:
	@test -n "$(VERSION)" || (echo "Usage: make release VERSION=X.Y.Z" && exit 1)
	$(MAKE) coverage
	uv run python scripts/release.py $(VERSION)

docs:
	uv sync --group docs
	uv run mkdocs build

show-coverage:
	open ./reports/coverage/index.html

show-docs:
	open ./reports/docs/index.html
```

All tool invocations use `uv run` to use the project's pinned
versions from `uv.lock`.

The `release` target runs `make coverage` first (validates 100%,
produces data for badge generation), then delegates to
`scripts/release.py` (section 4.4.4).

## 4.1.6. .gitignore

Standard Python ignores plus project-specific:

```gitignore
# Python
__pycache__/
*.egg-info/
dist/
.pytest_cache/
.ruff_cache/

# Coverage
htmlcov/
.coverage
reports/

# Virtual environments
.venv/

# Private dev docs
.local/

# IDE
.idea/
.vscode/

# AI assistants
.claude/
CLAUDE.md
AGENTS.md
.cursor/
.cursorrules
.aider*
.copilot/
.github/copilot-instructions.md
```

Note: `badges/` is **not** in `.gitignore` — badge SVGs are
committed to the repo so they are frozen at each tag (section 4.4.5).

## 4.1.7. Skeleton docs

Created at project setup, populated with real content later (section 4.5):

- **README.md** — package name, one-line description, installation,
  basic usage stub, badges (section 4.4.5).
- **CHANGELOG.md** — hand-written, Keep a Changelog–inspired
  format. Initial `## Unreleased` section with all six category
  sub-headers. See section 4.4.4 for the release automation.
- **CONTRIBUTING.md** — dev setup (`make dev-setup` — syncs dev
  deps and installs pre-commit hooks), running tests, branch
  naming, changelog conventions.
- **LICENSE** — BSD-3-Clause.

### 4.1.7.1. GitHub issue and PR templates, SECURITY.md

Standard open-source practice is to provide:

- `.github/ISSUE_TEMPLATE/` (bug report, feature request)
- `.github/pull_request_template.md`
- `SECURITY.md` (vulnerability reporting policy, per GitHub's
  community-health file recommendation)

`click-prism` will have these before its 0.10.0 release. The timing
of when they are added (initial scaffolding vs later phase) is an
implementation plan concern (section 5), not a design decision.

## 4.1.8. PyPI setup

Reserve the package name before first code is written:

1. Create a "pending publisher" on PyPI for `click-prism`.
2. Configure **Trusted Publishing** (OIDC) — no API tokens needed.
   Links the GitHub repository + workflow file + environment to
   PyPI.
3. The `release_tag.yml` workflow (section 4.4.2) uses this to publish.
