# 0. Conventions

Style, formatting, and content conventions for the plan
documents. Read this before editing any document in the series.

## 0.1. Headers and numbering

- All headers are numbered, up to six levels deep
  (e.g., `###### 3.3.0.2.1.1. Detail`). Header numbers always
  end with a dot. Numbers only — no letters at any level.
- The markdown heading level determines the numbering depth.
  Each document has exactly one H1 (the title) whose depth
  matches the file's position in the hierarchy — each
  subsequent heading level adds one number. Examples for a
  file named `3_3_rendering.md`:

  | Heading | Example | Number depth |
  |---|---|---|
  | H1 (title) | `# 3.3. Rendering` | 2 |
  | H2 | `## 3.3.1. Plain text` | 3 |
  | H3 | `### 3.3.1.1. Character sets` | 4 |
  | H4 | `#### 3.3.1.1.1. Unicode` | 5 |
  | H5 | `##### 3.3.1.1.1.1. Detail` | 6 (max) |

  A file at a different depth follows the same pattern:
  `0_conventions.md` has H1 at depth 1 (`# 0.`), while
  `1_1_1_core_packages.md` has H1 at depth 3 (`# 1.1.1.`).

- The H1 number matches the file name:
  `# 4.5. Title` lives in a file whose name starts with `4_5_`.
  Exception: `index.md` is exempt from numbering when it
  serves as a pure table-of-contents with no substantive
  content.
- Numbering starts at 1 by default at every level. Sections
  that represent a preamble, introduction, overview, or index
  start at 0 (e.g., `## 2.0. Overview`).
- Referring to sections: `See section 3.3.1` or
  `(section 3.3.1)` — always with the `section`
  qualifier. Plural: `sections 3.3.1, 3.3.2` for
  lists, `sections 3.3.1–3.3.3` for ranges (full
  numbers on each end, en-dash, no spaces). No
  trailing dot on the number.

## 0.2. Style conventions

### 0.2.1. Package names

Always backticked in prose, table body cells, and anywhere else
they appear as text. Use the PyPI name (e.g., `` `click-prism` ``,
not `` `click_prism` ``). Exceptions: headings/titles, code
blocks (already monospace), URLs, and table column-header
labels.

### 0.2.2. Code blocks

Always include a language tag: `` ```python ``,
`` ```toml ``, `` ```yaml ``, `` ```bash ``,
`` ```makefile ``, `` ```json ``, `` ```markdown ``,
`` ```gitignore ``. Use untagged `` ``` `` for plain-text
output, directory trees, or any content that does not
represent a specific programming language or syntax
(e.g., commit messages, branch names, flow diagrams).

### 0.2.3. Screenshots and output demos

Screenshot embed format:

```markdown
![alt_text](path/to/file.webp)
<!-- Textual output: path/to/file.txt -->
```

The `**End user: \`command\`**` label introduces a screenshot
or output demonstration.

### 0.2.4. Requirement references

Always `R` + number: R1, R25, R1–R5. Parentheses are
optional and follow normal prose punctuation — (R1),
(R1–R5), R37 requires this, etc. Never spell out
"Requirement" — always use the `R` prefix.

### 0.2.5. Ranges

En-dash without spaces: `3.10–3.14`, `phases 2–6`,
`2022–2024`. Never use a hyphen for ranges.

### 0.2.6. Em-dashes

Spaces on both sides: ` — `.

### 0.2.7. Horizontal rules

Do not use horizontal rules (`---`) as section separators.
Headers are visually distinct on their own; horizontal rules
add clutter.

### 0.2.8. Markdown compatibility

These rules ensure consistent rendering on GitHub (GFM):

- **4-space indent for nested lists.** GFM requires 4 spaces
  (not 2) to nest a list item under a parent; 2-space indent
  renders the child as a sibling.

  **CORRECT**:

  ```markdown
  - Parent
      - Child
  ```

  **WRONG** (Child renders as sibling, not nested):

  ```markdown
  - Parent
    - Child
  ```

- **Blank line before a list.** Always leave a blank line between
  prose and the first `- item`, including continuation prose
  inside a parent list item. A nested list placed directly under
  a parent marker (no intervening prose) does not need a blank
  line. Missing blank lines fold the would-be list into the
  preceding paragraph.

  **CORRECT** (direct nesting, no blank line needed):

  ```markdown
  - Parent
      - Nested
  ```

  **CORRECT** (prose + nested list, blank line separates them):

  ```markdown
  - Parent
    Prose.

      - Nested
  ```

  **WRONG** (prose + nested list without blank line — the nested
  bullets fold into the prose):

  ```markdown
  - Parent
    Prose.
      - Nested
  ```

- **No blank lines between list items** within the same list,
  unless every item has one. Mixing blank and non-blank gaps
  produces inconsistent spacing (some items get `<p>` wrapping,
  others don't).

  **WRONG**:

  ```markdown
  - A
  - B

  - C
  ```

- **Indented content under list items.** Code blocks, tables, or
  continuation paragraphs inside a list item must be indented to
  the item's content column — aligned with the first character
  after `- `. For a top-level `- Item`, that's col 2; for a nested
  `    - Item` (marker at col 4), col 6. Otherwise they break out
  of the list. Nested lists are a separate case: they use the
  4-space indent from rule 1, not the content column.

  **CORRECT**:

  ```markdown
  - Top-level item
    continuation at col 2

      - Nested item
        continuation at col 6
  ```

## 0.3. Content guidelines

- **No semantic forward references.** Do not use terms that are
  only introduced in a later section. Do not rely on design
  decisions that are made in a later section.
  **Exception — public API symbols in requirements/UX sections.**
  Requirements and UX documents (section 2) must propose concrete
  API names (`PrismGroup`, `TreeConfig`, `tree_command()`, etc.)
  to avoid vague, abstract specifications. These symbols are
  introduced informally in section 2 and defined formally in
  section 3. This is intentional: requirements precede design,
  and UX examples need specific names to be useful. Do not flag
  forward references of this type.
- **Navigational forward references are fine.** Pointing the
  reader ahead for context is useful: "we discuss this in more
  detail in section 3.3.1".
- **Avoid duplicating content**, especially literals (code
  blocks, package lists, folder structures). Duplication
  increases the risk of inconsistencies as documents are
  reviewed and edited. Only duplicate content when it
  significantly improves readability, and keep the duplication
  to the minimum needed for clarity. Otherwise, make a backward
  reference to where the content first appears.
