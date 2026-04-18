"""Post-process SVG to add a colored title bar and fix font references.

Supports both freeze-generated and Rich-generated SVGs.

Usage:
    python postprocess_svg.py input.svg output.svg [--bar-color '#252525'] [--bar-height 36]
"""

import argparse
import re


def add_title_bar(svg: str, bar_color: str, bar_height: int) -> str:
    # Match the first <rect .../> with a fill attribute — the background rect.
    # (Skip clip-path rects which appear earlier in Rich SVGs.)
    bg_match = re.search(r'<rect\s[^>]*fill="[^"]*"[^>]*/>', svg)
    if not bg_match:
        raise ValueError("Could not find background rect in SVG")

    bg_tag = bg_match.group(0)

    # Extract dimensions and border radius from the rect attributes.
    # Use \s prefix to match standalone attributes — avoids stroke-width
    # matching as width, or rx matching as x.
    w = re.search(r'\swidth="([\d.]+)"', bg_tag)
    h = re.search(r'\sheight="([\d.]+)"', bg_tag)
    r = re.search(r'\srx="([\d.]+)"', bg_tag)
    if not (w and h and r):
        raise ValueError(f"Could not parse background rect attributes: {bg_tag}")

    width = w.group(1)
    height = h.group(1)
    rx = r.group(1)

    # Detect x/y offset (Rich uses x="1" y="1"; freeze uses x="0.00px")
    x_match = re.search(r'\sx="([\d.]+)', bg_tag)
    y_match = re.search(r'\sy="([\d.]+)', bg_tag)
    x = x_match.group(1) if x_match else "0"
    y = y_match.group(1) if y_match else "0"

    # Clip to the window shape, then draw a bar across the top
    title_bar = (
        f'<defs><clipPath id="windowClip">'
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
        f'rx="{rx}" ry="{rx}"/>'
        f"</clipPath></defs>"
        f'<rect x="{x}" y="{y}" width="{width}" height="{bar_height}" '
        f'fill="{bar_color}" clip-path="url(#windowClip)"/>'
    )

    # Insert AFTER the complete background rect tag
    svg = svg.replace(bg_tag, bg_tag + title_bar, 1)

    return svg


def fix_fonts(svg: str) -> str:
    """Fix font-family case for resvg compatibility."""
    svg = svg.replace("font-family: arial", "font-family: Arial")
    return svg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Input SVG file")
    parser.add_argument("output", help="Output SVG file")
    parser.add_argument("--bar-color", default="#252525", help="Title bar color")
    parser.add_argument(
        "--bar-height", type=int, default=36, help="Title bar height in px"
    )
    args = parser.parse_args()

    with open(args.input) as f:
        svg = f.read()

    svg = fix_fonts(svg)
    svg = add_title_bar(svg, args.bar_color, args.bar_height)

    with open(args.output, "w") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
