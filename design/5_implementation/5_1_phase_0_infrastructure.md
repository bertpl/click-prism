# 5.1. Phase 0: Infrastructure

**Version:** `0.0.x` (throwaway releases)
**Goal:** Full CI/CD pipeline working end-to-end, before any feature
code is written.

## 5.1.1. Manual actions (required from maintainer)

These can only be done by a human with the right accounts. They
must all be completed before the first `0.0.1` push.

### 5.1.1.1. GitHub

- [ ] **Make the existing `bertpl/click-prism` repository public** (it
  is currently private — all design work so far has happened in the
  private repo).
- [ ] Configure **branch protection on `main`**:
    - Require PR reviews + status checks to pass.
    - List the release maintainer under "Allow specified actors to
      bypass required pull requests" (section 4.4.6).
- [ ] Configure **tag protection** for `v*` tags, restricted to
  maintainers (section 4.4.6).
- [ ] Create the **`prod` environment** in Settings → Environments:
    - Add required reviewers (release approvers).
    - Restrict deployment branches to tags matching `v*`.
- [ ] Confirm **no custom secrets are needed**. All git write
  operations (version bump, tag) happen locally via
  `make release` — CI only publishes to PyPI (Trusted Publishing
  OIDC) and creates a GitHub Release (automatic `GITHUB_TOKEN`).
  No `GIT_ADMIN_TOKEN` or other PAT is required (section 4.4.6).

### 5.1.1.2. PyPI

- [ ] Create a **pending publisher** on PyPI for `click-prism` (section 4.1).
- [ ] Configure **Trusted Publishing** (OIDC) binding:
    - Repository: `bertpl/click-prism`
    - Workflow: `release_tag.yml`
    - Environment: `prod`

### 5.1.1.3. Read the Docs

- [ ] Import the project on readthedocs.org.
- [ ] Verify that builds trigger on push to `main` and on release
  tags (section 4.5.2).

## 5.1.2. Repository scaffolding

Create all files and directories defined in section 4.1:

- `click_prism/` with `__init__.py`, `py.typed`, and a stub
  `__version__` attribute (read from `importlib.metadata` so the
  source of truth stays `pyproject.toml`'s `[project] version`).
  No functional code yet.
- `tests/` with one trivial test (e.g.,
  `def test_import(): import click_prism`).
- `scripts/release.py` fully implemented per section 4.4.4. Must work
  end-to-end before any `0.0.x` release.
- `scripts/extract_changelog.py` fully implemented per section 4.4.2.
- `pyproject.toml` per section 4.1 (with the real classifiers,
  dependencies, and dep groups).
- `uv.lock` committed.
- `.python-version` pinned to `3.10` (section 4.1).
- `.python-versions` listing `3.10`–`3.14` (section 4.1).
- `Makefile` with all targets (section 4.1).
- `.pre-commit-config.yaml` (section 4.2.3).
- `.readthedocs.yaml` (section 4.5.2).
- `mkdocs.yml` (stub — enough for RTD to build something trivial).
- `.gitignore` (section 4.1).
- `LICENSE` (BSD-3-Clause).
- `README.md` (stub with badges — see section 4.4.5; badges may initially
  404, that's fine).
- `CHANGELOG.md` with initial `## Unreleased` + six category
  sub-headers (section 4.4.4).
- `CONTRIBUTING.md` with `make dev-setup` instructions.
- `badges/` directory (empty; first badge generated at first
  release).

## 5.1.3. CI/CD workflows

All workflows from section 4.4.2 must exist and be tested:

- `push_to_branch.yml`
- `pull_request_to_main.yml`
- `push_to_main.yml`
- `release_tag.yml`
- `_unit_tests.yml` (reusable)

Both composite actions from section 4.4.3:

- `unit_test`
- `validate_version_trigger`

## 5.1.4. Pull requests

Suggested split (each PR leaves the repo in a working state):

1. **Package scaffolding** — `pyproject.toml`, flat `click_prism/` package with `py.typed` and a stub `__version__`, `LICENSE`, `README` stub, `CHANGELOG` skeleton, `CONTRIBUTING` stub, `.gitignore`, `.python-version`, `.python-versions`, `uv.lock`.
2. **Local dev tooling** — `Makefile` with all targets, `.pre-commit-config.yaml`, verify `make dev-setup` works on a fresh clone.
3. **Non-release CI** — composite actions (`python_versions`, `unit_test`, `validate_version_trigger`), `_unit_tests.yml`, `push_to_branch.yml`, `pull_request_to_main.yml`, `push_to_main.yml`, Codecov upload.
4. **Release pipeline** — `release_tag.yml`, `scripts/release.py`, `scripts/extract_changelog.py`.
5. **Documentation setup** — `.readthedocs.yaml`, `mkdocs.yml` stub, `badges/` directory.
6. **Shakedown fixes (iterative)** — any PRs needed to resolve issues surfaced during `0.0.x` releases. Expected: 0–10 PRs depending on how many pipeline edge cases show up.

## 5.1.5. Expected release count

Best case: **2–3** `0.0.x` releases (first success, one fix, done).
Worst case: **10–15** `0.0.x` releases while pipeline edge cases
are shaken out.

`0.0.x` releases that are clean (working infrastructure, clear
"pre-implementation" framing) stay published. Only yank if a
release ships broken infrastructure or misleading content. See
section 5.0.5 for the as-shipped record.

## 5.1.6. Requirements newly satisfied

*(none — Phase 0 is infrastructure only)*

## 5.1.7. Exit criteria

**Manual setup actually completed** (catches missed items from section 5.1.1
before the first release attempt):

- [ ] GitHub repo is public.
- [ ] Branch protection on `main` is active, with the release
  maintainer listed as a bypass actor.
- [ ] Tag protection for `v*` tags is active.
- [ ] `prod` GitHub environment exists, has required reviewers,
  and is restricted to `v*` tags.
- [ ] PyPI trusted publisher is configured for
  `bertpl/click-prism` / `release_tag.yml` / `prod`.
- [ ] Read the Docs project is imported and webhook is active
  (a push to `main` triggers a build).

**Local tooling:**

- [ ] `make dev-setup` succeeds on a fresh clone.
- [ ] `make test` runs the trivial test and passes.
- [ ] `make coverage` runs the 4-run sequence and passes (100% on
  the trivial test).
- [ ] `make format` and `make lint` pass.
- [ ] `pre-commit run --all-files` passes.
- [ ] `make docs` builds the (stub) mkdocs site.
- [ ] `push_to_branch.yml` runs green on a feature branch push.
- [ ] `pull_request_to_main.yml` runs green on a PR (full matrix +
  lint + branch name check).
- [ ] `push_to_main.yml` runs green after merge (full matrix +
  Codecov upload).
- [ ] Read the Docs successfully builds and publishes the stub
  site.
- [ ] **A successful end-to-end release**: `make release
  VERSION=0.0.N` triggers `release_tag.yml`, which passes validation
  and tests, is manually approved in the `prod` environment,
  publishes the package to PyPI, and creates a GitHub Release with
  notes extracted from `CHANGELOG.md`.
- [ ] The published package is installable:
  `pip install click-prism==0.0.N` succeeds and `import click_prism`
  works.
- [ ] All five badges on the README resolve to their expected
  sources (CI status, PyPI version, Python versions, coverage,
  license).
