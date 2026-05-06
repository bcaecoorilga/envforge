"""CLI subcommand for redacting sensitive values in snapshots."""

import argparse
import json
import sys

from envforge.redact import redact_by_patterns, redact_keys, list_sensitive_keys, RedactError
from envforge.snapshot import load, save


def cmd_redact(args: argparse.Namespace) -> None:
    try:
        snapshot = load(args.input)
    except Exception as exc:
        print(f"Error loading snapshot: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.list_only:
            sensitive = list_sensitive_keys(snapshot, patterns=args.pattern or None)
            if sensitive:
                print("Sensitive keys detected:")
                for key in sensitive:
                    print(f"  {key}")
            else:
                print("No sensitive keys detected.")
            return

        if args.keys:
            result = redact_keys(snapshot, keys=args.keys)
        else:
            result = redact_by_patterns(snapshot, patterns=args.pattern or None)

        output_path = args.output or args.input
        save(result, output_path)
        print(f"Redacted snapshot saved to: {output_path}")

    except RedactError as exc:
        print(f"Redact error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_redact_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "redact",
        help="Redact sensitive variable values from a snapshot.",
    )
    parser.add_argument("input", help="Path to the input snapshot JSON file.")
    parser.add_argument("-o", "--output", help="Output path (defaults to overwriting input).")
    parser.add_argument(
        "--pattern",
        action="append",
        metavar="REGEX",
        help="Custom regex pattern to match sensitive keys (repeatable).",
    )
    parser.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Explicit key names to redact.",
    )
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Only list sensitive keys; do not modify the snapshot.",
    )
    parser.set_defaults(func=cmd_redact)
