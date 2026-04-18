# 1.1.2. Competing Packages

> Research date: 2026-04-05

Packages that provide tree visualization of Click command hierarchies. After
exhaustive searching of PyPI, GitHub, and the click-contrib organization, **two
dedicated packages exist**: `click-command-tree` (functional but inactive,
section 1.1.2.1) and `click-tree` (single-release experiment with no traction,
section 1.1.2.2).

## 1.1.2.1. click-command-tree

The more established of the two existing packages providing tree visualization of
Click CLIs, and the only one with real-world usage.

### 1.1.2.1.1. Identity

| Field | Value |
|---|---|
| Package | `click-command-tree` |
| PyPI | https://pypi.org/project/click-command-tree/ |
| GitHub | https://github.com/whwright/click-command-tree |
| Author | Harrison Wright (@whwright) |
| License | MIT |

### 1.1.2.1.2. Metrics

| Metric | Value |
|---|---|
| Latest version | 1.2.0 (2024-03-25) |
| First release | 1.0.0 (2019-02-08) |
| Total releases | 5 over ~5 years |
| GitHub stars | 12 |
| Forks | 2 |
| Total commits | 40 |
| Contributors | 2 |
| Monthly downloads | ~245k |
| Python support | 3.8–3.12 (CI-tested; not declared in classifiers) |
| Click support | 5.1–8.1.x |
| Last code change | 2024-03-25 |
| Last commit | 2024-10-02 (README update) |
| Open issues | 1 (stale since 2022) |
| Maintenance status | [Inactive](https://snyk.io/advisor/python/click-command-tree) (per Snyk Advisor) |

### 1.1.2.1.3. How it works

Single Python file (~73 lines). Registers as a `click-plugins` entry point under the
`click_command_tree` group. Consumers use it via `click-plugins`' `@with_plugins()` decorator.

Core components:

1. `tree` command — the entry point
2. `_CommandWrapper` — wraps Click commands with a `children` list
3. `_build_command_tree()` — recursive walk of `click.core.Group` instances
4. `_print_tree()` — renders with Unicode box-drawing characters, alphabetical sort
5. `_get_truncated_docstring()` — first line of `__doc__`, hardcoded 80-char truncation

Example output:

```
root
├── command-group
│   └── nested-command
├── standard-command
└── tree - show the command tree of your CLI
```

### 1.1.2.1.4. Features

- Recursive tree display of all commands/groups
- Unicode box-drawing characters
- Short help text alongside command names
- Hidden command filtering
- Alphabetical sorting
- Broad Click version support (5.1–8.1.x)

### 1.1.2.1.5. Limitations

- No color/styling — plain text only
- No depth control — always renders full tree
- No filtering — no name filter, no commands-only/groups-only
- No parameter display — only shows command names and docstrings
- Requires `click-plugins` — integration via `@with_plugins()` decorator
- Hardcoded 80-char truncation — not configurable
- No output format options — no JSON, Markdown, etc.
- No programmatic API — CLI-only, no importable functions
- Alphabetical sort only — cannot preserve declaration order
- Not tested on Python 3.13+ or Click 8.2+
- Hardcoded command name — `tree` cannot be renamed

### 1.1.2.1.6. Dependencies

- `click` (loosely pinned)
- Integrates via `click-plugins` (itself effectively abandoned — maintainers recommend vendoring)

## 1.1.2.2. click-tree

A dedicated tree-visualization package with no activity since its initial release
and effectively zero adoption.

### 1.1.2.2.1. Identity

| Field | Value |
|---|---|
| Package | `click-tree` |
| PyPI | https://pypi.org/project/click-tree/ |
| GitHub | https://github.com/adammillerio/click-tree |
| Author | Adam Miller (@adammillerio) |
| License | MIT |

### 1.1.2.2.2. Metrics

| Metric | Value |
|---|---|
| Latest version | 0.0.1 (2024-05-21) |
| First release | 0.0.1 (2024-05-21) |
| Total releases | 1 |
| GitHub stars | 0 |
| Forks | 0 |
| Total commits | 7 (all on 2024-05-20 – 2024-05-21) |
| Contributors | 1 |
| Monthly downloads | ~24 |
| Python support | 3.10–3.12 (classifiers only; `requires_python` not declared) |
| Click support | unpinned (any version accepted by the dependency spec) |
| Last code change | 2024-05-21 |
| Last commit | 2024-05-21 |
| Open issues | 0 |
| Maintenance status | Single-commit-burst release; no subsequent activity |

### 1.1.2.2.3. How it works

Integration centers on a `ClickTreeParam` — a `click.Option` subclass added to
the root group that attaches a `--tree` flag; invoking the flag prints the tree
and exits. An alternative programmatic path exposes `get_tree()` for direct use.
Tree construction and rendering are delegated to the third-party `anytree`
library.

Core components:

1. `ClickTreeParam` — a custom `click.Option` exposing `--tree` on the root group
2. `get_tree(obj, argv=None, scoped=False, ignore_names=...)` — builds and returns
   an `anytree.Node` tree
3. Rendering via `anytree.RenderTree` with an `anytree` ASCII style

Usage sketch (parameter approach, as recommended by the README):

```python
import click
from click_tree import ClickTreeParam

@click.group(cls=click.Group)
@click.option("--tree", is_flag=True, cls=ClickTreeParam)
def cli(tree: bool) -> None: ...
```

### 1.1.2.2.4. Features

- Recursive tree display of commands and groups
- Optional scoping (`scoped=True`) — restricts output to the subtree rooted at
  the current invocation path
- Command filtering via `ignore_names`
- ASCII styles configurable through `anytree`'s render-style parameter
- Invocation pattern: root-level `--tree` flag (not a subcommand)

### 1.1.2.2.5. Limitations

- Requires `anytree` as a mandatory runtime dependency (second tree-data
  library in the process, alongside Click's own internal `Group` tree)
- No color/styling — plain ASCII only; no Rich integration
- No depth control
- No parameter display — command names only, no option/argument surfacing
- No output format options (JSON, Markdown, etc.)
- Integration constraint: the tree is reachable only via a flag on the root
  group, not addable as a subcommand and not a `Group` subclass users can
  opt into
- No compatibility matrix: `requires_python` is not set and the `click`
  dependency is unpinned, despite the "Development Status :: 5 -
  Production/Stable" classifier (contradicted by the `0.0.1` version)
- Single release with zero post-release activity — effectively abandoned
- 0 stars, 0 forks, 0 open issues — no evidence of real-world users

### 1.1.2.2.6. Dependencies

- `click` (unpinned)
- `anytree` (unpinned, required) — pulls in a general-purpose tree
  data-structure library where Click's own group/command hierarchy is
  already a tree

## 1.1.2.3. Packages investigated and ruled out

The following packages appeared in searches but do **not** provide tree visualization
of Click command hierarchies:

| Package | What it actually does | Why not a competitor |
|---|---|---|
| `rich-click` | `rich`-formatted help output | Flat command panels, not recursive tree |
| `click-extra` | Config files, colorized help, `--show-params` | Parameter introspection, not tree visualization |
| `sphinx-click` | Sphinx documentation from Click apps | Build-time docs generation, not runtime CLI |
| `click-inspect` | Create Click options from function params | Unrelated to tree visualization |
| `click-plugins` | Entry-point plugin registration | Infrastructure, not a visualizer |
| `Typer` | CLI framework built on Click | No tree command (Typer apps are Click apps under the hood) |
| `click-help-all` | N/A | **Does not exist.** Phantom reference. |

### 1.1.2.3.1. General-purpose tree rendering (not Click-specific)

| Package | Downloads | Notes |
|---|---|---|
| `rich` (`rich.tree.Tree`) | — | General-purpose tree rendering widget (see section 1.1.1 for details) |
| `treelib` | — | Generic tree data structure |
| `tree-format` | — | Console tree formatting |
| `pipdeptree` | — | Package dependency trees, not CLI trees |
| `asciitree` | — | ASCII tree rendering |

None of these provide tree visualization of Click command hierarchies.

## 1.1.2.4. Summary

The competitive landscape is essentially empty. `click-command-tree` is functional
but inactive, with significant feature gaps; its ~245k monthly downloads despite
only 12 GitHub stars suggest automated/CI inclusion rather than active user choice.
`click-tree` (Adam Miller) is a single-day commit burst with zero stars, zero
forks, and ~24 monthly downloads — no meaningful adoption, no iteration, and an
integration model limited to a root-level `--tree` flag. Neither package provides Rich integration, parameter display, depth control,
JSON output, or a `Group`-subclass integration path. No other package fills this
niche.
