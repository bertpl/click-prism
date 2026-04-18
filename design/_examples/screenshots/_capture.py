"""Capture stdin (possibly ANSI-styled) and save as Rich SVG + plain TXT.

Used by generate.sh to screenshot real CLI command output via the same
Rich+resvg pipeline as the mock scripts.

Usage:
    python example_cli.py --help | python _capture.py output.svg --title "projex --help"
    FORCE_COLOR=1 python example_rich_click.py --help | python _capture.py output.svg --title "projex --help"
"""

import argparse
import re
import sys

from rich.console import Console
from rich.terminal_theme import MONOKAI
from rich.text import Text

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg_path", help="Output SVG path (.txt saved alongside)")
    parser.add_argument("--title", default="Terminal", help="Title bar text")
    args = parser.parse_args()

    raw = sys.stdin.read().rstrip("\n")
    lines = raw.split("\n")

    console = Console(record=True, width=100)
    console.print(f"> {args.title}\n")
    for line in lines:
        console.print(Text.from_ansi(line), highlight=False)

    # Save plain-text version first (save_svg clears the record buffer)
    txt_path = args.svg_path.rsplit(".", 1)[0] + ".txt"
    with open(txt_path, "w") as f:
        f.write(console.export_text(clear=False))

    console.save_svg(args.svg_path, title=args.title, theme=MONOKAI)


if __name__ == "__main__":
    main()
