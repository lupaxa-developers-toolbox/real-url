# Getting started

## Requirements

- Python 3.10 or newer
- `httpx` (installed with the package)

## Install

```bash
python3 -m pip install lupaxa-real-url
```

The PyPI name is `lupaxa-real-url`. The import path is `lupaxa.real_url`.
The console script is `real-url`. `lupaxa` is a namespace package — there
is no `lupaxa/__init__.py`.

### From source (development)

```bash
make init
make python-install-dev
```

Site Markdown lives in `mkdocs/` (not GitHub’s special `docs/` directory).
After makefile-skills are installed:

```bash
make mkdocs-serve
```

## First lookup

Pass any HTTP(S) URL. The return value is the URL that finally served
the response:

```python
from lupaxa.real_url import resolve

resolve("https://github.com")
```

If you omit the scheme, `https://` is tried first. When that host cannot
be fetched or returns 404, `http://` is tried:

```python
resolve("example.com")
```

The same lookup from the shell:

```bash
real-url https://github.com
```

The CLI prints the final URL and exits `0`. Exit `2` means the URL was
invalid. Exit `1` means a loop, hop limit, or network error.

## See the chain

Ask for every hop, or hops with status codes:

```python
from lupaxa.real_url import resolve

resolve("https://example.com", full=True)
resolve("https://example.com", status=True)
```

```bash
real-url --full https://example.com
real-url --status https://example.com
```

`--full` prints one URL per line. `--status` prints `STATUS URL` for
each hop. Passing both flags uses the `--status` layout.

## Makefile helpers

```bash
make init                 # clone makefile-skills into .makefiles/
make python-install-dev   # editable install with [dev]
make python-check         # lint + type + test (via makefile-skills)
make mkdocs-serve         # local docs site
```
