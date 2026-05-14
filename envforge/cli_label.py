"""CLI subcommand for snapshot label management."""

from __future__ import annotations

import argparse
import sys

from envforge.snapshot_label import (
    LabelError,
    list_labels,
    register_label,
    rename_label,
    resolve_label,
    unregister_label,
)

DEFAULT_LABEL_FILE = ".envforge_labels.json"


def cmd_label(args: argparse.Namespace) -> None:
    label_file = args.label_file

    if args.label_action == "register":
        try:
            register_label(args.label, args.path, label_file)
            print(f"Registered '{args.label}' -> {args.path}")
        except LabelError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.label_action == "unregister":
        try:
            unregister_label(args.label, label_file)
            print(f"Unregistered label '{args.label}'.")
        except LabelError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.label_action == "resolve":
        path = resolve_label(args.label, label_file)
        if path is None:
            print(f"Label '{args.label}' is not registered.", file=sys.stderr)
            sys.exit(1)
        print(path)

    elif args.label_action == "list":
        entries = list_labels(label_file)
        if not entries:
            print("No labels registered.")
        else:
            for entry in entries:
                print(f"{entry['label']:30s}  {entry['path']}")

    elif args.label_action == "rename":
        try:
            rename_label(args.old_label, args.new_label, label_file)
            print(f"Renamed '{args.old_label}' to '{args.new_label}'.")
        except LabelError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)


def add_label_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("label", help="Manage snapshot labels")
    parser.add_argument(
        "--label-file", default=DEFAULT_LABEL_FILE, help="Label registry file"
    )
    label_sub = parser.add_subparsers(dest="label_action", required=True)

    reg = label_sub.add_parser("register", help="Register a label for a snapshot file")
    reg.add_argument("label", help="Label name")
    reg.add_argument("path", help="Path to snapshot file")

    unreg = label_sub.add_parser("unregister", help="Remove a label registration")
    unreg.add_argument("label", help="Label name")

    res = label_sub.add_parser("resolve", help="Print the path for a label")
    res.add_argument("label", help="Label name")

    label_sub.add_parser("list", help="List all registered labels")

    ren = label_sub.add_parser("rename", help="Rename a label")
    ren.add_argument("old_label", help="Existing label name")
    ren.add_argument("new_label", help="New label name")

    parser.set_defaults(func=cmd_label)
