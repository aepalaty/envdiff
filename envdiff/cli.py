"""Command-line interface for envdiff."""

import sys
import argparse
from pathlib import Path

from envdiff.parser import parse_file
from envdiff.comparator import EnvComparator
from envdiff.formatter import DiffFormatter


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and surface missing or mismatched keys.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to compare (first file is treated as the baseline).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print a summary line after the diff.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with a non-zero status code if differences are found.",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    """Entry point for the CLI. Returns an exit code."""
    arg_parser = build_parser()
    args = arg_parser.parse_args(argv)

    if len(args.files) < 2:
        arg_parser.error("At least two .env files are required for comparison.")

    paths = [Path(f) for f in args.files]
    for path in paths:
        if not path.exists():
            print(f"envdiff: error: file not found: {path}", file=sys.stderr)
            return 2
        if not path.is_file():
            print(f"envdiff: error: not a file: {path}", file=sys.stderr)
            return 2

    baseline_path, *other_paths = paths
    baseline = parse_file(baseline_path)

    formatter = DiffFormatter(use_color=not args.no_color)
    has_differences = False

    for other_path in other_paths:
        other = parse_file(other_path)
        comparator = EnvComparator(baseline, other)
        difference = comparator.compare()

        label = f"{baseline_path}  vs  {other_path}"
        print(label)
        print("-" * len(label))

        output = formatter.format_difference(difference)
        if output:
            print(output)
            has_differences = True
        else:
            print("No differences found.")

        if args.summary:
            print(formatter.format_summary(difference))

        print()

    if args.exit_code and has_differences:
        return 1
    return 0


def main() -> None:
    """Main entry point installed as a console script."""
    sys.exit(run())


if __name__ == "__main__":
    main()
