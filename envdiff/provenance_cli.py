import argparse
from envdiff.parser import parse_file
from envdiff.key_provenance import ProvenanceCalculator
from envdiff.provenance_formatter import ProvenanceFormatter


def add_provenance_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "provenance",
        help="Show where each key originates and whether values are consistent",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help=".env files to analyse (name=path or just path)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable coloured output",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        default=False,
        help="Print summary line only",
    )


def run_provenance_command(args: argparse.Namespace) -> int:
    envs = {}
    for spec in args.files:
        if "=" in spec:
            name, path = spec.split("=", 1)
        else:
            name = spec
            path = spec
        try:
            envs[name] = parse_file(path)
        except FileNotFoundError:
            print(f"Error: file not found: {path}")
            return 1

    calculator = ProvenanceCalculator()
    report = calculator.calculate(envs)
    formatter = ProvenanceFormatter(color=not args.no_color)

    if args.summary_only:
        print(formatter.format_summary(report))
    else:
        print(formatter.format_report(report))

    return 1 if report.has_inconsistencies() else 0
