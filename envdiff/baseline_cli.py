"""CLI sub-commands for baseline management."""

from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.baseline import BaselineManager
from envdiff.parser import parse_file


def add_baseline_subcommands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    baseline_parser = subparsers.add_parser("baseline", help="Manage env baselines")
    sub = baseline_parser.add_subparsers(dest="baseline_cmd", required=True)

    rec = sub.add_parser("record", help="Record an env file as the baseline")
    rec.add_argument("file", help="Path to the .env file")
    rec.add_argument("--label", default=None, help="Optional label for this baseline")
    rec.add_argument("--store", default=None, help="Custom baseline store path")

    show = sub.add_parser("show", help="Show the recorded baseline for a file")
    show.add_argument("file", help="Path to the .env file")
    show.add_argument("--store", default=None, help="Custom baseline store path")

    rm = sub.add_parser("remove", help="Remove a recorded baseline")
    rm.add_argument("file", help="Path to the .env file")
    rm.add_argument("--store", default=None, help="Custom baseline store path")

    lst = sub.add_parser("list", help="List all recorded baselines")
    lst.add_argument("--store", default=None, help="Custom baseline store path")


def run_baseline_command(args: argparse.Namespace) -> int:
    kwargs = {}
    if getattr(args, "store", None):
        kwargs["store_path"] = args.store
    manager = BaselineManager(**kwargs)

    cmd = args.baseline_cmd

    if cmd == "record":
        try:
            env = parse_file(args.file)
        except FileNotFoundError:
            print(f"error: file not found: {args.file}", file=sys.stderr)
            return 1
        entry = manager.record(args.file, env, label=args.label)
        label_info = f" (label: {entry.label})" if entry.label else ""
        print(f"Baseline recorded for {args.file}{label_info} at {entry.recorded_at}")
        return 0

    if cmd == "show":
        entry = manager.get(args.file)
        if entry is None:
            print(f"No baseline found for {args.file}", file=sys.stderr)
            return 1
        label_info = f"Label   : {entry.label}\n" if entry.label else ""
        print(f"File    : {entry.path}\n{label_info}Recorded: {entry.recorded_at}\nKeys    : {len(entry.env)}")
        return 0

    if cmd == "remove":
        removed = manager.remove(args.file)
        if not removed:
            print(f"No baseline found for {args.file}", file=sys.stderr)
            return 1
        print(f"Baseline removed for {args.file}")
        return 0

    if cmd == "list":
        entries = manager.list_all()
        if not entries:
            print("No baselines recorded.")
            return 0
        for path, entry in entries.items():
            label = f" [{entry.label}]" if entry.label else ""
            print(f"{path}{label} — {len(entry.env)} keys — recorded {entry.recorded_at}")
        return 0

    print(f"Unknown baseline command: {cmd}", file=sys.stderr)
    return 1
