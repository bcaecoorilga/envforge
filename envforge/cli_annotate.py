"""cli_annotate.py — CLI subcommand for snapshot annotation."""

from __future__ import annotations

import argparse
import sys

from envforge.annotate import AnnotateError, add_note, get_notes, list_annotated_labels, remove_notes

DEFAULT_ANNOTATIONS_FILE = ".envforge_annotations.json"


def cmd_annotate(args: argparse.Namespace) -> None:
    path = getattr(args, "annotations_file", DEFAULT_ANNOTATIONS_FILE)

    try:
        if args.annotate_cmd == "add":
            entry = add_note(args.label, args.note, path)
            print(f"Note added to '{args.label}' at {entry['timestamp']}")

        elif args.annotate_cmd == "list":
            notes = get_notes(args.label, path)
            if not notes:
                print(f"No notes for '{args.label}'.")
            else:
                for i, n in enumerate(notes, 1):
                    print(f"[{i}] {n['timestamp']}  {n['note']}")

        elif args.annotate_cmd == "remove":
            count = remove_notes(args.label, path)
            print(f"Removed {count} note(s) from '{args.label}'.")

        elif args.annotate_cmd == "labels":
            labels = list_annotated_labels(path)
            if not labels:
                print("No annotated snapshots found.")
            else:
                for label in labels:
                    print(label)

        else:
            print("Unknown annotate subcommand.", file=sys.stderr)
            sys.exit(1)

    except AnnotateError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_annotate_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("annotate", help="Manage notes attached to snapshots")
    p.add_argument(
        "--annotations-file",
        default=DEFAULT_ANNOTATIONS_FILE,
        dest="annotations_file",
        metavar="FILE",
        help="Path to the annotations store (default: %(default)s)",
    )

    sub = p.add_subparsers(dest="annotate_cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="Attach a note to a snapshot")
    p_add.add_argument("label", help="Snapshot label")
    p_add.add_argument("note", help="Note text")

    # list
    p_list = sub.add_parser("list", help="List notes for a snapshot")
    p_list.add_argument("label", help="Snapshot label")

    # remove
    p_remove = sub.add_parser("remove", help="Remove all notes for a snapshot")
    p_remove.add_argument("label", help="Snapshot label")

    # labels
    sub.add_parser("labels", help="List all annotated snapshot labels")

    p.set_defaults(func=cmd_annotate)
