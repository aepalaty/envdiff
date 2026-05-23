import argparse
import json
from pathlib import Path

from envdiff.key_lineage import LineageCalculator
from envdiff.lineage_formatter import LineageFormatter


def add_lineage_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "lineage",
        help="Trace the history of each key across ordered snapshot files.",
    )
    p.add_argument(
        "snapshots",
        nargs="+",
        metavar="SNAPSHOT",
        help="Ordered snapshot JSON files (oldest first). Each must contain {label, env}.",
    )
    p.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output.",
    )


def run_lineage_command(args: argparse.Namespace) -> int:
    snapshots = []
    for path_str in args.snapshots:
        path = Path(path_str)
        if not path.exists():
            print(f"error: snapshot file not found: {path}")
            return 1
        with path.open() as f:
            data = json.load(f)
        if "label" not in data or "env" not in data:
            print(f"error: snapshot {path} must have 'label' and 'env' keys")
            return 1
        snapshots.append(data)

    calculator = LineageCalculator()
    report = calculator.calculate(snapshots)

    formatter = LineageFormatter(color=not args.no_color)
    print(formatter.format_report(report))
    return 0
