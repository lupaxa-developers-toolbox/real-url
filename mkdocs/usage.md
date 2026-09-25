# Usage

## How Following Works

`resolve` issues a GET for the starting URL with automatic redirects
turned off. Each `3xx` response with a `Location` header becomes the
next hop. Relative and protocol-relative locations are joined onto the
current URL.

| Situation                              | Result                                      |
| -------------------------------------- | ------------------------------------------- |
| Final non-redirect response            | That URL is the real URL                    |
| Redirect with a `Location` header      | Follow the next hop                         |
| Redirect without `Location`            | Stop; that hop is treated as final          |
| Same URL seen twice                    | `RedirectLoopError`                         |
| Hop limit reached                      | `TooManyRedirectsError` (default 20 hops)   |
| No scheme; HTTPS fails or returns 404  | Retry the same host as `http://`            |
| Timeout or connection failure          | `ResolveError` (after HTTP fallback)        |

Bodies are not downloaded. Only `http` and `https` are accepted.

## Library

### Final URL

```python
from lupaxa.real_url import resolve

resolve("https://example.com")
```

### Every Hop

```python
resolve("https://example.com", full=True)
```

Returns a list of URL strings, start first and final last.

### Hops With Status Codes

```python
from lupaxa.real_url import Hop, resolve

hops: list[Hop] = resolve("https://example.com", status=True)
for hop in hops:
    print(hop.status, hop.url)
```

`status=True` always returns the full chain as `Hop` values, including
when `full=True` is also set.

### Trace Explicitly

`trace` always returns the hop list. `resolve` is the convenience
wrapper that matches the CLI flags:

```python
from lupaxa.real_url import trace

hops = trace("https://example.com")
hops[-1].url
```

### Timeouts and Hop Limits

```python
resolve("https://example.com", timeout=5.0, max_redirects=10)
```

### Handle Failures

```python
from lupaxa.real_url import (
    InvalidURLError,
    RedirectLoopError,
    ResolveError,
    TooManyRedirectsError,
    resolve,
)

try:
    resolve("https://example.com")
except InvalidURLError as exc:
    print(f"Bad URL: {exc}")
except RedirectLoopError as exc:
    print(f"Loop after {len(exc.hops)} hops")
except TooManyRedirectsError as exc:
    print(f"Stopped after {len(exc.hops)} hops")
except ResolveError as exc:
    print(f"Fetch failed: {exc}")
```

## CLI

```bash
real-url https://example.com
real-url --full https://example.com
real-url --status https://example.com
real-url --full --status https://example.com
real-url --version
real-url --help
```

The URL is a positional argument. A missing scheme is tried as
`https://` first, then `http://` if HTTPS cannot be fetched or returns
404. An explicit `http://` or `https://` is used as given.

### Output and Exit Codes

| Result                    | Stdout                         | Exit |
| ------------------------- | ------------------------------ | ---- |
| Default success           | Final URL                      | `0`  |
| `--full`                  | One URL per hop                | `0`  |
| `--status`                | `STATUS URL` per hop           | `0`  |
| `--version`               | `real-url x.y.z`               | `0`  |
| Invalid URL or missing    | error on stderr                | `2`  |
| Loop, hop limit, network  | error on stderr                | `1`  |

```bash
if landing="$(real-url https://example.com)"; then
    echo "Landed on $landing"
fi
```
