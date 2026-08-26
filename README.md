<p align="center">
  <a href="https://github.com/lupaxa-developers-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/developers-toolbox/readme-logo.png" alt="Developers Toolbox" />
  </a>
</p>

<h1 align="center">real-url</h1>

Follow HTTP redirects and report the URL that actually serves the page.
The hop list is kept from the URL you started with through to the last
response.

The PyPI name is `lupaxa-real-url`. The import path is `lupaxa.real_url`.

## Install

```bash
pip install lupaxa-real-url
```

Requires Python 3.10+ and `httpx`.

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
real-url --version
```

By default the library and CLI return only the final URL. `--full` prints
every hop. `--status` prints each hop with its HTTP status code.

## Documentation

Site pages live in `mkdocs/`.

```bash
make init
make python-install-dev
make mkdocs-serve
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
