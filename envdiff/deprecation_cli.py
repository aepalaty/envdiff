"""CLI subcommand for checking deprecated keys in .env files."""

import argparse
import sys
from typing import List

from envdiff.deprecation_loader import load_registry_auto, load_registry_from_path
from envdiff.parser import parse_file


def add_deprecation_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "deprecations",
        help="Check .env files for deprecated keys",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to check")
    p.add_argument(
        "--config",
        metavar="PATH",
        default=None,
        help="Path to deprecation config (JSON or TOML)",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )


def run_deprecation_command(args: argparse.Namespace) -> int:
    if args.config:
        registry = load_registry_from_path(args.config)
    else:
        registry = load_registry_auto()

    if not registry._registry:
        print("No deprecation rules loaded. Provide a config file.")
        return 0

    found_any = False
    for filepath in args.files:
        try:
            env = parse_file(filepath)
        except FileNotFoundError:
            print(f"File not found: {filepath}", file=sys.stderr)
            return 2

        report = registry.check(env)
        if report.has_deprecated:
            found_any = True
            print(f"[{filepath}]")
            print(report)
            print()

    if not found_any:
        print("No deprecated keys found in any file.")
    return 1 if found_any else 0
