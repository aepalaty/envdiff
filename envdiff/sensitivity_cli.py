"""CLI subcommand: envdiff sensitivity — classify keys by sensitivity tier."""
from __future__ import annotations
import argparse
import sys
from envdiff.parser import parse_file
from envdiff.key_sensitivity import SensitivityCalculator
from envdiff.sensitivity_formatter import SensitivityFormatter


def add_sensitivity_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "sensitivity",
        help="Classify keys by sensitivity tier and flag plain-text secrets.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="One or more .env files to analyse.")
    p.add_argument("--no-color", action="store_true", help="Disable coloured output.")
    p.add_argument("--summary", action="store_true", help="Print summary line only.")
    p.add_argument(
        "--min-tier",
        choices=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
        default="LOW",
        help="Only show keys at or above this tier.",
    )
    p.set_defaults(func=run_sensitivity_command)


_TIER_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def run_sensitivity_command(args: argparse.Namespace) -> int:
    envs = {}
    for path in args.files:
        try:
            envs[path] = parse_file(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2

    calculator = SensitivityCalculator()
    report = calculator.calculate(envs)

    min_rank = _TIER_ORDER[args.min_tier]
    report.entries = [e for e in report.entries if _TIER_ORDER[e.tier] >= min_rank]

    formatter = SensitivityFormatter(color=not args.no_color)

    if args.summary:
        print(formatter.format_summary(report))
    else:
        print(formatter.format_report(report))

    return 1 if report.has_plain_secrets() else 0
