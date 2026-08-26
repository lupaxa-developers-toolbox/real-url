# real-url

Follow HTTP redirects and report the URL that actually serves the page.

Install the **`lupaxa-real-url`** package and import the `lupaxa.real_url`
namespace. Use it from Python or from the `real-url` CLI in shell scripts.

```bash
pip install lupaxa-real-url
```

```python
from lupaxa.real_url import resolve

resolve("https://example.com")
```

```bash
real-url https://example.com
real-url --full https://example.com
real-url --status https://example.com
real-url --version
```

## What you get

-   The final URL by default, from the library or the CLI
-   The full hop list when you pass `full=True` or `--full`
-   HTTP status codes for each hop when you pass `status=True` or
    `--status`
-   Redirect-loop detection and a hop limit
-   Typed errors for bad URLs and network failures

Only `http` and `https` are followed. A URL without a scheme is tried as
`https://` first, then `http://` if HTTPS cannot be fetched or returns
404. Relative `Location` headers are joined onto the current hop.

## Next steps

- [Getting started](getting-started.md) — install and first lookups
- [Usage](usage.md) — library options and CLI flags
- [Reference](reference.md) — public API and exit codes
- [Examples](examples.md) — copy-paste recipes
