"""CLI helpers for snapshot sub-commands (capture / diff)."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.formatter import DiffFormatter
from envdiff.parser import parse_file
from envdiff.snapshot import SnapshotManager
from envdiff.snapshot_diff import SnapshotDiffer


def add_snapshot_subcommands(subparsers: argparse._SubParsersAction) -> None:
    """Register 'snapshot' sub-commands onto an existing subparsers group."""
    snap_parser = subparsers.add_parser("snapshot", help="Capture or diff env snapshots")
    snap_sub = snap_parser.add_subparsers(dest="snap_cmd", required=True)

    # capture
    cap = snap_sub.add_parser("capture", help="Capture a snapshot of an env file")
    cap.add_argument("env_file", help="Path to the .env file to snapshot")
    cap.add_argument("--label", default=None, help="Human-readable label for this snapshot")
    cap.add_argument("--dir", dest="snapshot_dir", default=".envdiff_snapshots",
                     help="Directory to store snapshots (default: .envdiff_snapshots)")
    cap.add_argument("--output", default=None, help="Override output filename")

    # diff
    dif = snap_sub.add_parser("diff", help="Diff two snapshot files")
    dif.add_argument("baseline", help="Path to baseline snapshot JSON")
    dif.add_argument("other", help="Path to other snapshot JSON")
    dif.add_argument("--no-color", action="store_true", help="Disable colour output")
    dif.add_argument("--dir", dest="snapshot_dir", default=".envdiff_snapshots")

    # list
    lst = snap_sub.add_parser("list", help="List saved snapshots")
    lst.add_argument("--dir", dest="snapshot_dir", default=".envdiff_snapshots")


def run_snapshot_command(args: argparse.Namespace) -> int:
    """Dispatch to the appropriate snapshot sub-command handler."""
    manager = SnapshotManager(snapshot_dir=args.snapshot_dir)

    if args.snap_cmd == "capture":
        env = parse_file(args.env_file)
        snap = manager.capture(env, source=args.env_file, label=args.label)
        path = manager.save(snap, filename=args.output)
        print(f"Snapshot saved: {path}")
        return 0

    if args.snap_cmd == "diff":
        differ = SnapshotDiffer()
        result = differ.diff_from_files(args.baseline, args.other, manager=manager)
        formatter = DiffFormatter(use_color=not args.no_color)
        print(formatter.format_difference(result))
        print(formatter.format_summary([result]))
        return 1 if (result.missing_keys or result.extra_keys or result.mismatched_keys) else 0

    if args.snap_cmd == "list":
        snapshots = manager.list_snapshots()
        if not snapshots:
            print("No snapshots found.")
        else:
            for p in snapshots:
                print(str(p))
        return 0

    print(f"Unknown snapshot command: {args.snap_cmd}", file=sys.stderr)
    return 2
