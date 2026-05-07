"""CLI subcommand for snapshot variable transformations."""

import argparse
import json
import sys

from envforge.snapshot import load, save
from envforge.transform import (
    TransformError,
    prefix_keys,
    strip_prefix,
    uppercase_keys,
    substitute_values,
)


def cmd_transform(args: argparse.Namespace) -> None:
    try:
        snapshot = load(args.input)
    except Exception as exc:
        print(f"Error loading snapshot: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.transform_cmd == "prefix":
            result = prefix_keys(snapshot, args.prefix)
        elif args.transform_cmd == "strip-prefix":
            result = strip_prefix(snapshot, args.prefix)
        elif args.transform_cmd == "uppercase":
            result = uppercase_keys(snapshot)
        elif args.transform_cmd == "substitute":
            replacements = dict(pair.split("=", 1) for pair in args.replace)
            result = substitute_values(snapshot, replacements)
        else:
            print(f"Unknown transform: {args.transform_cmd}", file=sys.stderr)
            sys.exit(1)
    except TransformError as exc:
        print(f"Transform error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Invalid replacement format: {exc}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or args.input
    try:
        save(result, output_path)
        print(f"Transformed snapshot saved to '{output_path}'.")
    except Exception as exc:
        print(f"Error saving snapshot: {exc}", file=sys.stderr)
        sys.exit(1)


def add_transform_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("transform", help="Transform keys/values in a snapshot")
    parser.add_argument("input", help="Path to input snapshot JSON file")
    parser.add_argument("-o", "--output", default=None, help="Output file (default: overwrite input)")

    tsub = parser.add_subparsers(dest="transform_cmd", required=True)

    p_prefix = tsub.add_parser("prefix", help="Add a prefix to all keys")
    p_prefix.add_argument("prefix", help="Prefix string to add")

    p_strip = tsub.add_parser("strip-prefix", help="Remove a prefix from matching keys")
    p_strip.add_argument("prefix", help="Prefix string to remove")

    tsub.add_parser("uppercase", help="Convert all keys to uppercase")

    p_sub = tsub.add_parser("substitute", help="Replace substrings in values")
    p_sub.add_argument(
        "-r", "--replace",
        action="append",
        required=True,
        metavar="OLD=NEW",
        help="Replacement pair (can be repeated)",
    )

    parser.set_defaults(func=cmd_transform)
