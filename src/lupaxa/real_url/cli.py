"""Command-line interface for lupaxa.real_url."""

from __future__ import annotations

import argparse
import sys

from lupaxa.real_url import __version__, resolve
from lupaxa.real_url.exceptions import InvalidURLError, RealUrlError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Follow HTTP redirects and print the URL that serves the page."
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print every URL in the redirect chain.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print the HTTP status code for each hop.",
    )
    parser.add_argument("url", nargs="?", help="Starting URL.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"real-url {__version__}")
        return 0

    if not args.url:
        parser.error("url is required unless --version is used")

    try:
        if args.status:
            hops = resolve(args.url, status=True)
            for hop in hops:
                code = "-" if hop.status is None else hop.status
                print(f"{code} {hop.url}")
        elif args.full:
            for item in resolve(args.url, full=True):
                print(item)
        else:
            print(resolve(args.url))
    except InvalidURLError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except RealUrlError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0
