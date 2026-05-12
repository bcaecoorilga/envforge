"""CLI subcommand for snapshot alias management."""

import argparse
import sys

from envforge.snapshot_alias import (
    AliasError,
    add_alias,
    update_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
)

DEFAULT_ALIAS_FILE = ".envforge_aliases.json"


def cmd_alias(args: argparse.Namespace) -> int:
    alias_file = getattr(args, "alias_file", DEFAULT_ALIAS_FILE)

    try:
        if args.alias_action == "add":
            add_alias(args.alias, args.label, alias_file)
            print(f"Alias '{args.alias}' -> '{args.label}' added.")

        elif args.alias_action == "update":
            update_alias(args.alias, args.label, alias_file)
            print(f"Alias '{args.alias}' updated to '{args.label}'.")

        elif args.alias_action == "remove":
            remove_alias(args.alias, alias_file)
            print(f"Alias '{args.alias}' removed.")

        elif args.alias_action == "resolve":
            label = resolve_alias(args.alias, alias_file)
            if label is None:
                print(f"No alias found for '{args.alias}'.")
                return 1
            print(label)

        elif args.alias_action == "list":
            entries = list_aliases(alias_file)
            if not entries:
                print("No aliases defined.")
            else:
                for entry in entries:
                    print(f"{entry['alias']:20s} -> {entry['label']}")

        else:
            print(f"Unknown alias action: {args.alias_action}", file=sys.stderr)
            return 2

    except AliasError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


def add_alias_subcommand(subparsers: argparse._SubParsersAction) -> None:
    alias_parser = subparsers.add_parser("alias", help="Manage snapshot aliases")
    alias_parser.add_argument(
        "--alias-file", default=DEFAULT_ALIAS_FILE, help="Path to alias store"
    )
    alias_sub = alias_parser.add_subparsers(dest="alias_action", required=True)

    # add
    p_add = alias_sub.add_parser("add", help="Add a new alias")
    p_add.add_argument("alias", help="Alias name")
    p_add.add_argument("label", help="Snapshot label")

    # update
    p_update = alias_sub.add_parser("update", help="Update an existing alias")
    p_update.add_argument("alias", help="Alias name")
    p_update.add_argument("label", help="New snapshot label")

    # remove
    p_remove = alias_sub.add_parser("remove", help="Remove an alias")
    p_remove.add_argument("alias", help="Alias name")

    # resolve
    p_resolve = alias_sub.add_parser("resolve", help="Resolve alias to label")
    p_resolve.add_argument("alias", help="Alias name")

    # list
    alias_sub.add_parser("list", help="List all aliases")

    alias_parser.set_defaults(func=cmd_alias)
