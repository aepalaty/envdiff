"""CLI subcommand: envdiff template — generate a .env.example file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from envdiff.env_template import TemplateGenerator
from envdiff.parser import parse_file
from envdiff.redactor import Redactor
from envdiff.template_writer import TemplateWriter


def add_template_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "template",
        help="Generate a .env.example template from an env file",
    )
    parser.add_argument("env_file", help="Source .env file")
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output path (default: print to stdout)",
    )
    parser.add_argument(
        "--placeholder",
        default="CHANGE_ME",
        help="Placeholder for sensitive values (default: CHANGE_ME)",
    )
    parser.add_argument(
        "--required",
        nargs="*",
        default=[],
        metavar="KEY",
        help="Keys to mark as required (default: all)",
    )


def run_template_command(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"Error: file not found: {env_path}", file=sys.stderr)
        return 1

    env = parse_file(env_path)
    redactor = Redactor()
    generator = TemplateGenerator(
        redactor=redactor,
        placeholder=args.placeholder,
        required_keys=args.required or None,
    )
    template = generator.generate(env)
    writer = TemplateWriter()

    if args.output:
        out_path = Path(args.output)
        writer._output_path = out_path
        writer.write(template)
        print(f"Template written to {out_path}")
    else:
        writer.print(template)

    return 0
