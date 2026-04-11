"""CLI integration for key rename detection."""
import argparse
from typing import List

from envdiff.parser import parse_file
from envdiff.comparator import EnvComparator
from envdiff.key_rename import KeyRenameDetector


def add_rename_subcommand(subparsers) -> None:
    parser = subparsers.add_parser(
        "rename",
        help="Detect possible key renames between two .env files",
    )
    parser.add_argument("baseline", help="Baseline .env file")
    parser.add_argument("target", help="Target .env file to compare against")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.6,
        help="Minimum similarity score to suggest a rename (default: 0.6)",
    )
    parser.add_argument(
        "--no-value-boost",
        action="store_true",
        default=False,
        help="Disable score boost for matching values",
    )


def run_rename_command(args: argparse.Namespace) -> int:
    try:
        old_env = parse_file(args.baseline)
        new_env = parse_file(args.target)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1

    comparator = EnvComparator(old_env, new_env)
    diff = comparator.compare()

    missing = list(diff.missing_keys)
    extra = list(diff.extra_keys)

    if not missing and not extra:
        print("No missing or extra keys — nothing to rename.")
        return 0

    detector = KeyRenameDetector(
        threshold=args.threshold,
        prefer_value_match=not args.no_value_boost,
    )
    report = detector.detect(old_env, new_env, missing, extra)

    if report.has_candidates():
        print(f"Rename candidates ({len(report.candidates)}):")
        for candidate in report.candidates:
            print(f"  {candidate}")
    else:
        print("No rename candidates found.")

    if report.unmatched_old:
        print(f"\nUnmatched removed keys: {', '.join(report.unmatched_old)}")
    if report.unmatched_new:
        print(f"Unmatched added keys:   {', '.join(report.unmatched_new)}")

    return 0
