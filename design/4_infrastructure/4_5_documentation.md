# 4.5. Documentation

## 4.5.1. MkDocs Material

```yaml
# mkdocs.yml
site_name: click-prism
site_url: https://click-prism.readthedocs.io/
repo_url: https://github.com/bertpl/click-prism
repo_name: bertpl/click-prism

theme:
  name: material
  palette:
    - scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - content.code.annotate
    - content.code.copy
    - navigation.sections
    - toc.integrate

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [.]
          options:
            show_source: false
            members_order: source
            docstring_style: google
            merge_init_into_class: true
            show_root_heading: true
            show_root_full_path: false
            show_if_no_docstring: false
            filters:
              - "!^_"
              - "^__init__$"

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - admonition
  - pymdownx.details
  - attr_list
```

Stripped to the extensions `click-prism` actually needs — no
MathJax, no Mermaid.

**Docstring style**: Google (`Args:`, `Returns:`, `Raises:`
section headers), set via `docstring_style: google` in the
mkdocstrings config above. All public docstrings in the package
must follow this style so mkdocstrings renders them consistently.
Google is mkdocstrings' default, has the richest parser options,
and matches the dominant convention in modern Python libraries
(`rich`, `pydantic`, `rich-click`). Click itself uses Sphinx/reST style,
but matching Click's internal convention was judged less
important than aligning with the modern ecosystem and our
`rich`-adjacent positioning.

## 4.5.2. Read the Docs

```yaml
# .readthedocs.yaml
version: 2

build:
  os: ubuntu-24.04
  tools:
    python: "3.10"   # Matches .python-version (section 4.1) — local = minimum supported

python:
  install:
    - method: uv
      command: sync
      groups:
        - docs

mkdocs:
  configuration: mkdocs.yml
```

Uses RTD's native `uv` integration (`python.install` with
`method: uv`). Under the hood RTD runs `uv sync --group docs`
against the checked-out commit, which picks up the committed
`uv.lock` automatically. Docs dependencies live in
`[dependency-groups]` (section 4.1), keeping `rich` as the only
user-visible extra.

Hosted at `click-prism.readthedocs.io`. Builds automatically on
push to main and on release tags.

### 4.5.2.1. On `--frozen`

The native method runs `uv sync` without `--frozen`. `uv sync`
still respects `uv.lock` when it matches `pyproject.toml`, but
silently re-resolves on drift instead of failing loudly. That
safety net is redundant here: our primary CI (section 4.4.2) runs
`uv sync --frozen` on every commit before it reaches RTD, so
lockfile drift is caught upstream.

## 4.5.3. Doc structure

```yaml
# mkdocs.yml (nav section)
nav:
  - Home: index.md
  - Getting Started: getting_started.md
  - User Guide:
    - Integration Paths: guide/integration.md
    - Configuration: guide/configuration.md
    - rich Support: guide/rich.md
    - Composability: guide/composability.md
  - API Reference: reference.md
  - Compatibility: compatibility.md
  - Changelog: changelog.md
```

| Page | Content |
|---|---|
| Home | One-line pitch, hero screenshot, quick install, minimal example |
| Getting Started | Install, first `cls=PrismGroup`, what you see |
| Integration Paths | The three paths (cls, add_command, show_tree / render_tree) with examples |
| Configuration | TreeConfig fields, precedence, resolve/merge |
| `rich` Support | TreeTheme, `rich-click` style conversion via `tree_theme_from_rich_click()` (opt-in), fallback |
| Composability | wrapping(), manual MRO, ecosystem compatibility |
| API Reference | Single page: all public symbols auto-generated from docstrings via mkdocstrings |
| Compatibility | Tested Group subclasses, known limitations |
| Changelog | Symlinked or included from repo root `CHANGELOG.md` |

**Note**: The nav structure is tentative. During implementation,
the API Reference may be split into multiple pages if a single
page becomes too long to navigate, or the User Guide may be
restructured based on what reads best. The final structure is a
documentation concern revisited in section 5.

## 4.5.4. Docs dependency group

```toml
# pyproject.toml (also shown in section 4.1)
[dependency-groups]
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.0",
    "mkdocstrings[python]>=0.24",
]
```

Installed via `uv sync --group docs`. Not exposed as a
user-visible extra — `rich` is the only
`[project.optional-dependencies]` entry.

Local preview: `make docs && make show-docs`.
