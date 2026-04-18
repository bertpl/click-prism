"""Mock: projex deploy tree (subtree scoping)"""

from _render import render


def draw(c):
    c.print("projex deploy")
    c.print("├── run           Run a deployment")
    c.print("╰── rollback      Roll back to a previous version")


render("projex deploy tree", draw)
