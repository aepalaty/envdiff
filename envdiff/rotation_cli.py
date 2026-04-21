"""CLI subcommand for key rotation analysis."""
import argparse
import sys
from envdiff.snapshot import SnapshotManager
from envdiff.key_age import AgeCalculator
from envdiff.key_sensitivity import SensitivityCalculator
from envdiff.key_rotation import RotationCalculator
from envdiff.rotation_formatter import RotationFormatter


def add_rotation_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "rotation",
        help="Identify keys overdue for rotation based on age and sensitivity",
    )
    parser.add_argument(
        "--store",
        default=".envdiff_snapshots",
        help="Path to snapshot store directory (default: .envdiff_snapshots)",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=None,
        help="Override default max-days threshold for all tiers",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only the summary line",
    )


def run_rotation_command(args: argparse.Namespace) -> int:
    manager = SnapshotManager(store_dir=args.store)
    snapshots = manager.list_snapshots()

    if len(snapshots) < 2:
        print("Need at least 2 snapshots to compute rotation data.", file=sys.stderr)
        return 1

    age_calculator = AgeCalculator()
    age_report = age_calculator.calculate(snapshots)

    all_envs = {}
    for snap in snapshots:
        all_envs[snap.label or snap.timestamp] = snap.env

    sensitivity_calculator = SensitivityCalculator()
    sensitivity_report = sensitivity_calculator.calculate(all_envs)

    rotation_calculator = RotationCalculator()
    report = rotation_calculator.calculate(age_report, sensitivity_report)

    formatter = RotationFormatter(use_color=not args.no_color)

    if args.summary_only:
        print(formatter.format_summary(report))
    else:
        print(formatter.format_report(report))

    return 1 if report.has_overdue else 0
