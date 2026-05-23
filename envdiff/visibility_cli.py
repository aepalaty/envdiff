from __future__ import annotations
import argparse
import sys
from envdiff.parser import parse_file
from envdiff.key_visibility import VisibilityCalculator
from envdiff.visibility_formatter import VisibilityFormatter


def add_visibility_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "visibility",
        help="Classify keys by visibility: public, internal, or private",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to analyse",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable coloured output",
    )


def run_visibility_command(args: argparse.Namespace) -> int:
    envs = {}
    for path in args.files:
        try:
            envs[path] = parse_file(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 1

    calculator = VisibilityCalculator()
    report = calculator.calculate(envs)

    formatter = VisibilityFormatter(color=not args.no_color)
    print(formatter.format_report(report))

    return 1 if report.has_private() else 0
