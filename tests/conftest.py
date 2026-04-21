import sys
from pathlib import Path
from typing import Any

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@pytest.fixture(scope="session")
def pyproject() -> dict[str, Any]:
    """Parsed pyproject.toml found by walking up from this file."""
    here = Path(__file__).resolve()
    for parent in [here, *here.parents]:
        candidate = parent / "pyproject.toml"
        if candidate.exists():
            return tomllib.loads(candidate.read_text())
    raise FileNotFoundError("No pyproject.toml found in any parent directory")
