from __future__ import annotations
import argparse
import json
import sys
from envdiff.key_dependencies import DependencyChecker
from envdiff.dependency_formatter import DependencyFormatter
from envdiff.parser import parse_file


def add_dependency_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "dependencies",
        help="Check that key dependencies are satisfied across env files",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to check")
    p.add_argument(
        "--rules",
        required=True,
        metavar="JSON",
        help='Dependency rules as JSON, e.g. \'{"DB_HOST": ["DB_PORT"]}\'",
    )
    p.add_argument("--no-color", action="store_true", help="Disable color output")


def run_dependency_command(args: argparse.Namespace) -> int:
    try:
        rules = json.loads(args.rules)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON for --rules: {exc}", file=sys.stderr)
        return 2

    envs = {}
    for path in args.files:
        try:
            envs[path] = parse_file(path)
        except FileNotFoundError:
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 2

    checker = DependencyChecker(rules=rules)
    report = checker.calculate(envs)
    formatter = DependencyFormatter(color=not args.no_color)
    print(formatter.format_report(report))
    return 1 if report.has_violations else 0
