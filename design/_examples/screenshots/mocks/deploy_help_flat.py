"""Mock: projex deploy --help (standard Click flat format)"""

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
    c.print("  rollback  Roll back to a previous version.")
    c.print("  run       Run a deployment.")


render("projex deploy --help", draw)
