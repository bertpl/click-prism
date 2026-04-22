# 4.4. CI/CD

## 4.4.1. Branch and release strategy

**Trunk-based development on `main`.** No release branches.

```
main                              ← development trunk
  ├─ commit ...
  ├─ commit "release: 0.2.0"     ← created by `make release`
  │    └─ tag v0.2.0             ← created by `make release`
  │         → CI: test + publish  ← triggered by tag push
  └─ commit "chore: begin next development cycle" ← created by `make release`
```

Flow:

1. Development happens on feature branches, merged to `main` via
   PR. **Squash-merge is the only allowed merge method** — repo
   settings disable merge commits and rebase merges, so each PR
   produces exactly one commit on `main`. The squash commit
   subject is the PR title (which follows the `<prefix>: …`
   convention from section 4.2.5); the body is the PR body. The
   feature branch is auto-deleted on merge. Version in
   `pyproject.toml` on main stays at the last released version
   between releases.
2. A maintainer decides to release and runs
   `make release VERSION=X.Y.Z` — a single developer command that
   drives the 18-step process documented in section 4.4.4 (8 validation
   gates, then version bump, changelog finalization, badge
   freezing, commits, tag, badge restoration, and push).
3. Tag push triggers `release_tag.yml`. CI runs the full test
   matrix. The `publish` job requires **manual approval** from
   the `prod` GitHub environment (section 4.4.6) before publishing to
   PyPI.
4. After approval, CI publishes to PyPI and creates a GitHub
   Release with notes extracted from CHANGELOG.md.

The developer decides **when** to release and **what version**.
CI handles validation and publishing.

## 4.4.2. Workflow overview

```
push to feature branch      → push_to_branch.yml        → single-config test
pull request to main        → pull_request_to_main.yml   → full test matrix + lint
push to main                → push_to_main.yml           → full test matrix + coverage
push tag v*                 → release_tag.yml            → test + publish (requires approval)
```

When `make release` pushes to main and pushes a tag
simultaneously, both `push_to_main.yml` and `release_tag.yml`
trigger. Tests run twice — redundant but harmless, and acts as a
double safety net.

Reusable workflows (prefixed with `_`):

- `_unit_tests.yml` — full test matrix (section 4.3.3), called by multiple
  workflows. Implemented in phase 0 (section 5.1.3).

**Naming convention**: `unit_test` (singular, composite action)
runs one matrix cell (one Python + Click + `rich` combo).
`_unit_tests.yml` (plural, reusable workflow) is the full matrix
that invokes `unit_test` for each cell. Workflows that only need
a single-config test call `unit_test` directly; workflows that
need the full matrix call `_unit_tests.yml`.

### 4.4.2.1. push_to_branch.yml

```yaml
name: Push to branch
on:
  push:
    branches-ignore:
      - main
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: ./.github/actions/unit_test
        # No inputs → uses defaults: Python from .python-version (3.10),
        # Click from uv.lock, resolution "highest", no extras.
```

Single-config test for fast feedback on feature branches. Uses
the same Python/Click that a developer runs locally (3.10 +
lock-pinned Click), matching the "local = minimum supported"
principle from section 4.1. Full version-matrix compatibility is covered
on PR (section 4.4.2 `pull_request_to_main.yml`).

### 4.4.2.2. pull_request_to_main.yml

```yaml
name: Pull Request to Main
on:
  pull_request:
    branches: [main]
    types: [opened, synchronize]
jobs:
  validate-branch-name:
    runs-on: ubuntu-latest
    steps:
      - name: Check branch name
        run: |
          BRANCH="${{ github.head_ref }}"
          if [[ ! "$BRANCH" =~ ^(feat|fix|chore|docs|refactor|test)/[a-z0-9-]+$ ]]; then
            echo "::error::Branch name '$BRANCH' does not match pattern"
            exit 1
          fi

  require-changelog:
    needs: [validate-branch-name]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0
      - name: Check changelog updated for feat/ and fix/ branches
        run: |
          BRANCH="${{ github.head_ref }}"
          if [[ ! "$BRANCH" =~ ^(feat|fix)/ ]]; then
            echo "Branch '$BRANCH' is not feat/ or fix/; changelog entry not required."
            exit 0
          fi
          if git diff --name-only "${{ github.event.pull_request.base.sha }}...HEAD" | grep -q '^CHANGELOG\.md$'; then
            echo "CHANGELOG.md was modified — OK."
            exit 0
          fi
          echo "::error::feat/ and fix/ PRs must update CHANGELOG.md"
          exit 1

  lint:
    needs: [validate-branch-name]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v7
      - run: uv sync --group dev
      - run: uv run ruff check .

  test:
    needs: [validate-branch-name]
    uses: ./.github/workflows/_unit_tests.yml
```

Full test matrix + lint + branch-name validation (section 4.2.4) +
changelog enforcement on `feat/` and `fix/` branches. The check
catches missing entries at PR time instead of at release time
(`scripts/release.py` step 8 would otherwise be the only safety
net, by which point multiple PRs may have already merged without
entries). `chore/`, `docs/`, `refactor/`, `test/` are exempt
because their changes are typically not user-visible. All four
gated jobs (`require-changelog`, `lint`, `test`) wait for
`validate-branch-name` so a PR with a malformed branch name fails
fast without running the heavier matrix.

### 4.4.2.3. push_to_main.yml

```yaml
name: Push to Main
on:
  push:
    branches: [main]
jobs:
  test:
    uses: ./.github/workflows/_unit_tests.yml

  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v7
      - run: make coverage
      - name: Export coverage to XML
        env:
          COVERAGE_FILE: ./reports/.coverage   # match `make coverage`
        run: uv run coverage xml -o ./reports/coverage.xml
      - uses: codecov/codecov-action@v5
        with:
          files: ./reports/coverage.xml
          token: ${{ secrets.CODECOV_TOKEN }}   # Codecov no longer
                                                # accepts tokenless
                                                # uploads for non-fork
                                                # repos. CODECOV_TOKEN
                                                # is a per-repo upload
                                                # token (read on
                                                # codecov.io repo page,
                                                # stored as a GitHub
                                                # repo secret).
```

Full test matrix + merged coverage upload to Codecov. The
`make coverage` target (section 4.3.5) runs tests four times with
different dependency configurations and checks `fail_under=100`.

**Codecov configuration**: Codecov does not support configuration
via `pyproject.toml` (exception to design principle #8 in section 4.0).
If customization beyond Codecov's defaults is needed, add
`.codecov.yml` at repo root. The initial design uses Codecov
defaults — any customization is deferred to implementation if
required.

### 4.4.2.4. release_tag.yml

```yaml
name: Release
on:
  push:
    tags: [v*]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: ./.github/actions/validate_version_trigger

  test:
    uses: ./.github/workflows/_unit_tests.yml

  publish:
    needs: [validate, test]
    runs-on: ubuntu-latest
    environment: prod              # Requires manual approval (section 4.4.6)
    permissions:
      id-token: write              # Required for Trusted Publishing
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v7
      - run: uv build
      - uses: pypa/gh-action-pypi-publish@release/v1

  github-release:
    needs: publish
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v7
      - name: Extract release notes from CHANGELOG.md
        run: uv run python scripts/extract_changelog.py > release_notes.md
      - name: Create GitHub Release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh release create "${{ github.ref_name }}" \
            --title "${{ github.ref_name }}" \
            --notes-file release_notes.md
```

The `publish` job blocks on `prod` environment approval — a
maintainer must approve in the GitHub UI before PyPI upload
proceeds. The full test matrix runs again on the tag as a safety
net.

## 4.4.3. Composite actions

| Action | Purpose |
|---|---|
| `unit_test` | Install deps + run pytest for a single matrix cell |
| `validate_version_trigger` | Check tag name matches `pyproject.toml` version |

Both live under `.github/actions/` and are implemented in
phase 0 (section 5.1.3).

## 4.4.4. Release process: `make release`

### 4.4.4.1. CHANGELOG.md format

Hand-written,
[Keep a Changelog](https://keepachangelog.com/)–inspired (we use
`## X.Y.Z (date)` instead of the strict `## [X.Y.Z] - date` for
readability). The `## Unreleased` section is pre-populated with
all six Keep a Changelog category sub-headers so developers never
have to remember the names or spelling:

```markdown
# Changelog

## Unreleased

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## 0.1.0 (2026-05-01)

### Added
- Tree rendering with Unicode and ASCII styles
- Three integration paths: cls, add_command, show_tree / render_tree (#3)

### Fixed
- Handle empty groups without crashing (#7)
```

Developers add bullet entries under the appropriate category as
they merge PRs. Issue references (`#7`) in entries become
clickable links on GitHub and in the GitHub Release notes.

Note the released `0.1.0` section above has only `### Added` and
`### Fixed` — empty categories are dropped at release time (see
step 10 below).

**Single source of truth.** `CHANGELOG.md` serves both as the
developer-facing change history and as the source for user-facing
release notes (GitHub Release bodies). We do not maintain
separate release notes — the same content is re-surfaced in
multiple places.

### 4.4.4.2. What `make release VERSION=X.Y.Z` does

```makefile
release:
	@test -n "$(VERSION)" || (echo "Usage: make release VERSION=X.Y.Z" && exit 1)
	$(MAKE) coverage
	uv run python scripts/release.py $(VERSION)
```

`scripts/release.py` and `scripts/extract_changelog.py` are
implemented in phase 0 (section 5.1.2) — this section is the behavioral
spec both scripts must satisfy.

The `scripts/release.py` script performs these steps:

**Validation (fail fast, before any changes):**

1. **Working tree** — on `main`, clean, no unpushed commits.
2. **In sync with remote** — `git fetch` + verify local main
   matches `origin/main`. Prevents releasing stale code.
3. **Coverage data present** — `./reports/.coverage` exists and
   was modified in the last 10 minutes. Ensures the developer ran
   `make release` (which runs `make coverage` first) rather than
   invoking `scripts/release.py` directly with stale or missing
   data. (10 minutes is chosen to be safely larger than a typical
   `make coverage` run — 4 pytest runs on a small package takes
   seconds to a couple of minutes — while still catching stale
   data from sessions run hours earlier. Adjust if the test suite
   grows significantly.)
4. **Version is an upgrade** — `VERSION` > current version in
   `pyproject.toml`. Prevents accidental downgrades.
5. **Tag doesn't exist** — checks both local (`git tag -l`) and
   remote (`git ls-remote --tags`). Prevents collisions.
6. **Version not on PyPI** — queries
   `pypi.org/pypi/click-prism/VERSION/json` (expects 404). Prevents
   re-releasing a published version.
7. **Classifiers match** — `pyproject.toml` Python classifiers
   match `.python-versions`. Fails if they diverge.
8. **Changelog has entries** — `## Unreleased` section has at
   least one bullet entry under at least one category sub-header.
   Fails with a clear error if all categories are empty.

**Release commit (frozen badges, finalized changelog, bumped version):**

9. **Bump version** — runs `uv version VERSION`.
10. **Finalize changelog** — renames `## Unreleased` to
    `## VERSION (YYYY-MM-DD)` with today's date, then removes any
    category sub-headers that have no entries. This keeps the
    released section concise without requiring developers to
    manage category headers manually.
11. **Generate coverage badge** — runs `genbadge coverage` using
    `./reports/.coverage` (validated in step 3). Writes
    `badges/coverage.svg`.
12. **Freeze README badges** — replaces four dynamic badge URLs
    (version, Python, coverage, license) with static equivalents
    (section 4.4.5). CI badge stays dynamic. Values read from
    `.python-versions`, `pyproject.toml`, and
    `./reports/.coverage`.
13. **Commit** — `release: VERSION`.
14. **Tag** — `vVERSION`.

**Post-release (prepare main for continued development):**

15. **Restore dynamic badges** — reverses the URL freeze from
    step 12.
16. **Add new changelog header** — inserts `## Unreleased` with
    all six Keep a Changelog category sub-headers (Added,
    Changed, Deprecated, Removed, Fixed, Security) at the top of
    CHANGELOG.md.
17. **Commit** — `chore: begin next development cycle`.
18. **Push** — `git push --atomic origin main refs/tags/vVERSION`.
    The `--atomic` flag ensures both refs push together or
    neither does, avoiding an inconsistent state if one push
    fails.

### 4.4.4.3. Recovery from mid-script failure

If `scripts/release.py` fails after the release commit/tag
(step 13 or later) but before the push (step 18), the local repo
is in an inconsistent state. The script catches errors in the
post-tag phase and prints exact recovery commands, e.g.:

```
ERROR: step 15 failed (restore dynamic badges).
Local state: release commit and tag created, not pushed.
To abort and retry:
  git tag -d v0.2.0
  git reset --hard HEAD~1   # or HEAD~2 if step 17 also ran
```

After recovery, fix the issue and re-run `make release VERSION=0.2.0`.

## 4.4.5. README badges

### 4.4.5.1. Badge list

```markdown
[![CI](https://github.com/bertpl/click-prism/actions/workflows/push_to_main.yml/badge.svg)](...)
[![PyPI](https://img.shields.io/pypi/v/click-prism)](...)
[![Python](https://img.shields.io/pypi/pyversions/click-prism)](...)
[![Coverage](https://codecov.io/gh/bertpl/click-prism/branch/main/graph/badge.svg)](...)
[![License](https://img.shields.io/pypi/l/click-prism)](...)
```

### 4.4.5.2. Dynamic vs frozen

| Badge | On main | At tagged release | Rationale |
|---|---|---|---|
| CI | Dynamic | **Dynamic** | Answers "is the project healthy now?" — a frozen "passing" from months ago is not useful |
| PyPI version | Dynamic | Frozen | Shows the version at the time of release |
| Python versions | Dynamic | Frozen | Shows the supported versions at the time of release |
| Coverage | Dynamic (Codecov) | Frozen (committed SVG) | Shows the actual coverage for that version's code |
| License | Dynamic | Frozen | Rarely changes, but frozen for correctness |

The CI badge is the only one that stays dynamic at tagged
releases. It reflects current project health, which is the
relevant question regardless of which version someone is looking
at. All other badges are version-specific facts that should be
immutable.

### 4.4.5.3. Freezing mechanism

At release time, `scripts/release.py` replaces four dynamic badge
URLs with static equivalents:

| Badge | Frozen URL example |
|---|---|
| Version | `img.shields.io/badge/PyPI-v0.2.0-blue` |
| Python | `img.shields.io/badge/python-3.10 | ... | 3.14-blue` |
| Coverage | `raw.githubusercontent.com/bertpl/click-prism/vX.Y.Z/badges/coverage.svg` |
| License | `img.shields.io/badge/license-BSD--3--Clause-blue` (badge SVG; LICENSE link target is also tag-pinned to `github.com/bertpl/click-prism/blob/vX.Y.Z/LICENSE` for parity with coverage) |

The coverage badge is a committed SVG generated by `genbadge`
(not a shields.io URL) — it captures the exact coverage
percentage from the release's test run.

After tagging, the four frozen URLs are restored to dynamic for
main. The tagged commit permanently has frozen badges (except
CI). Anyone browsing `v0.2.0` on GitHub or the 0.2.0 page on PyPI
sees that version's actual stats.

## 4.4.6. Release access control

Releasing to PyPI is irreversible. Multiple layers ensure only
authorized maintainers can trigger it. **All of these must be
configured before the first release.**

### 4.4.6.1. Gate chain

```
make release VERSION=X.Y.Z (local)
  ✓ coverage is 100% (make coverage)
  ✓ main in sync with remote
  ✓ version is an upgrade
  ✓ tag doesn't exist (local + remote)
  ✓ version not on PyPI
  ✓ classifiers match .python-versions
  ✓ changelog has entries
    → git push (requires repo write access + branch protection bypass)
      → CI: full test matrix passes
        → publish job (requires prod environment approval)
          ✓ maintainer approves in GitHub UI
            → PyPI upload (Trusted Publishing OIDC)
```

### 4.4.6.2. GitHub repository settings

- **Branch protection on `main`**: require PR reviews and status
  checks for normal development. The release maintainer is listed
  under "Allow specified actors to bypass required pull requests"
  so that `make release` can push directly to main.
- **Tag protection**: restrict creation of `v*` tags to
  maintainers.

### 4.4.6.3. GitHub environment: `prod`

Create in repository Settings → Environments:

- **Required reviewers**: list the maintainers who can approve a
  release. The `publish` job in `release_tag.yml` uses
  `environment: prod` — it blocks until an approved reviewer
  clicks "Approve" in the GitHub Actions UI.
- **Deployment branches**: restrict to tags matching `v*`.

### 4.4.6.4. PyPI Trusted Publishing (OIDC)

Configured on PyPI as a "pending publisher" during project setup
(section 4.1). The binding specifies:

- Repository: `bertpl/click-prism`
- Workflow: `release_tag.yml`
- Environment: `prod`

Only this exact combination can publish to PyPI. No API tokens
are stored anywhere — authentication is via short-lived OIDC
tokens scoped to the workflow run.

### 4.4.6.5. No custom secrets required

Tags are created locally by the maintainer (via `make release`)
and pushed with their normal git credentials. CI uses only
`GITHUB_TOKEN` (automatic) for creating GitHub Releases and
Trusted Publishing OIDC for PyPI. No `GIT_ADMIN_TOKEN` or other
custom secrets are needed.
