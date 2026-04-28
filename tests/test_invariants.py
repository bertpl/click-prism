"""Predictable-behavior invariant suite — no import-time side effects, no module-level mutable state.

These tests enforce a project-wide invariant: `import click_prism`
must be cheap, silent, and free of side effects. They stay green
through every release — any new code that violates the invariant
breaks one of these tests immediately rather than creating a
debugging session months later.

Why this invariant matters in practice:

- **Optional-dependency guarantee**: a user who installs `click-prism`
  without `rich` must still be able to `import click_prism` cleanly.
  Importing `rich` at module top-level would effectively force the
  optional extra on everyone, eroding the zero-required-deps promise.
- **CLI startup time**: every Click invocation imports the package.
  Import-time work compounds in shell-script and CI loops; users
  notice it in `time mycli --help` measurements.
- **Reproducibility**: module-level mutable state (caches, registries,
  configuration that mutates at runtime) creates ordering dependencies
  between unrelated test files and makes behaviour non-reproducible.
"""

from __future__ import annotations

import importlib
import pkgutil
import subprocess
import sys
from collections.abc import Iterator
from types import ModuleType

import click_prism


def _walk_click_prism() -> Iterator[ModuleType]:
    """Yield `click_prism` and every submodule reachable via `pkgutil.walk_packages`."""
    yield click_prism
    for _, name, _ in pkgutil.walk_packages(click_prism.__path__, prefix=click_prism.__name__ + "."):
        yield importlib.import_module(name)


def test_clean_subprocess_import() -> None:
    """`python -c "import click_prism"` produces no output and exits 0.

    Run in a fresh subprocess because pytest itself imports
    `click_prism` (other tests need it), so by the time this test
    runs `sys.modules` is already populated and an in-process import
    doesn't model a real first-import. A subprocess gives a clean
    interpreter where any stray `print()`, `warnings.warn()`,
    `logging.basicConfig()`, or environment probing surfaces as
    visible stdout/stderr.

    Rationale: import must be silent. Anything that prints or warns
    at import time pollutes the host CLI's error stream during
    normal use and breaks downstream tooling that consumes its output.
    """
    # --- arrange / act ----------------
    result = subprocess.run(
        [sys.executable, "-c", "import click_prism"],
        capture_output=True,
        text=True,
        check=False,
    )

    # --- assert -----------------------
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_optional_dependencies_not_imported() -> None:
    """`rich` is absent from `sys.modules` after a fresh `import click_prism`.

    Run in a subprocess for the same reason as
    `test_clean_subprocess_import`: pytest's own setup or other test
    files may have already imported `rich`, which would mask a
    regression where `click_prism` itself starts importing it
    eagerly. A subprocess starts from a clean `sys.modules` and
    asserts that `import click_prism` alone doesn't pull in any
    optional dependency.

    Rationale: `rich` is an optional extra. Users who install
    `click-prism` without it must still be able to import the
    package. If this regresses, the failure mode is silent —
    `click-prism` would just appear to "always need rich", and the
    optional-dep promise would erode without a clear breaking point.
    """
    # --- arrange ----------------------
    probe = (
        "import sys\n"
        "import click_prism\n"
        "leaked = [m for m in ('rich',) if m in sys.modules]\n"
        "assert not leaked, f'leaked optional deps: {leaked}'\n"
    )

    # --- act --------------------------
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=False,
    )

    # --- assert -----------------------
    assert result.returncode == 0, result.stderr


def test_no_module_level_mutable_containers() -> None:
    """No top-level `list` / `dict` / `set` in any `click_prism` submodule (dunders excepted).

    Walks every submodule's `vars()` and flags any top-level attribute
    that's a mutable container. Dunders like `__all__` and `__path__`
    are excepted because they're framework-managed and read-only by
    convention. Functions, classes, type aliases, and immutable types
    (`tuple`, `frozenset`, primitives, frozen dataclasses) are always
    allowed.

    Why this test is in-process (unlike the other two): there's no
    fresh-import requirement — we're inspecting already-imported
    module dicts, and pytest's prior import of `click_prism` is
    exactly the state we want to inspect.

    Rationale: module-level mutable state creates spooky
    action-at-a-distance bugs and ordering dependencies between
    unrelated tests. The discipline is "read-only constants only at
    module scope" — if you need a registry or cache, scope it inside
    a class or function.

    Strict by design: any module-level `list`, `dict`, or `set` fails
    this test, even if the author intends to never mutate it. Use
    `tuple` / `frozenset` for read-only constants instead. The cost
    of being strict is low; the cost of allowing exceptions is that
    the rule becomes unenforceable.
    """
    # --- arrange / act ----------------
    offenders = []
    for module in _walk_click_prism():
        for attr_name, attr in vars(module).items():
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue
            if isinstance(attr, list | dict | set):
                offenders.append(f"{module.__name__}.{attr_name}: {type(attr).__name__}")

    # --- assert -----------------------
    assert not offenders, f"module-level mutable containers found: {offenders}"
