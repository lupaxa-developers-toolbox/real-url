"""Public value types for redirect hops."""

from __future__ import annotations

from typing import NamedTuple


class Hop(NamedTuple):
    """One URL in a redirect chain and the status it returned."""

    url: str
    status: int | None
