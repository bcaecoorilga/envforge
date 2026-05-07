"""CLI subcommand for interpolating variable references in a snapshot."""

import json
import sys
from argparse import ArgumentParser, Namespace

from envforge.interpolate import InterpolateError, interpolate, list_references


def cmd_interpolate(args: Namespace) -> None:
    """Resolve variable references inside a snapshot file."""
    try:
        with open(args.snapshot, "r") as fh:
            snapshot = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read snapshot: {exc}", file=sys.stderr)
        sys.exit(1)

    context: dict = {}
    for item in args.set or []:
        if "=" not in item:
            print(f"error: --set value must be KEY=VALUE, got: {item}", file=sys.stderr)
            sys.exit(1)
        k, v = item.split("=", 1)
        context[k] = v

    if args.list_refs:
        refs = list_references(snapshot)
        if not refs:
            print("No variable references found.")
            return
        for key, names in refs.items():
            print(f"  {key}: {', '.join(names)}")
        return

    try:
        result = interpolate(snapshot, context=context, strict=args.strict)
    except InterpolateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output + "\n")
        print(f"Interpolated snapshot written to {args.output}")
    else:
        print(output)


def add_interpolate_subcommand(subparsers) -> None:
    parser: ArgumentParser = subparsers.add_parser(
        "interpolate",
        help="Resolve $VAR / ${VAR} references within snapshot values.",
    )
    parser.add_argument("snapshot", help="Path to the snapshot JSON file.")
    parser.add_argument(
        "-o", "--output", metavar="FILE", help="Write result to FILE instead of stdout."
    )
    parser.add_argument(
        "--set",
        metavar="KEY=VALUE",
        action="append",
        help="Provide external values for unresolved references (repeatable).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if any reference cannot be resolved.",
    )
    parser.add_argument(
        "--list-refs",
        action="store_true",
        help="List all variable references found in the snapshot and exit.",
    )
    parser.set_defaults(func=cmd_interpolate)
