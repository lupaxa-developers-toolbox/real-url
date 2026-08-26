# Reference

Public names are exported from `lupaxa.real_url`.

## Package

| Name                              | Description                                         |
| --------------------------------- | --------------------------------------------------- |
| `resolve(url, *, ...)`            | Final URL, hop URLs, or hops with status            |
| `trace(url, *, ...)`              | Always return the hop list                          |
| `normalize_url(url)`              | Add `https://` and reject non-HTTP schemes          |
| `Hop`                             | Named tuple: `url`, `status`                        |
| `RealUrlError`                    | Base error                                          |
| `InvalidURLError`                 | Empty URL or unsupported scheme                     |
| `ResolveError`                    | Timeout or transport failure                        |
| `RedirectLoopError`               | Repeated URL in the chain (`hops` attached)         |
| `TooManyRedirectsError`           | Hop limit reached (`hops` attached)                 |
| `DEFAULT_TIMEOUT`                 | `10.0` seconds                                      |
| `DEFAULT_MAX_REDIRECTS`           | `20` hops                                           |
| `__version__`                     | Package version string                              |
| `get_version()`                   | Return `__version__`                                |

### `resolve`

```text
resolve(url, *, full=False, status=False, timeout=10.0, max_redirects=20, client=None)
```

| Parameter       | Type                     | Description                                          |
| --------------- | ------------------------ | ---------------------------------------------------- |
| `url`           | `str`                    | Starting URL; `https://` then `http://` if omitted   |
| `full`          | `bool`                   | Return every hop URL when `status` is false          |
| `status`        | `bool`                   | Return `list[Hop]` for the whole chain               |
| `timeout`       | `float`                  | Per-request timeout in seconds                       |
| `max_redirects` | `int`                    | Maximum hops before `TooManyRedirectsError`          |
| `client`        | `httpx.Client`, optional | Injected client (tests); not closed by `resolve`     |

Return type:

| Flags                    | Return type    |
| ------------------------ | -------------- |
| default                  | `str`          |
| `full=True`              | `list[str]`    |
| `status=True`            | `list[Hop]`    |
| `full=True, status=True` | `list[Hop]`    |

### `trace`

```text
trace(url, *, timeout=10.0, max_redirects=20, client=None) -> list[Hop]
```

Same fetch rules as `resolve`. Use this when you always want the hop
list.

### `normalize_url`

```text
normalize_url(url) -> str
```

Strips surrounding whitespace, adds `https://` when the scheme is
missing, and raises `InvalidURLError` for an empty string, a missing
host, or a scheme other than `http` / `https`. `resolve` and `trace`
still try `http://` afterwards when the scheme was omitted and HTTPS
cannot be fetched or returns 404.

### `Hop`

```text
Hop(url: str, status: int | None)
```

`status` is the HTTP status returned for that URL. It is `None` only if
a hop was recorded without a response (the public helpers always set an
integer after a successful fetch).

## CLI

The CLI is installed as `real-url`.

| Flag        | Meaning                                         |
| ----------- | ----------------------------------------------- |
| `url`       | Starting URL (required unless `--version`)      |
| `--full`    | Print every hop URL                             |
| `--status`  | Print `STATUS URL` for each hop                 |
| `--version` | Print `real-url x.y.z` and exit `0`             |
| `--help`    | Show argparse help                              |

`--full` combined with `--status` uses the `--status` layout.

### Exit codes

| Code | Meaning                                         |
| ---- | ----------------------------------------------- |
| `0`  | Success, or `--version` printed                 |
| `1`  | Loop, hop limit, or network / timeout failure   |
| `2`  | Missing URL, invalid URL, or bad args           |
