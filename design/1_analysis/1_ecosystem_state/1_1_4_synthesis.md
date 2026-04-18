# 1.1.4. Synthesis

Drawing from the ecosystem research in sections 1.1.1–1.1.3, this document identifies which
packages and versions are relevant to `click-prism` development.

## 1.1.4.1. Core package versions

**Principle:** support versions going back ~3–4 years where feasible. For Python
specifically, only support versions that are still officially supported (receiving
security fixes).

### 1.1.4.1.1. Python

| Version | Released | EOL | Supported (Apr 2026) |
|---|---|---|---|
| 3.9 | 2020-10 | 2025-10 | No |
| 3.10 | 2021-10 | 2026-10 | Yes |
| 3.11 | 2022-10 | 2027-10 | Yes |
| 3.12 | 2023-10 | 2028-10 | Yes |
| 3.13 | 2024-10 | 2029-10 | Yes |
| 3.14 | 2025-10 | 2030-10 | Yes |

Python 3.9 reached EOL in October 2025. The oldest still-supported version is **3.10**,
which also happens to align with the ~3–4 year window (released October 2021).

**Relevant Python versions: 3.10, 3.11, 3.12, 3.13, 3.14**

### 1.1.4.1.2. Click

| Version | Date | Python requires |
|---|---|---|
| 8.0.0 | 2021-05 | >=3.7 |
| 8.1.x | 2022–2024 | >=3.7 |
| 8.2.0 | 2025-05 | >=3.10 |
| 8.3.x | 2025-09+ | >=3.10 |

Click 8.0 is ~5 years old — outside the 3–4 year window but still widely deployed.
Click 8.1.x (2022–2024) is squarely within range. The core traversal API
(`list_commands()`, `get_command()`) is stable across all 8.x versions, so supporting
8.0+ is low-cost.

Click 8.0.x and 8.1.x support Python 3.7+, so users of those versions on Python 3.10+
(our minimum) are fully covered.

**Relevant Click versions: >=8.0**

### 1.1.4.1.3. Rich

| Version | Date | Python requires |
|---|---|---|
| 13.0.0 | 2022-12 | >=3.7 |
| 13.9.x | 2024-11 | >=3.8 |
| 14.0.0 | 2025-03 | >=3.8 |
| 14.3.3 | 2026-02 | >=3.8 |

`rich` 13.0 is ~3 years old and within range. The `rich.tree.Tree` API is stable
across both the 13.x and 14.x series. All `rich` 13.0+ versions support Python 3.10+.

**Relevant `rich` versions: >=13.0** (as optional dependency)

### 1.1.4.1.4. Cross-compatibility check

With Python >=3.10, Click >=8.0, `rich` >=13.0:

| Combination | Compatible? |
|---|---|
| Click 8.0.x + Python 3.10 | Yes (Click 8.0.x supports 3.7+) |
| Click 8.1.x + Python 3.10–3.14 | Yes (Click 8.1.x supports 3.7+) |
| Click 8.2.x+ + Python 3.10–3.14 | Yes (Click 8.2+ requires 3.10+) |
| `rich` 13.x + Python 3.10–3.14 | Yes (`rich` 13.0 requires 3.7+; later 13.x requires 3.8+) |
| `rich` 14.x + Python 3.10–3.14 | Yes (`rich` 14.x supports 3.8+) |

No conflicts. The only users excluded are those on Click 8.0.x/8.1.x *and*
Python 3.9 or below — but those Python versions are EOL.

## 1.1.4.2. Competitor

There is exactly one: **`click-command-tree`**.

The most significant improvement areas (based on its documented limitations in section 1.1.2):

- **No color/styling** — plain text only; no `rich` or ANSI support
- **Requires `click-plugins`** — an effectively abandoned dependency; the integration
  pattern (`@with_plugins()` + entry points) is more invasive than a simple
  `cls=` or `add_command()` call
- **No runtime configuration** — no depth control, no filtering, no way to rename
  the command, hardcoded 80-char truncation
- **No programmatic API** — CLI output only, no importable functions
- **Stale version support** — not tested on Python 3.13+ or Click 8.2+
- **Inactive maintenance** — classified inactive by Snyk; 40 commits over 7 years

## 1.1.4.3. Related packages: neighborhood analysis

From the packages cataloged in section 1.1.3, which ones would it make sense for a user to
use *alongside* `click-prism`? If a package enhances Click's help/UX and `click-prism` also
enhances Click's help/UX, a user is likely to want both — so being a "nice neighbor"
matters.

### 1.1.4.3.1. Relevant neighbors

These packages modify help presentation or Group behavior in ways that would
naturally coexist with tree visualization:

| Package | Monthly downloads | Why a user would combine it with a tree plugin |
|---|---|---|
| **`rich-click`** | ~41M | Already using `rich` for beautiful help → would want tree output to match |
| **`cloup`** | ~898k | Organizes commands into sections → would want tree to work with sectioned groups |
| **`click-extra`** | ~70k | Builds on `cloup` with extra features → same reasoning as `cloup` |
| **`click-help-colors`** | ~1.2M | Colorizes help → would want consistent visual treatment for tree output |
| **`click-didyoumean`** | ~44M | Improves UX with typo suggestions → tree visualization is another UX enhancement |
| **`click-default-group`** | ~7.9M | Sets a default subcommand → a tree command would be another subcommand alongside it |
| **`click-aliases`** | ~2.1M | Adds command aliases → tree should display aliased commands sensibly |

All of these provide custom Group subclasses — see the Group
subclass registry and method override matrix in section 1.1.3.

### 1.1.4.3.2. Not relevant as neighbors

These packages either don't provide Group subclasses, don't touch help formatting,
or have too little adoption to be worth considering:

| Package | Reason |
|---|---|
| `click-option-group` | Modifies Commands/Options, not Groups |
| `click-plugins` | Infrastructure (decorator pattern), no Group subclass |
| `click-rich-help` | Inactive, superseded by `rich-click` |
| `click-shell` | Low activity; overrides `invoke()` only, not help formatting |
| `click-repl` | No Group subclass; registers a subcommand only |
| `asyncclick` | Async fork; different use case |
