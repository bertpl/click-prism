# 5.4. Phase 3: `--help-json`

**Version:** `0.3.0`
**Goal:** Complete R1 by adding the `--help-json` eager option.
Ships parameter extraction and JSON serialization — the first
machine-readable output path.

## 5.4.1. Scope

### 5.4.1.1. Parameter extraction (`_params.py`, `_model.py`)

**`_params.py`** (new):

- `ParamInfo` dataclass (section 3.2) — **Completes (from phase 1)**:
  phase 1's placeholder in `_config.py` is removed; real dataclass
  now lives in `_params.py`.
- `_extract_params()` — **Completes (from phase 1)**: phase 1's
  inline stub in `_model.py` is removed; real implementation now
  lives in `_params.py`.
- Extracts per-parameter metadata from `click.Parameter` objects:
    - name, type name (via `param.type.name`)
    - required, default, is_flag, multiple
    - declarations (e.g., `["-e", "--env"]`)
    - help text
    - choices (for `Choice` types only)
- Splits `cmd.params` into arguments vs options lists.

**`_model.py`** (modified):

- `_build_child()`: the inline `_extract_params()` stub is replaced
  by a call to `_params._extract_params()`. The `ParamInfo` import
  moves from `_config.py` to `_params.py`.
- `TreeNode.params` — **Completes (from phase 1)**: now populated
  with real parameter metadata.

### 5.4.1.2. JSON renderer (`_render_json.py`)

- Internal `tree_to_dict(node: TreeNode) -> dict` helper that
  converts a `TreeNode` to a JSON-serializable dict
- JSON serialization via `json.dumps(..., indent=2)`
- Always traverses at full depth, ignoring `TreeConfig.depth` and
  all filters (R2 explicitly requires this)
- Includes hidden + deprecated commands regardless of config
- Includes all parameters regardless of `show_params`
- Per section 3.3.3.1, the JSON output includes `is_default`,
  `aliases`, and `section_name` from this phase forward — these
  `TreeNode` fields have been populated via duck-typed discovery
  since phase 1 (section 5.2.1.1) and flow straight through
  `tree_to_dict`. Visual renderer consumption of the same fields
  remains deferred to phase 9 (section 5.10.1.5).
- Error nodes: `error_message` field replaces `arguments`/`options`/`children`

### 5.4.1.3. `--help-json` option (wiring in `_mixin.py`)

- `PrismMixin.make_context` override — **Active** (new in this
  phase; deferred from phase 2): appends the `--help-json` eager
  option to `self.params` when `parent is None`. Guards against
  re-entry so the option is appended at most once per instance.
- `PrismMixin._help_json_option` / `_help_json_callback` — **Active**
  (new in this phase; deferred from phase 2). The callback uses
  `TreeConfig().resolve()` (fresh — group config intentionally
  ignored, per section 3.4.1.1), builds the full tree, serializes
  to JSON, writes to stdout, exits cleanly.
- Only on the root group (not subgroups — see R2); enforced by
  the `parent is None` guard in `make_context`.

### 5.4.1.4. `show_tree` / `render_tree` — `format="json"` support

- `render_tree` / `show_tree` `format="json"` branch — **Completes
  (from phase 1)**: phase 1's `PrismError` placeholder is
  replaced by the real JSON path.
- `"json"` follows the same rules as `--help-json` (full depth,
  hidden + deprecated included, all parameters included).
- `render_tree(cli, format="json") -> str` returns the JSON as a
  string; `show_tree(cli, format="json")` prints it to stdout.

### 5.4.1.5. Public API additions

- No new exports. `render_tree` and `show_tree` are already public
  from phase 1 — this phase only widens their signatures to accept
  `format="json"`.
- `ParamInfo` and `tree_to_dict` stay internal helpers. Users who
  need a dict for programmatic walking use
  `json.loads(render_tree(cli, format="json"))`, which keeps the
  public surface minimal and the `TreeNode` / `ParamInfo` shapes
  free to evolve.

### 5.4.1.6. Not in this phase

- No runtime CLI flags on a tree subcommand (phase 4)
- No parameter display columns in text output (phase 6)
- No `rich` (phase 7)

## 5.4.2. Pull requests

Suggested split. Each PR ships code **with** its tests and leaves
the repo at 100% coverage.

1. **Parameter extraction** — `_params.py` with `ParamInfo`
   dataclass and extraction logic for all built-in Click types
   plus `Choice`; `_model.py` updated to call the real
   `_extract_params()` and drop the phase 1 inline stub (the
   `ParamInfo` import switches from `_config.py` to `_params.py`);
   plus unit tests covering every supported type and edge case
   (flags, multiple, defaults, custom `ParamType`).
2. **JSON renderer** — `_render_json.py` with serialization and
   the internal `tree_to_dict()` helper, plus JSON snapshot
   tests against the expected schema (including error nodes).
3. **`--help-json` eager option** — wire the option into
   `PrismMixin` / `PrismGroup`, root-only, plus integration tests
   verifying full-depth output regardless of config and exit
   behavior.
4. **Standalone functions — `format="json"`** — extend
   `show_tree` and `render_tree` with the `format` parameter,
   plus tests for both JSON paths (stdout via `show_tree`, return
   value via `render_tree`).

## 5.4.3. Tests

- Parameter extraction unit tests:
    - All built-in Click types (`STRING`, `INT`, `FLOAT`, `BOOL`,
      `UUID`, `Path`, `File`, `Tuple`, `IntRange`, `FloatRange`,
      `DateTime`)
    - Custom `click.ParamType` subclasses (uses `.name`)
    - `Choice` type with `choices` extraction
    - Flag vs non-flag options
    - Required vs optional
- JSON snapshot tests against an expected schema
- `--help-json` integration tests:
    - On a `PrismGroup` root, `--help-json` outputs full hierarchy
      and exits 0
    - Includes hidden + deprecated commands regardless of config
    - Includes all parameters
    - Ignores `depth` config
- `show_tree(cli, format="json")` standalone tests (writes JSON
  to stdout)
- `render_tree(cli, format="json")` standalone tests (returns
  JSON string)
- `tree_to_dict()` unit tests (internal helper)
- Error node serialization tests (error_message field populated)

## 5.4.4. Requirements newly satisfied

| Req | Notes |
|---|---|
| R1 | **Completes** — `cls=PrismGroup` now adds both tree-as-help (phase 2) and `--help-json` (this phase) |
| R2 | `--help-json` eager option on root, with all specified behaviors |
| R4 | **Completes** — `show_tree()` and `render_tree()` now support both text and JSON format |

## 5.4.5. Exit criteria

- [ ] `mycli --help-json` on a `PrismGroup` CLI outputs full tree as
  JSON and exits 0
- [ ] `show_tree(cli, format="json")` writes JSON to stdout
- [ ] `render_tree(cli, format="json")` returns the JSON string
- [ ] JSON output validates against the expected schema
- [ ] All parameter extraction edge cases tested
- [ ] Coverage is 100% on merged runs
- [ ] Full release pipeline succeeds for `0.3.0`
