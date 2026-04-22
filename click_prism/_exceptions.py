"""Single exception type click-prism introduces."""

from __future__ import annotations

import click


class PrismError(click.ClickException):
    """Raised by click-prism for user-facing configuration errors
    (invalid depth, name collisions, unknown theme, etc.).

    Subclassing `click.ClickException` means Click formats the error
    and exits with a non-zero status automatically.
    """
