from __future__ import annotations

from typing import Any


def test_import(pyproject: dict[str, Any]) -> None:
    # --- arrange / act ----------------
    import click_prism

    # --- assert -----------------------
    assert click_prism.__version__ == pyproject["project"]["version"]
