"""Environment detection — what the runtime supports so we can degrade gracefully.

Centralizes "what context are we in?" probes: stdout encoding, optional
dependencies (e.g. `rich`), neighbour-package presence. Callers consult
these to pick the best-available rendering instead of hard-failing.
"""

from __future__ import annotations

import sys
from typing import Literal


def _detect_stdout_charset() -> Literal["unicode", "ascii"]:
    """Return the best tree charset the current terminal can render.

    Probes `sys.stdout.encoding` by attempting to encode a box-drawing
    glyph used in tree output. Not cached — `sys.stdout` is
    reassignable at runtime (capsys, redirected output, etc.) so a
    process-lifetime cache would be observably wrong.

    Returns:
        `"unicode"` if `sys.stdout.encoding` can encode the box-drawing
        glyphs the tree renderer uses, otherwise `"ascii"`.
    """
    encoding = sys.stdout.encoding or "ascii"
    try:
        "╰".encode(encoding)
    except (UnicodeEncodeError, LookupError):
        return "ascii"
    return "unicode"
