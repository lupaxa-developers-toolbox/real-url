"""lupaxa.real_url — follow HTTP redirects to the URL that serves the page.

``resolve(url)`` returns the final URL. Pass ``full=True`` for every hop,
or ``status=True`` for hops with HTTP status codes. A missing scheme is
tried as HTTPS first, then HTTP if that lookup fails or returns 404.
"""

from __future__ import annotations

from .constants import DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT
from .core import normalize_url, resolve, trace
from .exceptions import (
    InvalidURLError,
    RealUrlError,
    RedirectLoopError,
    ResolveError,
    TooManyRedirectsError,
)
from .types import Hop
from .version import __version__, get_version

__all__ = [
    "DEFAULT_MAX_REDIRECTS",
    "DEFAULT_TIMEOUT",
    "Hop",
    "InvalidURLError",
    "RealUrlError",
    "RedirectLoopError",
    "ResolveError",
    "TooManyRedirectsError",
    "__version__",
    "get_version",
    "normalize_url",
    "resolve",
    "trace",
]
