"""Tests for the real-url CLI."""

from __future__ import annotations

import subprocess
import sys

import httpx
import pytest

from lupaxa.real_url import Hop, __version__
from lupaxa.real_url.cli import main

_RealClient = httpx.Client


def _patch_client(monkeypatch: pytest.MonkeyPatch, handler: object) -> None:
    transport = httpx.MockTransport(handler)

    def factory(*_args: object, **_kwargs: object) -> httpx.Client:
        return _RealClient(transport=transport, follow_redirects=False)

    monkeypatch.setattr("lupaxa.real_url.core.httpx.Client", factory)


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--version"]) == 0
    assert f"real-url {__version__}" in capsys.readouterr().out


def test_default_prints_final_url(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://cli.example/in":
            return httpx.Response(302, headers={"Location": "https://cli.example/out"})
        return httpx.Response(200)

    _patch_client(monkeypatch, handler)
    assert main(["https://cli.example/in"]) == 0
    assert capsys.readouterr().out.strip() == "https://cli.example/out"


def test_full_prints_each_url(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://cli.example/in":
            return httpx.Response(302, headers={"Location": "https://cli.example/out"})
        return httpx.Response(200)

    _patch_client(monkeypatch, handler)
    assert main(["--full", "https://cli.example/in"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "https://cli.example/in",
        "https://cli.example/out",
    ]


def test_status_prints_code_and_url(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if str(request.url) == "https://cli.example/in":
            return httpx.Response(301, headers={"Location": "https://cli.example/out"})
        return httpx.Response(200)

    _patch_client(monkeypatch, handler)
    assert main(["--status", "https://cli.example/in"]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "301 https://cli.example/in",
        "200 https://cli.example/out",
    ]


def test_full_and_status_match_status_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    _patch_client(monkeypatch, handler)
    assert main(["--full", "--status", "https://cli.example/only"]) == 0
    assert capsys.readouterr().out.strip() == "200 https://cli.example/only"


def test_invalid_url_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["ftp://nope.example"]) == 2
    assert "error:" in capsys.readouterr().err


def test_loop_exits_1(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        target = "/b" if str(request.url).endswith("/a") else "/a"
        return httpx.Response(302, headers={"Location": target})

    _patch_client(monkeypatch, handler)
    assert main(["https://loop.example/a"]) == 1
    assert "error:" in capsys.readouterr().err


def test_missing_url() -> None:
    with pytest.raises(SystemExit) as exc:
        main([])
    assert exc.value.code == 2


def test_module_entry_version() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "lupaxa.real_url", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert __version__ in proc.stdout


def test_hop_repr_used_by_status_flag() -> None:
    hop = Hop(url="https://example.com/", status=200)
    assert hop.url == "https://example.com/"
    assert hop.status == 200
