"""Mock: projex --help-json (truncated to show structure)"""

import json

from _render import render

data = {
    "name": "projex",
    "type": "group",
    "help": "Projex \u2014 a project management tool.",
    "hidden": False,
    "deprecated": False,
    "options": [
        {
            "name": "version",
            "declarations": ["--version"],
            "is_flag": True,
            "help": "Show the version and exit.",
        }
    ],
    "children": [
        {
            "name": "config",
            "type": "group",
            "help": "Manage configuration settings.",
            "hidden": False,
            "deprecated": False,
            "arguments": [],
            "options": [],
            "children": [
                {
                    "name": "get",
                    "type": "command",
                    "help": "Get a configuration value.",
                    "hidden": False,
                    "deprecated": False,
                    "arguments": [
                        {"name": "key", "type": "TEXT", "required": True}
                    ],
                    "options": [],
                },
            ],
        },
    ],
}

text = json.dumps(data, indent=2)
# Append truncation hint
lines = text.split("\n")
output = lines[:-2] + ["    ...", "  ]", "}"]


def draw(c):
    for line in output:
        c.print(line, highlight=False)


render("projex --help-json", draw)
