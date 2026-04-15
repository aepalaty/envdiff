import argparse
import sys
from envdiff.parser import parse_file
from envdiff.key_coverage import CoverageCalculator
from envdiff.coverage_formatter import CoverageFormatter


def add_coverage_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "coverage",
        help="Show key coverage across multiple .env files",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to analyse",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable coloured output",
    )
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=0.0,
        metavar="RATIO",
        help="Only show keys below this coverage ratio (0.0–1.0)",
    )


def run_coverage_command(args: argparse.Namespace) -> int:
    if len(args.files) < 2:
        print("error: coverage requires at least two files", file=sys.stderr)
        return 2

    envs = {}
    for path in args.files:
        try:
            envs[path] = parse_file(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2

    calculator = CoverageCalculator()
    report = calculator.calculate(envs)

    if args.min_coverage > 0.0:
        report.entries = [
            e for e in report.entries if e.coverage_ratio < args.min_coverage
        ]

    formatter = CoverageFormatter(color=not args.no_color)
    print(formatter.format_report(report))

    return 1 if report.partial_keys else 0
