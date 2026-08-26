"""Follow HTTP redirects and return the URL that serves the page."""

from __future__ import annotations

from typing import Literal, overload
from urllib.parse import urljoin, urlparse

import httpx

from lupaxa.real_url.constants import ALLOWED_SCHEMES, DEFAULT_MAX_REDIRECTS, DEFAULT_TIMEOUT
from lupaxa.real_url.exceptions import (
    InvalidURLError,
    RedirectLoopError,
    ResolveError,
    TooManyRedirectsError,
)
from lupaxa.real_url.types import Hop
from lupaxa.real_url.version import __version__


def normalize_url(url: str) -> str:
    """Return an absolute HTTP(S) URL, adding ``https://`` when needed."""
    text = url.strip()
    if not text:
        raise InvalidURLError("URL is empty")

    parsed = urlparse(text)
    if not parsed.scheme:
        text = f"https://{text}"
        parsed = urlparse(text)

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise InvalidURLError(f"Unsupported URL scheme: {parsed.scheme}")
    if not parsed.netloc:
        raise InvalidURLError(f"URL has no host: {text}")
    return text


def _scheme_candidates(url: str) -> list[str]:
    """Return start URLs to try, HTTPS first when the scheme was omitted."""
    text = url.strip()
    if not text:
        raise InvalidURLError("URL is empty")

    parsed = urlparse(text)
    if parsed.scheme:
        return [normalize_url(text)]
    return [normalize_url(f"https://{text}"), normalize_url(f"http://{text}")]


def _is_not_found(hops: list[Hop]) -> bool:
    return len(hops) == 1 and hops[0].status == 404


def _follow(
    start: str,
    *,
    client: httpx.Client,
    max_redirects: int,
) -> list[Hop]:
    current = start
    hops: list[Hop] = []
    seen: set[str] = set()

    while True:
        if current in seen:
            raise RedirectLoopError(f"Redirect loop detected at {current}", hops=hops)
        seen.add(current)

        try:
            with client.stream("GET", current) as response:
                hop_url = str(response.url)
                hop_status = response.status_code
                is_redirect = response.is_redirect
                location = response.headers.get("location")
        except httpx.TimeoutException as exc:
            raise ResolveError(f"Timed out fetching {current}") from exc
        except httpx.RequestError as exc:
            raise ResolveError(f"Failed to fetch {current}: {exc}") from exc

        hops.append(Hop(url=hop_url, status=hop_status))

        if not is_redirect or not location:
            return hops
        if len(hops) >= max_redirects:
            raise TooManyRedirectsError(
                f"Exceeded redirect limit ({max_redirects}) at {hop_url}",
                hops=hops,
            )
        current = urljoin(hop_url, location)


def _open_client(timeout: float) -> httpx.Client:
    return httpx.Client(
        follow_redirects=False,
        timeout=timeout,
        headers={"User-Agent": f"lupaxa-real-url/{__version__}"},
    )


def trace(
    url: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    max_redirects: int = DEFAULT_MAX_REDIRECTS,
    client: httpx.Client | None = None,
) -> list[Hop]:
    """Follow redirects and return every hop from start to finish."""
    candidates = _scheme_candidates(url)
    own_client = client is None
    if client is None:
        client = _open_client(timeout)

    last_error: ResolveError | None = None
    not_found_hops: list[Hop] | None = None
    try:
        for index, start in enumerate(candidates):
            try:
                hops = _follow(start, client=client, max_redirects=max_redirects)
            except ResolveError as exc:
                last_error = exc
                continue
            if index == 0 and len(candidates) > 1 and _is_not_found(hops):
                not_found_hops = hops
                continue
            return hops
        if not_found_hops is not None:
            return not_found_hops
        if last_error is not None:
            raise last_error
        raise ResolveError(f"No response received for {url}")
    finally:
        if own_client:
            client.close()


@overload
def resolve(
    url: str,
    *,
    full: Literal[False] = False,
    status: Literal[False] = False,
    timeout: float = DEFAULT_TIMEOUT,
    max_redirects: int = DEFAULT_MAX_REDIRECTS,
    client: httpx.Client | None = None,
) -> str:
    pass


@overload
def resolve(
    url: str,
    *,
    full: Literal[True],
    status: Literal[False] = False,
    timeout: float = DEFAULT_TIMEOUT,
    max_redirects: int = DEFAULT_MAX_REDIRECTS,
    client: httpx.Client | None = None,
) -> list[str]:
    pass


@overload
def resolve(
    url: str,
    *,
    full: bool = False,
    status: Literal[True],
    timeout: float = DEFAULT_TIMEOUT,
    max_redirects: int = DEFAULT_MAX_REDIRECTS,
    client: httpx.Client | None = None,
) -> list[Hop]:
    pass


def resolve(
    url: str,
    *,
    full: bool = False,
    status: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    max_redirects: int = DEFAULT_MAX_REDIRECTS,
    client: httpx.Client | None = None,
) -> str | list[str] | list[Hop]:
    """Follow redirects and return the final URL, hop URLs, or hops with status.

    Default returns the last URL. ``full=True`` returns every URL.
    ``status=True`` returns :class:`Hop` values for the whole chain.
    """
    hops = trace(url, timeout=timeout, max_redirects=max_redirects, client=client)
    if not hops:
        raise ResolveError(f"No response received for {url}")
    if status:
        return hops
    if full:
        return [hop.url for hop in hops]
    return hops[-1].url
