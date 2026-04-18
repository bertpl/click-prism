"""Mock: projex deploy --help (tree-as-help on all groups)"""

from _render import render


def draw(c):
    c.print("Usage: projex deploy [OPTIONS] COMMAND [ARGS]...")
    c.print()
    c.print("  Deployment commands.")
    c.print()
    c.print("Options:")
    c.print("  --help  Show this message and exit.")
    c.print()
    c.print("Commands:")
    c.print("  projex deploy")
    c.print("  ├── run           Run a deployment")
    c.print("  ╰── rollback      Roll back to a previous version")


render("projex deploy --help", draw)
