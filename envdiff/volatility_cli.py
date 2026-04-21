"""CLI subcommand for key volatility analysis."""
from __future__ import annotations
import argparse
import sys
from envdiff.parser import parse_file
from envdiff.snapshot import SnapshotManager
from envdiff.key_volatility import VolatilityCalculator
from envdiff.volatility_formatter import VolatilityFormatter


def add_volatility_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "volatility",
        help="Measure how frequently keys change value across snapshots or env files.",
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--snapshots",
        metavar="DIR",
        help="Path to snapshot store directory.",
    )
    group.add_argument(
        "--files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files treated as ordered snapshots.",
    )
    p.add_argument("--no-color", action="store_true", help="Disable color output.")
    p.set_defaults(func=run_volatility_command)


def run_volatility_command(args: argparse.Namespace) -> int:
    calculator = VolatilityCalculator()
    formatter = VolatilityFormatter(color=not args.no_color)

    if args.files:
        snapshots = []
        for path in args.files:
            try:
                snapshots.append(parse_file(path))
            except FileNotFoundError:
                print(f"Error: file not found: {path}", file=sys.stderr)
                return 1
    else:
        manager = SnapshotManager(args.snapshots)
        all_snaps = manager.list_snapshots()
        if not all_snaps:
            print("No snapshots found in store.", file=sys.stderr)
            return 1
        snapshots = [s.env for s in all_snaps]

    report = calculator.calculate(snapshots)
    print(formatter.format_report(report))
    return 1 if report.has_volatile_keys else 0
