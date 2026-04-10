"""CLI integration for the lint subcommand."""

import argparse
import sys
from typing import List

from envdiff.parser import parse_file
from envdiff.lint import EnvLinter


def add_lint_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'lint' subcommand onto an existing subparsers group."""
    parser = subparsers.add_parser(
        "lint",
        help="Check a .env file for common issues.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to lint.",
    )
    parser.add_argument(
        "--allow-lowercase",
        action="store_true",
        default=False,
        help="Do not warn about lowercase key names.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any warnings are found (not just errors).",
    )


def run_lint_command(args: argparse.Namespace) -> int:
    """Execute the lint command; returns an exit code."""
    linter = EnvLinter(allow_lowercase=args.allow_lowercase)
    found_issues = False
    found_errors = False

    for filepath in args.files:
        try:
            env = parse_file(filepath)
        except FileNotFoundError:
            print(f"error: file not found: {filepath}", file=sys.stderr)
            return 2

        result = linter.lint(env)
        print(f"==> {filepath}")

        if result.is_clean:
            print("  No issues found.")
        else:
            for issue in result.issues:
                print(f"  {issue}")
            found_issues = True
            if result.errors:
                found_errors = True

        print()

    if found_errors:
        return 1
    if args.strict and found_issues:
        return 1
    return 0
