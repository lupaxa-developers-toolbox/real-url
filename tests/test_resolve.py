"""Tests for following redirect chains."""

from __future__ import annotations

import httpx
import pytest

from lupaxa.real_url import (
    Hop,
    InvalidURLError,
    RedirectLoopError,
    ResolveError,
    TooManyRedirectsError,
    resolve,
    trace,
)


def _client(handler: httpx.MockTransport | object) -> httpx.Client:
    if isinstance(handler, httpx.MockTransport):
        transport = handler
    else:
        transport = httpx.MockTransport(handler)
    return httpx.Client(transport=transport, follow_redirects=False)


def test_resolve_returns_final_url_by_default() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://short.example/a":
            return httpx.Response(302, headers={"Location": "https://final.example/page"})
        return httpx.Response(200, text="ok")

    with _client(handler) as client:
        assert resolve("https://short.example/a", client=client) == "https://final.example/page"


def test_resolve_full_returns_url_list() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url == "https://t.example/one":
            return httpx.Response(301, headers={"Location": "https://t.example/two"})
        if url == "https://t.example/two":
            return httpx.Response(302, headers={"Location": "https://final.example/"})
        return httpx.Response(200)

    with _client(handler) as client:
        assert resolve("https://t.example/one", full=True, client=client) == [
            "https://t.example/one",
            "https://t.example/two",
            "https://final.example/",
        ]


def test_resolve_status_returns_hops() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://go.example/x":
            return httpx.Response(301, headers={"Location": "https://land.example/y"})
        return httpx.Response(200)

    with _client(handler) as client:
        hops = resolve("https://go.example/x", status=True, client=client)
        assert hops == [
            Hop(url="https://go.example/x", status=301),
            Hop(url="https://land.example/y", status=200),
        ]


def test_resolve_full_and_status_matches_status() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    with _client(handler) as client:
        hops = resolve("https://only.example/", full=True, status=True, client=client)
        assert hops == [Hop(url="https://only.example/", status=200)]


def test_trace_keeps_start_to_end_order() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url.endswith("/start"):
            return httpx.Response(302, headers={"Location": "/mid"})
        if url.endswith("/mid"):
            return httpx.Response(302, headers={"Location": "/end"})
        return httpx.Response(200)

    with _client(handler) as client:
        hops = trace("https://rel.example/start", client=client)
        assert [hop.url for hop in hops] == [
            "https://rel.example/start",
            "https://rel.example/mid",
            "https://rel.example/end",
        ]


def test_detects_redirect_loop() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url.endswith("/a"):
            return httpx.Response(302, headers={"Location": "/b"})
        return httpx.Response(302, headers={"Location": "/a"})

    with _client(handler) as client:
        with pytest.raises(RedirectLoopError) as exc:
            resolve("https://loop.example/a", client=client)
        assert [hop.url for hop in exc.value.hops] == [
            "https://loop.example/a",
            "https://loop.example/b",
        ]


def test_too_many_redirects() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        current = str(request.url).rsplit("/", maxsplit=1)[-1]
        nxt = int(current) + 1
        return httpx.Response(302, headers={"Location": f"https://chain.example/{nxt}"})

    with _client(handler) as client, pytest.raises(TooManyRedirectsError):
        resolve("https://chain.example/1", client=client, max_redirects=3)


def test_adds_https_when_scheme_missing() -> None:
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        return httpx.Response(200)

    with _client(handler) as client:
        assert resolve("bare.example/path", client=client) == "https://bare.example/path"
    assert seen == ["https://bare.example/path"]


def test_falls_back_to_http_when_https_cannot_be_fetched() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.scheme == "https":
            raise httpx.ConnectError("refused", request=request)
        assert str(request.url) == "http://http-only.example/path"
        return httpx.Response(200)

    with _client(handler) as client:
        assert resolve("http-only.example/path", client=client) == "http://http-only.example/path"


def test_falls_back_to_http_when_https_returns_not_found() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.scheme == "https":
            return httpx.Response(404)
        return httpx.Response(200)

    with _client(handler) as client:
        assert resolve("legacy.example/page", client=client) == "http://legacy.example/page"


def test_explicit_https_does_not_fall_back_to_http() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.scheme == "https"
        raise httpx.ConnectError("refused", request=request)

    with _client(handler) as client, pytest.raises(ResolveError, match="Failed to fetch"):
        resolve("https://https-only-down.example/", client=client)


def test_scheme_probe_raises_when_both_https_and_http_fail() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    with _client(handler) as client, pytest.raises(ResolveError, match="Failed to fetch"):
        resolve("down.example/", client=client)


def test_rejects_empty_and_unsupported_scheme() -> None:
    with pytest.raises(InvalidURLError):
        resolve("")
    with pytest.raises(InvalidURLError):
        resolve("ftp://files.example/x")


def test_network_failure_is_resolve_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    with _client(handler) as client, pytest.raises(ResolveError, match="Failed to fetch"):
        resolve("https://down.example/", client=client)


def test_redirect_without_location_stops() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302)

    with _client(handler) as client:
        assert resolve("https://stuck.example/", client=client) == "https://stuck.example/"
