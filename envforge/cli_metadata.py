"""CLI subcommand for snapshot metadata management."""

from __future__ import annotations

import argparse
import json
import sys

from envforge.snapshot_metadata import (
    MetadataError,
    set_metadata,
    get_metadata,
    remove_metadata,
    clear_metadata,
    list_metadata,
)

DEFAULT_METADATA_FILE = "envforge_metadata.json"


def cmd_metadata(args: argparse.Namespace) -> None:
    mf = args.metadata_file
    try:
        if args.meta_action == "set":
            result = set_metadata(args.label, args.key, args.value, mf)
            print(f"Metadata set for '{args.label}': {args.key}={args.value}")
            if args.verbose:
                print(json.dumps(result, indent=2))

        elif args.meta_action == "get":
            result = get_metadata(args.label, mf)
            if not result:
                print(f"No metadata found for '{args.label}'.")
            else:
                print(json.dumps(result, indent=2))

        elif args.meta_action == "remove":
            remove_metadata(args.label, args.key, mf)
            print(f"Removed metadata key '{args.key}' from '{args.label}'.")

        elif args.meta_action == "clear":
            clear_metadata(args.label, mf)
            print(f"Cleared all metadata for '{args.label}'.")

        elif args.meta_action == "list":
            result = list_metadata(mf)
            if not result:
                print("No metadata entries found.")
            else:
                print(json.dumps(result, indent=2))

    except MetadataError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_metadata_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("metadata", help="Manage snapshot metadata")
    parser.add_argument(
        "--metadata-file",
        default=DEFAULT_METADATA_FILE,
        help="Path to metadata store (default: %(default)s)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show full output")

    meta_sub = parser.add_subparsers(dest="meta_action", required=True)

    p_set = meta_sub.add_parser("set", help="Set a metadata key on a snapshot")
    p_set.add_argument("label", help="Snapshot label")
    p_set.add_argument("key", help="Metadata key")
    p_set.add_argument("value", help="Metadata value")

    p_get = meta_sub.add_parser("get", help="Get all metadata for a snapshot")
    p_get.add_argument("label", help="Snapshot label")

    p_rm = meta_sub.add_parser("remove", help="Remove a metadata key from a snapshot")
    p_rm.add_argument("label", help="Snapshot label")
    p_rm.add_argument("key", help="Metadata key to remove")

    p_cl = meta_sub.add_parser("clear", help="Clear all metadata for a snapshot")
    p_cl.add_argument("label", help="Snapshot label")

    meta_sub.add_parser("list", help="List all metadata entries")

    parser.set_defaults(func=cmd_metadata)
