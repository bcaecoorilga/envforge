"""CLI subcommand for managing snapshot groups."""

import argparse
import json
import sys

from envforge.snapshot_group import (
    GroupError,
    create_group,
    add_to_group,
    remove_from_group,
    get_group,
    list_groups,
    delete_group,
)

DEFAULT_GROUP_FILE = "groups.json"


def cmd_group(args: argparse.Namespace) -> None:
    gf = getattr(args, "group_file", DEFAULT_GROUP_FILE)
    try:
        if args.group_action == "create":
            entry = create_group(args.name, description=args.description or "", group_file=gf)
            print(f"Created group '{entry['name']}'.")

        elif args.group_action == "add":
            entry = add_to_group(args.name, args.label, group_file=gf)
            print(f"Added '{args.label}' to group '{args.name}'. Labels: {entry['labels']}")

        elif args.group_action == "remove":
            entry = remove_from_group(args.name, args.label, group_file=gf)
            print(f"Removed '{args.label}' from group '{args.name}'.")

        elif args.group_action == "show":
            entry = get_group(args.name, group_file=gf)
            print(json.dumps(entry, indent=2))

        elif args.group_action == "list":
            groups = list_groups(group_file=gf)
            if not groups:
                print("No groups defined.")
            else:
                for g in groups:
                    label_count = len(g["labels"])
                    print(f"  {g['name']} ({label_count} snapshot(s)) — {g['description']}")

        elif args.group_action == "delete":
            delete_group(args.name, group_file=gf)
            print(f"Deleted group '{args.name}'.")

        else:
            print(f"Unknown group action: {args.group_action}", file=sys.stderr)
            sys.exit(1)

    except GroupError as exc:
        print(f"Group error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_group_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("group", help="Manage snapshot groups")
    p.add_argument("--group-file", default=DEFAULT_GROUP_FILE, help="Path to groups file")
    sub = p.add_subparsers(dest="group_action", required=True)

    c = sub.add_parser("create", help="Create a new group")
    c.add_argument("name", help="Group name")
    c.add_argument("--description", default="", help="Optional description")

    a = sub.add_parser("add", help="Add a snapshot label to a group")
    a.add_argument("name", help="Group name")
    a.add_argument("label", help="Snapshot label to add")

    r = sub.add_parser("remove", help="Remove a snapshot label from a group")
    r.add_argument("name", help="Group name")
    r.add_argument("label", help="Snapshot label to remove")

    s = sub.add_parser("show", help="Show details of a group")
    s.add_argument("name", help="Group name")

    sub.add_parser("list", help="List all groups")

    d = sub.add_parser("delete", help="Delete a group")
    d.add_argument("name", help="Group name")

    p.set_defaults(func=cmd_group)
