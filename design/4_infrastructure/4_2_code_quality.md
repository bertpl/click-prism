# 4.2. Code Quality

## 4.2.1. Ruff

Single tool for formatting and linting (replaces `black` + `isort` +
`flake8`). Sub-second execution — suitable for pre-commit hooks.

```toml
# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py310"   # Minimum supported Python syntax. Matches
                           # requires-python in pyproject.toml and
                           # .python-version — see section 4.1 for the
                           # "local = minimum supported" rationale.

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "RUF"]
```

| Rule set | Purpose |
|---|---|
| `E`, `F` | `pycodestyle` + `pyflakes` (real errors) |
| `I` | `isort` (import ordering) |
| `UP` | `pyupgrade` (modern syntax) |
| `B` | bugbear (common pitfalls) |
| `SIM` | simplify (unnecessary complexity) |
| `RUF` | `ruff`-specific rules |

Intentionally excluded: `D` (docstrings — noisy for a small
package), `ANN` (annotation enforcement — not needed without a
type checker; see section 4.2.2).

## 4.2.2. No type checker

**mypy is not used.** The slow feedback loop it creates (CI-only,
or multi-second local runs) conflicts with the "instant feedback"
principle (section 4.0).

Type annotations are still written — they provide IDE support
(live checking via Pylance/Pyright in editors) and benefit
downstream users via the `py.typed` marker. But no type checking
tool runs in CI or locally.

This is viable because:

- 100% test coverage catches type errors that matter at runtime.
- `ruff`'s `UP` rules enforce modern type syntax.
- `click-prism`'s type surface is simple (no complex generics).
- IDEs provide live type feedback without a separate tool in the
  pipeline.

## 4.2.3. Pre-commit hooks

Design principle: **as few tools as possible, very fast.** The
commit loop must feel instant.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-yaml
      - id: check-toml
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]
        pass_filenames: true
      - id: ruff
        name: ruff check
        entry: uv run ruff check
        language: system
        types: [python]
        pass_filenames: true
```

Two repos (one remote, one local), six hooks. All sub-second.
No Node.js dependency.

| Hook | Stage | Purpose |
|---|---|---|
| `check-yaml`, `check-toml` | pre-commit | Syntax validation |
| `end-of-file-fixer`, `trailing-whitespace` | pre-commit | Hygiene |
| `ruff-format` | pre-commit | Code formatting (via `uv run`, uses `uv.lock`'s `ruff`) |
| `ruff` | pre-commit | Linting (via `uv run`, uses `uv.lock`'s `ruff`) |

No commit message validation hook. See section 4.2.5 for commit message
guidance.

### 4.2.3.1. Ruff version — single source of truth

`ruff` lives in `[dependency-groups] dev` in `pyproject.toml` with
a lower-bound constraint (`"ruff>=0.14"`). `uv.lock` resolves the
exact version and that's what the pre-commit hook invokes via
`uv run ruff`. There is **no independent `rev:` pin** for `ruff` in
`.pre-commit-config.yaml` — the `local` repo with
`language: system` shells out to the project venv, so whatever
`uv.lock` says is what the hook runs.

Consequences:

- `uv lock --upgrade` is the only place `ruff`'s version is bumped.
  No paired "bump pre-commit rev" PR — `make lint` and the
  pre-commit hook literally invoke the same `ruff` binary from the
  same venv.
- No drift risk between `make lint` / CI's `ruff` step / pre-commit.
- The pre-commit hook requires the project venv to exist. The
  documented setup order (section 4.1's `make dev-setup`) produces the
  venv before `pre-commit install` is called, so this is a
  non-issue in practice; on a bare checkout without `uv sync`,
  the hook fails loudly with a clear error rather than silently
  using a different `ruff` version.

The `pre-commit-hooks` repo itself stays pinned via `rev: v5.0.0`
— those are pre-commit-native mini-scripts (`check-yaml`,
`check-toml`, etc.) that aren't shipped in `uv.lock` and have no
Python-side analogue, so the `rev:` pin is unavoidable and
uncontentious.

## 4.2.4. Branch naming

Format: `<prefix>/<NN>-<short-slug>`

```
chore/01-package-scaffolding
feat/12-tree-mixin
fix/34-rich-fallback
docs/05-update-readme
refactor/18-extract-renderer
test/22-snapshot-fixtures
```

| Prefix | Use |
|---|---|
| `feat/` | New functionality |
| `fix/` | Bug fixes |
| `chore/` | Maintenance, CI, tooling |
| `docs/` | Documentation only |
| `refactor/` | Code restructuring without behavior change |
| `test/` | Test additions or changes |

Rules:

- Short-form prefixes, aligned with Conventional Commits naming
  (without adopting the rest of the spec).
- All lowercase.
- Hyphens as word separators (not underscores). Matches GitHub's
  auto-generated branch names.
- **`NN`** — two-digit zero-padded sequence number, continuous
  across all branches in the project. When a GitHub issue exists,
  its number replaces the sequence (`feat/42-…`).
- Keep under 50 characters.

Enforced via a CI check in `pull_request_to_main.yml` (section 4.4.2) that
validates the source branch name against the pattern
`^(feat|fix|chore|docs|refactor|test)/[a-z0-9-]+$`.

References:

- [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow)
- [git-check-ref-format](https://git-scm.com/docs/git-check-ref-format)

## 4.2.5. Commit messages

Commit messages are **not enforced by tooling**. No pre-commit hook
validates format. This follows the ecosystem norm — no surveyed
package enforces commit message structure.

### 4.2.5.1. Recommended style

Subject line uses the same short-form prefix as the branch
(section 4.2.4):

```
<prefix>: <imperative summary>
```

- **Prefix** — `feat`, `fix`, `chore`, `docs`, `refactor`, `test`.
  Matching the branch prefix is the common case but not required
  (e.g. a `chore/…` branch may contain a mix of `chore:` and
  `docs:` commits).
- **Summary** — imperative mood, lowercase, no trailing period,
  ideally under 72 characters.

Body (optional) explains the *why*, not just the *what*. Wrap at
~72 characters. Include issue references where applicable:

```
feat: add TreeTheme dataclass for Rich styling

Refs #15
```

```
fix: handle empty group crash in tree_help mode

The renderer assumed at least one child command existed.
Fixes #22
```

Issue references in the message body or footer (`Refs #15`,
`Fixes #22`) are picked up by GitHub for auto-linking and
auto-closing. These also make it easy to trace changes when
writing release notes.

This adopts the *prefix* from Conventional Commits without
adopting the rest of the spec (no scopes, no `BREAKING CHANGE`
footer, no machine parsing). The prefix gives commit-log
scannability and consistency with branch names.
