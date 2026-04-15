"""CLI integration for key pattern checking."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.key_pattern import KeyPatternChecker
from envdiff.parser import parse_file
from envdiff.pattern_formatter import PatternFormatter


def add_pattern_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "pattern",
        help="Check env values against named patterns (url, uuid, port, …)",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to check")
    p.add_argument(
        "--rules",
        metavar="JSON",
        default="{}",
        help='JSON mapping of KEY -> pattern_name, e.g. \'{"PORT": "port"}\'',
    )
    p.add_argument(
        "--extra-patterns",
        metavar="JSON",
        default="{}",
        help="JSON mapping of pattern_name -> regex for custom patterns",
    )
    p.add_argument("--no-color", action="store_true", help="Disable colored output")


def run_pattern_command(args: argparse.Namespace) -> int:
    try:
        rules = json.loads(args.rules)
        extra = json.loads(args.extra_patterns)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON argument — {exc}", file=sys.stderr)
        return 2

    checker = KeyPatternChecker(rules=rules, extra_patterns=extra)
    formatter = PatternFormatter(color=not args.no_color)

    envs = {}
    for path in args.files:
        try:
            envs[path] = parse_file(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2

    reports = checker.check_all(envs)
    print(formatter.format_all(reports))
    print()
    print(formatter.format_summary(reports))

    any_violations = any(r.has_violations for r in reports.values())
    return 1 if any_violations else 0
