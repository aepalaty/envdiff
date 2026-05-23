"""CLI subcommand for key collision detection."""
import argparse
from typing import Dict

from .key_collisions import KeyCollisionDetector
from .collision_formatter import CollisionFormatter
from .parser import parse_file


def add_collision_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "collisions",
        help="Detect keys that collide when compared case-insensitively.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to inspect.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output.",
    )


def run_collision_command(args: argparse.Namespace) -> int:
    if len(args.files) < 2:
        print("error: at least two files are required.")
        return 2

    envs: Dict[str, Dict[str, str]] = {}
    for path in args.files:
        try:
            envs[path] = parse_file(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}")
            return 2

    detector = KeyCollisionDetector()
    report = detector.calculate(envs)

    formatter = CollisionFormatter(color=not args.no_color)
    print(formatter.format_report(report))
    print()
    print(formatter.format_summary(report))

    return 1 if report.has_collisions else 0
