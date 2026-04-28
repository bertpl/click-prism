from __future__ import annotations

import io
import sys

import pytest
from click_prism._environment import _detect_stdout_charset


class _StubStdout(io.StringIO):
    """Stand-in for sys.stdout with a configurable `encoding` attribute."""

    def __init__(self, encoding: str | None) -> None:
        super().__init__()
        self._encoding = encoding

    @property
    def encoding(self) -> str | None:
        return self._encoding


@pytest.mark.parametrize(
    ("encoding", "expected"),
    [
        ("utf-8", "unicode"),
        ("utf-16", "unicode"),
        ("ascii", "ascii"),
        ("latin-1", "ascii"),  # box-drawing char outside latin-1 → UnicodeEncodeError
    ],
)
def test_detect_stdout_charset_per_encoding(monkeypatch: pytest.MonkeyPatch, encoding: str, expected: str) -> None:
    # --- arrange ----------------------
    monkeypatch.setattr(sys, "stdout", _StubStdout(encoding))
    # --- act / assert -----------------
    assert _detect_stdout_charset() == expected


def test_detect_stdout_charset_unknown_codec(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unknown codec → LookupError → ascii fallback."""
    # --- arrange ----------------------
    monkeypatch.setattr(sys, "stdout", _StubStdout("definitely-not-a-real-codec"))
    # --- act / assert -----------------
    assert _detect_stdout_charset() == "ascii"


def test_detect_stdout_charset_no_encoding_attribute(monkeypatch: pytest.MonkeyPatch) -> None:
    """Some stdout-likes (e.g. captured) report `encoding=None`."""
    # --- arrange ----------------------
    monkeypatch.setattr(sys, "stdout", _StubStdout(None))
    # --- act / assert -----------------
    assert _detect_stdout_charset() == "ascii"
