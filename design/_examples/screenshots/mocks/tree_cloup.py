"""Mock: projex tree (with Cloup — sections preserved in tree output)

Cloup sections become visual headings, each with its own tree fragment.
"""

from _render import render


def draw(c):
    c.print("projex")
    c.print("  Infrastructure:")
    c.print("  ├── config         Manage configuration settings")
    c.print("  │   ├── get          Get a configuration value")
    c.print("  │   ├── set          Set a configuration value")
    c.print("  │   ╰── list         List all configuration values")
    c.print("  ╰── deploy         Deployment commands")
    c.print("      ├── run          Run a deployment")
    c.print("      ╰── rollback     Roll back to a previous version")
    c.print("  Info:")
    c.print("  ╰── status         Show current project status")


render("projex tree", draw)
