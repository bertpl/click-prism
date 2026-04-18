"""Mock: projex tree --depth 1"""

from _render import render


def draw(c):
    c.print("projex")
    c.print("├── config      Manage configuration settings")
    c.print("├── deploy      Deployment commands")
    c.print("├── status      Show current project status")
    c.print("╰── tree        Display the command tree")


render("projex tree --depth 1", draw)
