import argparse
from typing import List

from envdiff.parser import parse_file
from envdiff.key_frequency import KeyFrequencyCalculator
from envdiff.frequency_formatter import FrequencyFormatter


def add_frequency_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "frequency",
        help="Show how often each key appears across environments",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help=".env files to analyse",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        metavar="N",
        help="Number of top keys to display (default: 20)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colour output",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print summary line only",
    )


def run_frequency_command(args: argparse.Namespace) -> int:
    envs = {}
    for path in args.files:
        try:
            envs[path] = parse_file(path)
        except FileNotFoundError:
            print(f"Error: file not found: {path}")
            return 1

    calculator = KeyFrequencyCalculator()
    report = calculator.calculate(envs)
    formatter = FrequencyFormatter(color=not args.no_color)

    if args.summary:
        print(formatter.format_summary(report))
    else:
        print(formatter.format_report(report, top=args.top))

    return 0
