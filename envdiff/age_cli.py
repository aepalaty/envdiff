"""CLI subcommand for key age analysis."""

import argparse
from typing import List

from envdiff.snapshot import SnapshotManager
from envdiff.key_age import KeyAgeCalculator
from envdiff.age_formatter import AgeFormatter


def add_age_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "age",
        help="Analyse how long since each key was last changed across snapshots",
    )
    parser.add_argument(
        "--store",
        default=".envdiff_snapshots",
        help="Path to snapshot store directory (default: .envdiff_snapshots)",
    )
    parser.add_argument(
        "--env",
        required=True,
        help="Environment name whose snapshots to analyse",
    )
    parser.add_argument(
        "--stale-only",
        action="store_true",
        help="Only show keys that are stale (unchanged > 90 days)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )


def run_age_command(args: argparse.Namespace) -> int:
    manager = SnapshotManager(store_path=args.store)
    snapshots = manager.list_snapshots(env_name=args.env)

    if not snapshots:
        print(f"No snapshots found for environment: {args.env}")
        return 1

    loaded = [manager.load(s["id"]) for s in snapshots]
    loaded = [s for s in loaded if s is not None]

    calculator = KeyAgeCalculator()
    report = calculator.calculate(loaded)

    formatter = AgeFormatter(color=not args.no_color)

    if args.stale_only:
        from envdiff.key_age import AgeReport
        report = AgeReport(entries=report.stale_keys)

    print(formatter.format_report(report))
    return 1 if report.has_stale else 0
