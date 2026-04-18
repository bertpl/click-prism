"""Mock: projex tree --help"""

from _render import render


def draw(c):
    c.print("Usage: projex tree [OPTIONS]")
    c.print()
    c.print("  Display the command tree.")
    c.print()
    c.print("Options:")
    c.print("  --depth INTEGER  Limit tree depth.")
    c.print("  --help           Show this message and exit.")


render("projex tree --help", draw)
