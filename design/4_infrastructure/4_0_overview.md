# 4.0. Infrastructure Design Overview

> This section defines the project infrastructure: tooling, quality
> gates, test strategy, and CI/CD pipelines. It complements section 3
> (Package Design), which covers the shipping code.

## 4.0.1. Scope

**Build and quality infrastructure only.** Everything a contributor
or CI runner needs beyond the source code itself. Package design
decisions (APIs, data structures, module layout) are section 3's
concern.

**Final state.** Like section 3, this describes the target
infrastructure — not the order in which it is built. Phasing is
section 5's concern.

## 4.0.2. Rationale

### 4.0.2.1. Design principles

1. **Minimal tooling.** One tool per job. Every tool added is
   maintenance overhead.
2. **Instant feedback.** Pre-commit hooks must be sub-second.
   Anything slower belongs in CI, not the commit loop.
3. **Manual control over releases.** The developer decides when to
   release and what version to use. Automation handles validation
   and publishing, not decision-making.
4. **Hand-written changelogs.** Changelog entries are for users,
   not developers. They require curation — a commit message like
   `handle None in _pad_column` is not a useful release note.
5. **100% test coverage across configurations.** Optional
   dependencies (`rich`, `rich-click`) create mutually exclusive code
   paths. Coverage is measured by merging multiple test runs.
6. **Immutable release badges for version-specific facts.** README
   badges at a tagged version should reflect that version's stats
   (version, Python support, coverage, license), not main's current
   state. The CI badge is the exception — it stays dynamic because
   it reflects current project health, not a version-specific fact.
7. **Water-tight release pipeline.** Multiple gates — local
   validation, CI tests, environment approval, OIDC authentication
   — prevent unauthorized or broken releases.
8. **Configure tooling via `pyproject.toml` whenever possible.**
   This keeps all tool configuration in one place, discoverable
   and co-located with the package metadata. Tools that don't support
   it get a dedicated config file as a fallback — in our stack
   that's Codecov (`.codecov.yml`), pre-commit
   (`.pre-commit-config.yaml`), MkDocs (`mkdocs.yml`), and Read the
   Docs (`.readthedocs.yaml`).

### 4.0.2.2. Ecosystem alignment

These decisions are informed by how comparable open-source Python
packages operate (`httpx`, `rich`, `ruff`, `pydantic`, `fastapi`, `pip`, `numpy`,
`django`):

| Pattern | Ecosystem norm | click-prism |
|---|---|---|
| Branching | Trunk-based, no release branches | Same |
| Version bumping | Manual | Same |
| Changelog | Hand-written | Same |
| Release trigger | Tag push | Same |
| Conventional Commits | Not used (none of the surveyed packages) | Not enforced |
| Trusted Publishing | Standard for CI-published packages | Yes |
| GitHub environment | Standard with required reviewers | Yes |
| Type checker (`mypy`) | Mixed; many skip it | Not used (section 4.2.2) |

Release branches in the ecosystem (`numpy`, `django`) exist for
**multi-version maintenance** — backporting fixes to older release
series. `click-prism` has one active version; a release branch would
add complexity without benefit.

No comparable package uses Conventional Commits or automated
version bumping from commit messages. Manual version control with
hand-written changelogs is the clear norm, even for large,
frequently-released packages like `ruff`.

## 4.0.3. Tooling summary

| Concern | Tool | Reference |
|---|---|---|
| Build backend | `hatchling` | section 4.1 |
| Package manager | `uv` | section 4.1 |
| Formatting + linting | `ruff` | section 4.2.1 |
| Type checking | None (annotations for IDE/consumers only) | section 4.2.2 |
| Pre-commit hooks | `pre-commit` (`ruff` + hygiene hooks) | section 4.2.3 |
| Testing | `pytest` + `pytest-cov` + `syrupy` | section 4.3 |
| CI | GitHub Actions | section 4.4.2 |
| Badges | Dynamic on main, frozen at release (`genbadge` + shields.io) | section 4.4.5 |
| PyPI publishing | Trusted Publishing (OIDC) | section 4.4.6 |
| Documentation | MkDocs Material on Read the Docs | section 4.5 |

## 4.0.4. Contents

- **Project setup** (section 4.1) — pyproject.toml, `uv` and uv.lock,
  Makefile, `.python-version`, `.python-versions`, `.gitignore`,
  skeleton docs, PyPI setup.
- **Code quality** (section 4.2) — `ruff`, pre-commit hooks, branch naming,
  commit message recommendations.
- **Test infrastructure** (section 4.3) — `pytest` configuration, fixtures,
  24-job smart test matrix across Python 3.10–3.14 / Click / `rich`
  / ecosystem packages, multi-run coverage strategy, `syrupy`
  snapshot tests for rendered output.
- **CI/CD** (section 4.4) — GitHub Actions workflows, trunk-based release
  via tag push, `make release` process, badge freezing, release
  access control.
- **Documentation** (section 4.5) — MkDocs Material, Read the Docs, API
  reference via `mkdocstrings`.

## 4.0.5. Sub-sections

- [4.1. Project Setup](4_1_project_setup.md)
- [4.2. Code Quality](4_2_code_quality.md)
- [4.3. Test Infrastructure](4_3_test_infrastructure.md)
- [4.4. CI/CD](4_4_ci_cd.md)
- [4.5. Documentation](4_5_documentation.md)
