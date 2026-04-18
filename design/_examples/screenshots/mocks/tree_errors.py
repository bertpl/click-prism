"""Mock: projex tree with a broken command (error node)"""

from _render import render


def draw(c):
    c.print("projex")
    c.print("├── config      Manage configuration settings")
    c.print("├── broken      (error: No module named 'heavylib')")
    c.print("╰── status      Show current project status")


render("projex tree", draw)
