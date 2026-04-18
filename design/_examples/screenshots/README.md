# Screenshot generation

Two pipelines for generating terminal screenshots as WebP images, both
sharing the same final stages (SVG post-processing, rasterization,
lossless WebP compression).

## Pipelines

### Real CLI output (`generate.sh`)

For the 0.2 analysis docs — captures actual command output from the
example CLIs.

```
command stdout (± ANSI) → _capture.py → Rich SVG + TXT
                                            ↓
                                    postprocess_svg.py (title bar + font fix)
                                            ↓
                                    resvg --zoom 2 → PNG
                                            ↓
                                    cwebp -lossless → WebP
```

`_capture.py` reads stdin, parses ANSI escape codes via Rich's
`Text.from_ansi()`, records to a `Console(record=True)`, and calls
`console.save_svg()`. This preserves all styling (bold, dim, italic,
colors) from the original command output.

### Mock output (`generate_mocks.sh`)

For the 1.3 UX docs — hand-crafted output simulating `click-prism` behavior
that doesn't exist yet.

```
mock script → Rich Console(record=True) → SVG + TXT
                                              ↓
                                      postprocess_svg.py (title bar + font fix)
                                              ↓
                                      resvg --zoom 2 → PNG
                                              ↓
                                      cwebp -lossless → WebP
```

Each mock script uses `_render.py` (shared helper) — defines a
`draw(console)` function and calls `render(title, draw)`. Rich markup
is used directly for styled mocks (bold group rows, dim descriptions,
colored names).

### Shared stages

- **`postprocess_svg.py`** — Inserts a darker title bar rect behind the
  traffic lights and fixes `font-family: arial` → `Arial` (resvg
  case-sensitivity workaround).
- **`resvg --zoom 2`** — Rasterizes SVG to 2x PNG with local Fira Code
  font (Regular + Bold weights).
- **`cwebp -lossless`** — Converts PNG to lossless WebP for smaller file
  sizes. PNG is deleted after conversion.

## Setup

```bash
# System tools (macOS)
brew install resvg webp
brew install --cask font-fira-code

# Python venv (from design/_examples/cli/)
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"   # includes Rich + all example CLI dependencies
```

## Running

```bash
cd design/_examples/screenshots

# 0.2 analysis screenshots (real CLI output)
./generate.sh
mv output/{click,cloup,rich}_*.{webp,txt} ../../0_analysis/2_status_quo/screenshots/

# 1.3 UX mocks (hand-crafted `click-prism` output)
./generate_mocks.sh
mv output/mock_*.{webp,txt} ../../1_vision/mocks/
```

## Why Rich SVG + resvg (and what didn't work)

The core requirement is rendering **bold text** in terminal screenshots —
critical for showing bold group rows in `click-prism`'s Rich-styled output.

### Evaluated and rejected

| Tool | Issue |
|---|---|
| **Charm freeze** | Bold is [commented out in source](https://github.com/charmbracelet/freeze/blob/main/ansi.go) (SGR code 1). Open PR #154 since Nov 2024, unmerged. Colors and dim work; bold does not. |
| **freeze + patched PR #154** | One-line fix, but building from an unmerged PR felt fragile for a dev workflow. |
| **termshot** | Renders bold correctly, but: no font control, no hi-res scaling, no title bar customization. Output looked chunky compared to freeze. |
| **rsvg-convert** (for SVG→PNG) | Breaks Rich SVG spacing — character positions in the `<text>` elements are misaligned, causing text to jam together (`configManage` instead of `config    Manage`). |

### Chosen: Rich `console.save_svg()` + resvg

- **Perfect bold fidelity** — Rich generates SVG from its internal
  `Segment` objects with exact `Style` info (font-weight 700 for bold).
  No ANSI parsing needed for mocks; ANSI round-trip via
  `Text.from_ansi()` for real CLI captures.
- **Fira Code with bold weight** — installed locally via Homebrew.
  Rich's SVG template references it via `local("FiraCode-Bold")`.
  resvg finds it through system font matching.
- **Built-in macOS chrome** — Rich's SVG includes traffic light circles
  and a title bar. `postprocess_svg.py` adds a darker title bar
  background (matching the freeze-era visual style).
- **Clean output** — SVG is vector; `resvg --zoom 2` produces 2x PNGs,
  then `cwebp -lossless` compresses to WebP.
- **resvg over rsvg-convert** — resvg correctly handles Rich's SVG text
  layout and font-weight. rsvg-convert does not (spacing bug above).

### Known resvg quirks

- `@font-face` rules in the SVG are ignored (resvg logs a warning).
  Fonts must be installed locally. This is fine — we install Fira Code
  via Homebrew.
- `font-family: arial` (lowercase, as Rich emits it) doesn't match the
  system font `Arial`. Fixed by `postprocess_svg.py` capitalizing it.
- Some `clip-path` values from Rich's SVG fail to parse (logged as
  warnings). No visible impact on output.
