"""Custom exceptions for the real_url package."""

from __future__ import annotations

from lupaxa.real_url.types import Hop


class RealUrlError(Exception):
    """Base error for the real_url package."""


class InvalidURLError(RealUrlError):
    """Raised when the starting URL is empty or not HTTP(S)."""


class ResolveError(RealUrlError):
    """Raised when a hop cannot be fetched."""


class RedirectLoopError(RealUrlError):
    """Raised when a URL repeats in the redirect chain."""

    def __init__(self, message: str, hops: list[Hop] | None = None) -> None:
        super().__init__(message)
        self.hops = list(hops or [])


class TooManyRedirectsError(RealUrlError):
    """Raised when the hop limit is reached before a final URL."""

    def __init__(self, message: str, hops: list[Hop] | None = None) -> None:
        super().__init__(message)
        self.hops = list(hops or [])
