"""Shared defaults for redirect following."""

from __future__ import annotations

DEFAULT_TIMEOUT = 10.0
DEFAULT_MAX_REDIRECTS = 20
ALLOWED_SCHEMES = frozenset({"http", "https"})
