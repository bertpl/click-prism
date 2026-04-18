"""Shared rendering helper for mock screenshots.

Each mock script defines a draw(console) function and calls render().
This module handles SVG + TXT generation via Rich's Console.

Usage in mock scripts:
    from _render import render

    def draw(c):
        c.print("projex")
        c.print("[bold cyan]config[/bold cyan]  ...")

    render("projex tree", draw)
"""

import sys

from rich.console import Console
from rich.terminal_theme import MONOKAI


def render(title: str, draw_fn, width: int = 100):
    """Record console output and save SVG + TXT.

    Args:
        title: Shown in the macOS title bar (e.g., "projex tree").
        draw_fn: Callable(console) that prints the mock output.
        width: Console width in columns.
    """
    svg_path = sys.argv[1]

    console = Console(record=True, width=width)
    console.print(f"> {title}\n")
    draw_fn(console)

    # Save plain-text version first (save_svg clears the record buffer)
    txt_path = svg_path.rsplit(".", 1)[0] + ".txt"
    with open(txt_path, "w") as f:
        f.write(console.export_text(clear=False))

    console.save_svg(svg_path, title=title, theme=MONOKAI)
