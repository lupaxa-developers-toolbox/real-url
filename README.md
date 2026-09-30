<p align="center">
  <a href="https://github.com/lupaxa-developers-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/developers-toolbox/readme-logo.png" alt="Developers Toolbox" />
  </a>
</p>

<h1 align="center">Real URL</h1>

Follow HTTP redirects and report the URL that actually serves the page.
The hop list is kept from the URL you started with through to the last
response. Bodies are not downloaded. Only `http` and `https` are
followed.

The PyPI name is `lupaxa-real-url`. The import path is `lupaxa.real_url`.
The console script is `real-url`. `lupaxa` is a namespace package — there
is no `lupaxa/__init__.py`.

Public names: `resolve`, `trace`, `normalize_url`, `Hop`, `RealUrlError`,
`InvalidURLError`, `ResolveError`, `RedirectLoopError`,
`TooManyRedirectsError`, `DEFAULT_TIMEOUT` (`10.0`),
`DEFAULT_MAX_REDIRECTS` (`20`), `__version__`, `get_version()`.

## Install

```bash
pip install lupaxa-real-url
```

Requires Python 3.10+ and `httpx`.

## Library

```python
from lupaxa.real_url import Hop, resolve, trace

resolve("https://example.com")
resolve("https://example.com", full=True)
resolve("https://example.com", status=True)
resolve("example.com", timeout=5.0, max_redirects=10)
```

| Flags                    | Return        |
| ------------------------ | ------------- |
| default                  | final URL     |
| `full=True`              | `list[str]`   |
| `status=True`            | `list[Hop]`   |
| `full=True, status=True` | `list[Hop]`   |

`trace` always returns the hop list. `Hop` is `(url, status)`.

A missing scheme is tried as `https://` first, then `http://` if HTTPS
cannot be fetched or returns 404. An explicit scheme is used as given.
Relative `Location` headers are joined onto the current hop.

| Situation                             | Result                                    |
| ------------------------------------- | ----------------------------------------- |
| Final non-redirect response           | That URL is the real URL                  |
| Redirect with a `Location` header     | Follow the next hop                       |
| Redirect without `Location`           | Stop; that hop is treated as final        |
| Same URL seen twice                   | `RedirectLoopError`                       |
| Hop limit reached                     | `TooManyRedirectsError` (default 20 hops) |
| No scheme; HTTPS fails or returns 404 | Retry the same host as `http://`          |
| Timeout or connection failure         | `ResolveError` (after HTTP fallback)      |

```python
from lupaxa.real_url import RedirectLoopError, ResolveError, TooManyRedirectsError, resolve

try:
    resolve("https://example.com")
except RedirectLoopError as exc:
    print("Loop:", [hop.url for hop in exc.hops])
except TooManyRedirectsError as exc:
    print(f"Stopped after {len(exc.hops)} hops")
except ResolveError as exc:
    print(f"Fetch failed: {exc}")
```

`normalize_url` adds `https://` when the scheme is missing and rejects
empty strings, missing hosts, and non-HTTP schemes. `resolve` and
`trace` still try `http://` afterwards when the scheme was omitted.

## CLI

```bash
real-url https://example.com
real-url --full https://example.com
real-url --status https://example.com
real-url --full --status https://example.com
real-url --version
```

The URL is a positional argument. `--full` combined with `--status` uses
the `--status` layout.

| Flag        | Meaning                                    |
| ----------- | ------------------------------------------ |
| `url`       | Starting URL (required unless `--version`) |
| `--full`    | Print every hop URL                        |
| `--status`  | Print `STATUS URL` for each hop            |
| `--version` | Print `real-url x.y.z` and exit `0`        |
| `--help`    | Show argparse help                         |

| Result                   | Stdout            | Exit |
| ------------------------ | ----------------- | ---- |
| Default success          | Final URL         | `0`  |
| `--full`                 | One URL per hop   | `0`  |
| `--status`               | `STATUS URL`      | `0`  |
| `--version`              | `real-url x.y.z`  | `0`  |
| Invalid URL or missing   | error on stderr   | `2`  |
| Loop, hop limit, network | error on stderr   | `1`  |

```bash
if landing="$(real-url https://example.com)"; then
    echo "Landed on $landing"
fi
```

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
