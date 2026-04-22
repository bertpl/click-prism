"""Layered tree rendering configuration."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Final, Literal

from click_prism._environment import _detect_stdout_charset
from click_prism._exceptions import PrismError
from click_prism._theme import TreeTheme, _resolve_theme

UNLIMITED: Final[int] = -1


@dataclass
class TreeConfig:
    """Layered configuration for tree rendering.

    All fields default to None (unset). Use `merge_onto()` to overlay one
    config onto another (child wins, parent fills gaps), then `resolve()`
    to fill in defaults. Reversing the order corrupts `UNLIMITED`.
    """

    charset: Literal["unicode", "ascii"] | None = None
    depth: int | None = None  # None (inherit), UNLIMITED (-1), or >= 0
    show_hidden: bool | None = None
    show_params: bool | None = None
    tree_help: Literal["root", "all", "none"] | None = None
    theme: TreeTheme | None = None

    def resolve(self) -> TreeConfig:
        """Return a fully-populated config with defaults applied.

        Resolves `charset` via stdout autodetect when unset, normalises
        `UNLIMITED` to None, defaults booleans to False, defaults
        `tree_help` to "root", and resolves the theme via
        `_resolve_theme`.

        Returns:
            A new TreeConfig with all fields populated except `depth`,
            which may still be None (= no limit).

        Raises:
            PrismError: If `depth` is negative and not equal to
                `UNLIMITED`.
        """
        if self.depth is not None and self.depth < 0 and self.depth != UNLIMITED:
            raise PrismError(
                f"Invalid depth {self.depth!r}. Use None (inherit), UNLIMITED (-1), or a non-negative integer."
            )
        return TreeConfig(
            charset=self.charset if self.charset is not None else _detect_stdout_charset(),
            depth=None if self.depth == UNLIMITED else self.depth,
            show_hidden=self.show_hidden if self.show_hidden is not None else False,
            show_params=self.show_params if self.show_params is not None else False,
            tree_help=self.tree_help if self.tree_help is not None else "root",
            theme=_resolve_theme(self.theme),
        )

    def merge_onto(self, base: TreeConfig) -> TreeConfig:
        """Return `self` overlaid onto `base` — self's non-None fields win, base fills gaps."""
        return TreeConfig(
            **{f.name: (v if (v := getattr(self, f.name)) is not None else getattr(base, f.name)) for f in fields(self)}
        )
