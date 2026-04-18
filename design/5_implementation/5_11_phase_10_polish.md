# 5.11. Phase 10: Polish & 0.10.0

**Version:** `0.10.0`
**Goal:** Feature-complete, polished release. No new
requirements — everything is already satisfied by phase 9. This
phase completes the documentation, README, hero assets, and
performs a final sweep before the public launch.

## 5.11.1. Scope

### 5.11.1.1. Documentation site completion

Per section 4.5.3 — fill in the sub-pages of the MkDocs nav:

- **Home** (`index.md`): hero screenshot, one-line pitch, quick
  install, minimal example
- **Getting Started** (`getting_started.md`): install,
  `cls=PrismGroup` one-liner, what the user sees
- **User Guide**:
    - `guide/integration.md`: the three paths (`cls`,
      `add_command`, `show_tree` / `render_tree`) with examples
    - `guide/configuration.md`: `TreeConfig` fields, precedence,
      `.resolve()`, `.merge()`
    - `guide/rich.md`: `rich` support, `TreeTheme`, `rich-click`
      style conversion via `tree_theme_from_rich_click()`
      (opt-in), fallback behavior
    - `guide/composability.md`: `wrapping()`, manual MRO,
      ecosystem compatibility, information preservation
- **API Reference** (`reference.md`): auto-generated from
  docstrings via mkdocstrings (Google style, per section 4.5.1)
- **Compatibility** (`compatibility.md`): tested Group
  subclasses, known limitations
- **Changelog** (`changelog.md`): symlinked or included from
  repo-root `CHANGELOG.md`

### 5.11.1.2. Docstring sweep

- Every public symbol has a complete Google-style docstring
  (section 4.5.1)
- Examples in docstrings where relevant (mkdocstrings renders
  them nicely)
- No `# TODO` or `# FIXME` remaining in public API files

### 5.11.1.3. README polish

Final README structure (section 4.4.5 for the badges, plus content):

- Five badges (CI, PyPI version, Python versions, coverage,
  license)
- One-sentence pitch
- Hero screenshot / GIF (rendered tree output)
- Install: `pip install click-prism` (+ `[rich]` for the extras)
- 60-second quick-start with `cls=PrismGroup`
- Comparison table vs `click-command-tree` (the package we
  replace)
- Link to docs site
- Contributing link

### 5.11.1.4. Hero assets

- Hero screenshot showing a `rich`-styled tree from a realistic
  example CLI
- Optionally, an animated GIF showing `mycli --help` vs
  `mycli tree` side by side
- Stored under `badges/` alongside the coverage SVG (committed,
  frozen per tag — see section 4.4.5)

### 5.11.1.5. GitHub community-health files

Per section 4.1.7.1 — must exist before 0.10.0:

- `.github/ISSUE_TEMPLATE/` (bug report, feature request)
- `.github/pull_request_template.md`
- `SECURITY.md` (vulnerability reporting policy)

### 5.11.1.6. Final sweep

- Run the full test matrix across all 24 jobs
- Run `make coverage` locally, verify 100%
- Run `make lint` clean
- Run `make docs`, review the full site manually
- Manually test all three integration paths on a throwaway CLI
- Re-read the CHANGELOG from `0.1.0` onward for completeness
- Verify the PyPI listing renders the README correctly once
  `0.10.0` is published (do a dry-run with a `0.10.0rc1` if
  desired — but section 4.1's versioning scheme does not use
  pre-release suffixes, so this would need to be out-of-band
  or skipped)

### 5.11.1.7. Release

- `make release VERSION=0.10.0`
- Post-release: update the README badges to point to the
  `0.10.0` tag's frozen versions (automatic via the release
  script)
- Announce the release (not in scope for this document —
  marketing is separate from implementation)

## 5.11.2. Pull requests

Suggested split. Code changes in this phase are limited to adding docstrings to
public symbols; no new features or behavioral changes, so 100%
coverage is preserved by construction.

1. **Docstring sweep** — Google-style docstrings on all public
   symbols with examples where relevant; no `# TODO`/`# FIXME`
   left in public API files.
2. **User Guide pages** — `guide/integration.md`,
   `guide/configuration.md`, `guide/rich.md`,
   `guide/composability.md`.
3. **Landing + reference pages** — `index.md`,
   `getting_started.md`, `reference.md`, `compatibility.md`;
   changelog inclusion.
4. **README + hero asset** — final README content (badges,
   quick-start, comparison table), hero screenshot/GIF committed
   to `badges/`.
5. **Community-health files** — `.github/ISSUE_TEMPLATE/` (bug
   report, feature request), `.github/pull_request_template.md`,
   `SECURITY.md`.

## 5.11.3. Requirements newly satisfied

*(none — all 41 requirements satisfied by end of phase 9)*

## 5.11.4. Exit criteria

- [ ] Docs site complete: every nav entry has real content
- [ ] Every public symbol has a Google-style docstring with
  examples where relevant
- [ ] README has hero asset, 60-second quick-start, comparison
  table, and working badges
- [ ] Full test matrix passes
- [ ] `make coverage` reports 100%
- [ ] `make lint` clean
- [ ] `make docs` builds without warnings, site reviewed
  manually
- [ ] GitHub community-health files exist: issue templates, PR
  template, `SECURITY.md`
- [ ] All three integration paths manually verified on a
  throwaway CLI
- [ ] CHANGELOG reviewed for completeness from `0.1.0` through
  `0.9.0`
- [ ] `0.10.0` published to PyPI via the full release pipeline
- [ ] `click-prism` is installable via `pip install click-prism` and
  the PyPI page renders correctly
- [ ] Read the Docs is serving the `0.10.0` documentation at
  `click-prism.readthedocs.io`
