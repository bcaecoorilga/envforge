"""CLI commands for managing per-key notes on snapshots."""

import argparse
import json
import sys

from envforge.snapshot_notes import (
    NotesError,
    add_key_note,
    remove_key_note,
    get_key_notes,
    clear_key_notes,
)


def cmd_notes(args: argparse.Namespace) -> None:
    try:
        with open(args.file, "r") as fh:
            snapshot = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error loading snapshot: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.notes_cmd == "add":
            result = add_key_note(snapshot, args.key, args.note)
            _write_snapshot(result, args.output or args.file)
            print(f"Note added for key '{args.key}'.")

        elif args.notes_cmd == "remove":
            result = remove_key_note(snapshot, args.key)
            _write_snapshot(result, args.output or args.file)
            print(f"Note removed for key '{args.key}'.")

        elif args.notes_cmd == "list":
            notes = get_key_notes(snapshot)
            if not notes:
                print("No notes found.")
            else:
                for key, note in sorted(notes.items()):
                    print(f"  {key}: {note}")

        elif args.notes_cmd == "clear":
            result = clear_key_notes(snapshot)
            _write_snapshot(result, args.output or args.file)
            print("All notes cleared.")

    except NotesError as exc:
        print(f"Notes error: {exc}", file=sys.stderr)
        sys.exit(1)


def _write_snapshot(snapshot: dict, path: str) -> None:
    with open(path, "w") as fh:
        json.dump(snapshot, fh, indent=2)


def add_notes_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("notes", help="Manage per-key notes on a snapshot")
    parser.add_argument("file", help="Path to the snapshot JSON file")
    parser.add_argument("-o", "--output", help="Output file (defaults to input file)")

    sub = parser.add_subparsers(dest="notes_cmd", required=True)

    add_p = sub.add_parser("add", help="Add a note to a key")
    add_p.add_argument("key", help="Variable key")
    add_p.add_argument("note", help="Note text")

    rm_p = sub.add_parser("remove", help="Remove the note from a key")
    rm_p.add_argument("key", help="Variable key")

    sub.add_parser("list", help="List all key notes")
    sub.add_parser("clear", help="Remove all key notes")

    parser.set_defaults(func=cmd_notes)
