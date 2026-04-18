"""Mock: projex tree — unicode style (default)"""

from _render import render


def draw(c):
    c.print("projex")
    c.print("├── config    Manage configuration settings")
    c.print("│   ╰── get    Get a configuration value")
    c.print("╰── deploy    Deployment commands")
    c.print("    ╰── run    Run a deployment")


render("projex tree", draw)
