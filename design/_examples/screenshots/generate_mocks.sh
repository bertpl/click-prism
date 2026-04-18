#!/usr/bin/env bash
#
# Generate mock screenshots for the UX plan documents (1.3.A–C).
#
# These are hand-crafted output mocks — click-prism doesn't exist yet, so
# we simulate what the output should look like.
#
# Pipeline: Rich console.save_svg() → postprocess (title bar + font fix)
#           → resvg (hi-res PNG)
#
# ── First-time setup ────────────────────────────────────────────────────────
#
#   1. Install system tools (macOS):
#        brew install resvg
#        brew install --cask font-fira-code
#
#   2. Python venv must have Rich installed:
#        cd design/_examples/cli
#        source .venv/bin/activate
#        pip install rich    # (already included in [all] extra)
#
# ── Running ──────────────────────────────────────────────────────────────────
#
#   cd design/_examples/screenshots
#   ./generate_mocks.sh
#
# ── After running ────────────────────────────────────────────────────────────
#
#   Move the generated files to the plan document mock folder:
#
#     mv output/mock_*.{webp,txt} ../../1_vision/mocks/
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI_DIR="$SCRIPT_DIR/../cli"
MOCK_DIR="$SCRIPT_DIR/mocks"
OUT_DIR="$SCRIPT_DIR/output"
POSTPROCESS="$SCRIPT_DIR/postprocess_svg.py"

# Title bar settings
BAR_COLOR="#252525"
BAR_HEIGHT=36
ZOOM=2

# Activate venv (needed for Rich)
source "$CLI_DIR/.venv/bin/activate"

# Make _render.py importable from mock scripts
export PYTHONPATH="$MOCK_DIR"

mkdir -p "$OUT_DIR"

# Pipeline: mock script (SVG+TXT) → postprocess SVG → resvg → PNG
mock() {
    local name="$1"
    local script="$2"

    echo "  $name"

    # Mock script generates SVG + TXT via Rich console.save_svg()
    python "$MOCK_DIR/$script" "$OUT_DIR/$name.svg"

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

echo "Generating mock screenshots..."

# 1.3.A — Plain Click
echo "1.3.A — Integration paths:"
mock "mock_tree_plain"           tree_plain.py
mock "mock_help_tree"            help_tree.py
mock "mock_show_tree"            show_tree.py

echo "1.3.A — Runtime controls:"
mock "mock_tree_subcommand_help" tree_subcommand_help.py
mock "mock_tree_depth1"          tree_depth1.py

echo "1.3.A — Configuration:"
mock "mock_tree_unicode_style"   tree_unicode_style.py
mock "mock_tree_ascii_style"     tree_ascii_style.py
mock "mock_tree_show_hidden"     tree_show_hidden.py
mock "mock_tree_deprecated"      tree_deprecated.py
mock "mock_tree_renamed"         tree_renamed.py

echo "1.3.A — Tree-as-help:"
mock "mock_deploy_help_flat"     deploy_help_flat.py
mock "mock_deploy_help_tree"     deploy_help_tree.py

echo "1.3.A — Machine-readable:"
mock "mock_help_json"            help_json.py

echo "1.3.A — Parameter display:"
mock "mock_tree_show_params"     tree_show_params.py

echo "1.3.A — Edge cases:"
mock "mock_tree_errors"          tree_errors.py
mock "mock_deploy_tree"          deploy_tree.py

# 1.3.B — Rich
echo "1.3.B — Rich:"
mock "mock_tree_rich"               tree_rich.py
mock "mock_tree_rich_default_params" tree_rich_default_params.py
mock "mock_tree_rich_themed"        tree_rich_themed.py
mock "mock_tree_rich_spring"        tree_rich_spring.py

# 1.3.C — Composability
echo "1.3.C — Composability:"
mock "mock_tree_cloup"           tree_cloup.py
mock "mock_tree_default_group"   tree_default_group.py
mock "mock_tree_aliases"         tree_aliases.py

echo "Done. Screenshots in: $OUT_DIR/"
