from __future__ import annotations
import argparse
import sys
from envdiff.parser import parse_file
from envdiff.key_whitespace import WhitespaceChecker
from envdiff.whitespace_formatter import WhitespaceFormatter


def add_whitespace_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "whitespace",
        help="Detect whitespace issues in .env file values",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to check",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )


def run_whitespace_command(args: argparse.Namespace) -> int:
    envs = {}
    for path in args.files:
        try:
            envs[path] = parse_file(path)
        except FileNotFoundError:
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 2

    checker = WhitespaceChecker()
    report = checker.calculate(envs)
    formatter = WhitespaceFormatter(color=not args.no_color)
    print(formatter.format_report(report))
    return 1 if report.has_issues() else 0
