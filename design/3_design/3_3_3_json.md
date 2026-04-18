# 3.3.3. Rendering: JSON

Machine-readable CLI hierarchy for tooling, agents, and automation.

## 3.3.3.1. Schema

```json
{
  "name": "projex",
  "type": "group",
  "help": "Projex — a project management tool.",
  "hidden": false,
  "deprecated": false,
  "is_default": false,
  "aliases": [],
  "section_name": null,
  "arguments": [],
  "options": [
    {
      "name": "version",
      "declarations": ["--version"],
      "type": "TEXT",
      "required": false,
      "is_flag": true,
      "multiple": false,
      "default": null,
      "help": "Show the version and exit.",
      "choices": null
    }
  ],
  "children": [
    {
      "name": "config",
      "type": "group",
      "help": "Manage configuration settings.",
      "hidden": false,
      "deprecated": false,
      "is_default": false,
      "aliases": [],
      "section_name": null,
      "arguments": [],
      "options": [],
      "children": [ ... ]
    }
  ]
}
```

Maps directly from `TreeNode` and `ParamInfo` (section 3.2).

### 3.3.3.1.1. Splitting `params` into `arguments` and `options`

`TreeNode.params` is a single ordered list of `ParamInfo` entries
(section 3.2) — Click stores arguments and options in definition order,
and the tree model preserves that order. The JSON renderer
partitions the list by `param_type`, preserving relative order
within each partition:

```python
arguments = [p for p in node.params if p.param_type == "argument"]
options   = [p for p in node.params if p.param_type == "option"]
```

This is the only place the two kinds are split — everywhere else
in the design (plain text and `rich` renderers, config) they stay
in the unified `params` list.

### 3.3.3.1.2. Error nodes

When a command cannot be loaded during traversal (R40), its node
is serialized with only `name`, `type`, and `error_message` — all
other fields are absent:

```json
{
  "name": "broken-cmd",
  "type": "error",
  "error_message": "cannot import name 'MyCommand' from 'mymodule'"
}
```

Omitting the error node silently would violate the principle of
surfacing failures rather than hiding them (section 2.2). Consumers must
handle nodes where `type == "error"`.

## 3.3.3.2. Inclusion rules

| Aspect | Visual tree | JSON |
|---|---|---|
| Depth | Respects config / `--depth` | Always full |
| Hidden commands | Excluded by default | Always included |
| Deprecated | Always included | Always included |
| Tree subcommand | Included | Included |
| Parameters | Only when `show_params` | Always included |
| Error nodes | `(error: msg)` inline | Included as `"type": "error"` |

JSON always produces the complete CLI surface. This is guaranteed
architecturally: JSON call paths pass the complete tree from
`build_tree()` directly to the renderer, skipping `filter_tree()`
(section 3.2.5). `depth` and `show_hidden` are irrelevant because the
filtering step that consults them is never invoked. `show_params`
is a visual layout concern — JSON always includes all parameters
as structured arrays regardless.

## 3.3.3.3. Output

- Valid JSON to stdout, 2-space indent, UTF-8
- `--help-json`: replaces all visual output, then `ctx.exit(0)`
- `show_tree(cli, format="json")`: same output, no CLI context
  needed

Both paths use the same renderer and produce identical output.
