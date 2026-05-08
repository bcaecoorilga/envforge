"""CLI commands for snapshot set management."""

import argparse
import json
import sys

from envforge.snapshot_set import (
    SnapshotSetError,
    create_set,
    add_to_set,
    remove_from_set,
    list_sets,
    get_set,
    delete_set,
)

DEFAULT_SET_FILE = "envforge_sets.json"


def cmd_snapshot_set(args: argparse.Namespace) -> int:
    path = getattr(args, "set_file", DEFAULT_SET_FILE)
    try:
        if args.set_action == "create":
            entry = create_set(path, args.name)
            print(f"Created snapshot set '{entry['name']}'.")

        elif args.set_action == "add":
            entry = add_to_set(path, args.name, args.label)
            print(f"Added '{args.label}' to set '{args.name}'. ({len(entry['snapshots'])} total)")

        elif args.set_action == "remove":
            entry = remove_from_set(path, args.name, args.label)
            print(f"Removed '{args.label}' from set '{args.name}'.")

        elif args.set_action == "list":
            sets = list_sets(path)
            if not sets:
                print("No snapshot sets found.")
            else:
                for s in sets:
                    labels = ", ".join(s["snapshots"]) if s["snapshots"] else "(empty)"
                    print(f"  {s['name']}: {labels}")

        elif args.set_action == "show":
            entry = get_set(path, args.name)
            if entry is None:
                print(f"Snapshot set '{args.name}' not found.", file=sys.stderr)
                return 1
            print(json.dumps(entry, indent=2))

        elif args.set_action == "delete":
            delete_set(path, args.name)
            print(f"Deleted snapshot set '{args.name}'.")

        else:
            print(f"Unknown set action: {args.set_action}", file=sys.stderr)
            return 1

    except SnapshotSetError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


def add_snapshot_set_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("set", help="Manage named snapshot sets")
    parser.add_argument("--set-file", default=DEFAULT_SET_FILE, help="Path to sets file")
    set_sub = parser.add_subparsers(dest="set_action", required=True)

    p_create = set_sub.add_parser("create", help="Create a new snapshot set")
    p_create.add_argument("name", help="Name of the set")

    p_add = set_sub.add_parser("add", help="Add a snapshot label to a set")
    p_add.add_argument("name", help="Name of the set")
    p_add.add_argument("label", help="Snapshot label to add")

    p_remove = set_sub.add_parser("remove", help="Remove a snapshot label from a set")
    p_remove.add_argument("name", help="Name of the set")
    p_remove.add_argument("label", help="Snapshot label to remove")

    set_sub.add_parser("list", help="List all snapshot sets")

    p_show = set_sub.add_parser("show", help="Show details of a snapshot set")
    p_show.add_argument("name", help="Name of the set")

    p_delete = set_sub.add_parser("delete", help="Delete a snapshot set")
    p_delete.add_argument("name", help="Name of the set")

    parser.set_defaults(func=cmd_snapshot_set)
