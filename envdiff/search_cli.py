import argparse
from typing import List

from envdiff.parser import parse_file
from envdiff.key_search import KeySearcher
from envdiff.search_formatter import SearchFormatter


def add_search_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("search", help="Search for keys or values across .env files")
    p.add_argument("query", help="Search term or glob pattern")
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to search")
    p.add_argument("--values", action="store_true", help="Also search in values")
    p.add_argument("--keys-only", action="store_true", help="Search keys only (default)")
    p.add_argument("--glob", action="store_true", help="Treat query as a glob pattern")
    p.add_argument("--no-color", action="store_true", help="Disable colored output")


def run_search_command(args: argparse.Namespace) -> int:
    envs = {}
    for path in args.files:
        try:
            envs[path] = parse_file(path)
        except FileNotFoundError:
            print(f"Error: file not found: {path}")
            return 2
        except Exception as exc:
            print(f"Error reading {path}: {exc}")
            return 2

    search_values = getattr(args, "values", False)
    searcher = KeySearcher(search_keys=True, search_values=search_values)
    result = searcher.search(envs, args.query, glob=getattr(args, "glob", False))

    formatter = SearchFormatter(color=not getattr(args, "no_color", False))
    print(formatter.format_result(result))

    return 0 if result.has_matches else 1
