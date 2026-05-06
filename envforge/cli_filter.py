"""CLI subcommands for filtering and searching snapshot variables."""

import argparse
import json
import sys

from envforge.filter import FilterError, filter_by_prefix, filter_by_pattern, exclude_keys, search_values, list_keys
from envforge.snapshot import load


def cmd_filter(args: argparse.Namespace) -> int:
    """Filter a snapshot by prefix or pattern and print matching variables."""
    try:
        snapshot = load(args.file)
    except (OSError, ValueError) as exc:
        print(f"Error loading snapshot: {exc}", file=sys.stderr)
        return 1

    try:
        if args.prefix:
            result = filter_by_prefix(snapshot, args.prefix)
        elif args.pattern:
            result = filter_by_pattern(snapshot, args.pattern)
        elif args.exclude:
            result = exclude_keys(snapshot, args.exclude)
        elif args.search:
            matches = search_values(snapshot, args.search)
            for key, value in sorted(matches.items()):
                print(f"{key}={value}")
            return 0
        elif args.list_keys:
            for key in list_keys(snapshot):
                print(key)
            return 0
        else:
            result = snapshot

        if args.output_format == "json":
            print(json.dumps(result["variables"], indent=2))
        else:
            for key, value in sorted(result["variables"].items()):
                print(f"{key}={value}")

    except FilterError as exc:
        print(f"Filter error: {exc}", file=sys.stderr)
        return 1

    return 0


def add_filter_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'filter' subcommand on the given subparsers."""
    parser = subparsers.add_parser(
        "filter",
        help="Filter or search variables in a snapshot",
    )
    parser.add_argument("file", help="Path to snapshot JSON file")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--prefix", metavar="PREFIX", help="Keep only keys with this prefix")
    group.add_argument("--pattern", metavar="REGEX", help="Keep only keys matching this regex")
    group.add_argument("--exclude", nargs="+", metavar="KEY", help="Remove specified keys")
    group.add_argument("--search", metavar="TERM", help="Search variable values for a term")
    group.add_argument("--list-keys", action="store_true", dest="list_keys", help="List all variable keys")

    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["dotenv", "json"],
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    parser.set_defaults(func=cmd_filter)
