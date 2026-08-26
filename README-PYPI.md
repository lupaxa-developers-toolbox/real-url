<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-developers-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/developers-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
</p>
<h3 align="center">
  The Lupaxa Developers Toolbox<br />
  Part of The Lupaxa Project
</h3>

<br />

# lupaxa-real-url

Follow HTTP redirects and report the URL that actually serves the page.
The hop list is kept from the URL you started with through to the last
response.

Built for scripts and tools used by The Lupaxa Project.

The PyPI name is `lupaxa-real-url`. The import path is `lupaxa.real_url`.
The CLI is installed as `real-url`.

## Features

- Follows HTTP 3xx redirects, including relative `Location` values
- Default return is the final URL that served the page
- `full=True` / `--full` returns every URL in the chain
- `status=True` / `--status` returns each hop with its HTTP status code
- Detects redirect loops and stops after a hop limit
- Fails with typed errors for bad URLs and network problems
- Thin CLI plus a small library API

## Installation

### From PyPI

```bash
pip install lupaxa-real-url
```

### From source (development mode)

```bash
pip install -e ".[dev]"
```

Requires Python 3.10+ and `httpx`. `lupaxa` is a namespace package —
there is no `lupaxa/__init__.py`.

## Usage

```python
from lupaxa.real_url import resolve

resolve("https://example.com")
resolve("https://example.com", full=True)
resolve("https://example.com", status=True)
```

```bash
real-url https://example.com
real-url --full https://example.com
real-url --status https://example.com
real-url --full --status https://example.com
real-url --version
real-url --help
```

Default output is one final URL. `--full` prints one URL per hop.
`--status` prints `STATUS URL` for each hop.

## Development

```bash
make init
make python-install-dev
make python-check
make mkdocs-serve
```

Documentation lives in `mkdocs/`.

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
