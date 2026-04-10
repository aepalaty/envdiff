"""CLI helpers for --include / --exclude / --prefix flags."""

from __future__ import annotations

import argparse
from typing import Dict, List, Optional

from envdiff.key_filter import KeyFilter, KeyFilterConfig


def add_filter_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach key-filter flags to an existing ArgumentParser."""
    parser.add_argument(
        "--include",
        metavar="PATTERN",
        nargs="+",
        default=[],
        help="Only include keys matching these glob patterns.",
    )
    parser.add_argument(
        "--exclude",
        metavar="PATTERN",
        nargs="+",
        default=[],
        help="Exclude keys matching these glob patterns.",
    )
    parser.add_argument(
        "--prefix",
        metavar="PREFIX",
        nargs="+",
        default=[],
        dest="prefixes",
        help="Only include keys starting with these prefixes.",
    )


def build_filter_from_args(args: argparse.Namespace) -> KeyFilter:
    """Construct a KeyFilter from parsed CLI arguments."""
    cfg = KeyFilterConfig(
        include_patterns=getattr(args, "include", []),
        exclude_patterns=getattr(args, "exclude", []),
        prefixes=getattr(args, "prefixes", []),
    )
    return KeyFilter(cfg)


def apply_filter_to_envs(
    envs: Dict[str, Dict[str, str]],
    key_filter: KeyFilter,
) -> Dict[str, Dict[str, str]]:
    """Apply *key_filter* to every env dict in *envs* and return the filtered mapping."""
    return {name: key_filter.apply(env) for name, env in envs.items()}
