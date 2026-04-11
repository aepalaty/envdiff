"""CLI subcommand for key usage analysis."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.parser import parse_file
from envdiff.key_usage import KeyUsageTracker
from envdiff.usage_formatter import UsageFormatter


def add_usage_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "usage",
        help="Analyse key usage frequency across multiple .env files",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to analyse",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        metavar="N",
        help="Number of top/bottom keys to display (default: 5)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable coloured output",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a single summary line instead of the full report",
    )


def run_usage_command(args: argparse.Namespace) -> int:
    envs = {}
    for path in args.files:
        try:
            envs[path] = parse_file(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1

    tracker = KeyUsageTracker()
    report = tracker.track(envs)
    formatter = UsageFormatter(color=not args.no_color)

    if args.summary:
        print(formatter.format_summary(report))
    else:
        print(formatter.format_report(report, top_n=args.top))

    return 0
