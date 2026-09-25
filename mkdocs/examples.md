# Examples

## Unwrap a Short Link

```python
from lupaxa.real_url import resolve

landing = resolve("https://example.com")
print(landing)
```

```bash
real-url https://example.com
```

## Inspect the Whole Chain

```python
from lupaxa.real_url import resolve

for url in resolve("https://example.com", full=True):
    print(url)
```

```bash
real-url --full https://example.com
```

## Include Status Codes

```python
from lupaxa.real_url import resolve

for hop in resolve("https://example.com", status=True):
    print(f"{hop.status} {hop.url}")
```

```bash
real-url --status https://example.com
```

## Detect a Loop

```python
from lupaxa.real_url import RedirectLoopError, resolve

try:
    resolve("https://example.com")
except RedirectLoopError as exc:
    print("Loop:", [hop.url for hop in exc.hops])
```

## Cap the Hop Count

```python
from lupaxa.real_url import TooManyRedirectsError, resolve

try:
    resolve("https://example.com", max_redirects=5)
except TooManyRedirectsError as exc:
    print(f"Stopped after {len(exc.hops)} hops")
```

## Shell

Capture the landing URL when the lookup succeeds:

```bash
if landing="$(real-url https://example.com)"; then
    echo "Landed on $landing"
else
    echo "Could not resolve"
fi
```

Print the chain with statuses:

```bash
real-url --status https://example.com
```
