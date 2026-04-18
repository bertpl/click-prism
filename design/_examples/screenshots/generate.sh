#!/usr/bin/env bash
#
# Generate all screenshots for the plan documents.
#
# Output goes to ./output/ (.png + .txt). Plan documents reference local copies
# in their own subfolders — after regenerating, move the relevant files to the
# correct subfolder (see "After running" below).
#
# Pipeline: command output → _capture.py (Rich SVG + TXT) → postprocess
#           (title bar + font fix) → resvg (hi-res PNG)
#
# ── First-time setup ────────────────────────────────────────────────────────
#
#   1. Install system tools (macOS):
#        brew install resvg
#        brew install --cask font-fira-code
#
#   2. Create and populate the Python venv:
#        cd design/_examples/cli
#        python3 -m venv .venv
#        source .venv/bin/activate
#        pip install -e ".[all]"
#
#   Both steps only need to be done once. If new packages are added to
#   pyproject.toml's [all] extra later, re-run the pip install line.
#
# ── Running ──────────────────────────────────────────────────────────────────
#
#   cd design/_examples/screenshots
#   ./generate.sh
#
# ── After running ────────────────────────────────────────────────────────────
#
#   Move the generated files to the plan document screenshot folders:
#
#     0.2 screenshots → design/0_analysis/2_status_quo/screenshots/
#
#   Example (move everything):
#     mv output/{click,cloup,rich}_*.{webp,txt} ../../0_analysis/2_status_quo/screenshots/
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI_DIR="$SCRIPT_DIR/../cli"
OUT_DIR="$SCRIPT_DIR/output"
CAPTURE="$SCRIPT_DIR/_capture.py"
POSTPROCESS="$SCRIPT_DIR/postprocess_svg.py"

# Title bar settings
BAR_COLOR="#252525"
BAR_HEIGHT=36
ZOOM=2

# Activate venv
source "$CLI_DIR/.venv/bin/activate"

mkdir -p "$OUT_DIR"

# Pipeline: run command → capture to SVG+TXT → postprocess → resvg → PNG
_render() {
    local name="$1"
    local title="$2"
    shift 2

    echo "  $name"

    # Run command and capture output to Rich SVG + TXT
    "$@" | python "$CAPTURE" "$OUT_DIR/$name.svg" --title "$title"

    # Post-process: add title bar, fix font case
    python "$POSTPROCESS" \
        "$OUT_DIR/$name.svg" "$OUT_DIR/$name.svg" \
        --bar-color "$BAR_COLOR" --bar-height "$BAR_HEIGHT"

    # Convert to PNG (intermediate)
    resvg --zoom "$ZOOM" \
        "$OUT_DIR/$name.svg" "$OUT_DIR/$name.png" \
        2>/dev/null

    # Convert to lossless WebP (final)
    cwebp -lossless -quiet "$OUT_DIR/$name.png" -o "$OUT_DIR/$name.webp"

    # Clean up intermediates
    rm "$OUT_DIR/$name.svg" "$OUT_DIR/$name.png"
}

# Screenshot plain CLI output
screenshot() {
    local name="$1"
    local title="$2"
    shift 2
    _render "$name" "$title" bash -c "cd '$CLI_DIR' && $*"
}

# Screenshot CLI output with ANSI colors (Rich, rich-click, etc.)
screenshot_color() {
    local name="$1"
    local title="$2"
    shift 2
    _render "$name" "$title" bash -c "cd '$CLI_DIR' && FORCE_COLOR=1 $*"
}

# Screenshot a command that exits non-zero (captures stderr too)
screenshot_err() {
    local name="$1"
    local title="$2"
    shift 2
    _render "$name" "$title" bash -c "cd '$CLI_DIR' && ($* 2>&1 || true)"
}

echo "Generating screenshots..."

# 0.2.A — Core packages
echo "Core packages:"
screenshot       "click_help"        "projex --help"       "python example_cli.py --help"
screenshot       "click_help_deploy" "projex deploy --help" "python example_cli.py deploy --help"
screenshot_color "rich_tree"         "python show_tree.py"  "python example_rich_tree.py"

# 0.2.B — Competing packages
echo "Competing packages:"
screenshot       "click_command_tree" "projex tree"         "python example_click_command_tree.py tree"

# 0.2.C — Related packages
echo "Related packages:"
screenshot_color "rich_click_help"        "projex --help"        "python example_rich_click.py --help"
screenshot_color "rich_click_help_deploy" "projex deploy --help" "python example_rich_click.py deploy --help"
screenshot       "cloup_help"             "projex --help"        "python example_cloup.py --help"
screenshot_color "click_extra_help"        "projex --help"        "python example_click_extra.py --help"
screenshot       "click_help_colors_help" "projex --help"        "python example_click_help_colors.py --help"
screenshot_err   "click_didyoumean_err"   "projex stat"          "python example_click_didyoumean.py stat"
screenshot       "click_default_group_noarg" "projex"             "python example_click_default_group.py"
screenshot       "click_default_group_help"  "projex --help"      "python example_click_default_group.py --help"
screenshot       "click_aliases_help"     "projex --help"        "python example_click_aliases.py --help"

echo "Done. Screenshots in: $OUT_DIR/"
