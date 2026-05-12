"""CLI subcommand for snapshot archive operations."""

import argparse
import json
import sys

from envforge.snapshot_archive import (
    ArchiveError,
    create_archive,
    list_archive,
    extract_archive,
    extract_one,
)
from envforge.snapshot import load, save


def cmd_archive(args: argparse.Namespace) -> None:
    action = args.archive_action

    if action == "create":
        snapshots = []
        for path in args.snapshots:
            try:
                snapshots.append(load(path))
            except Exception as exc:
                print(f"Error loading '{path}': {exc}", file=sys.stderr)
                sys.exit(1)
        try:
            create_archive(snapshots, args.output)
            print(f"Archive created: {args.output} ({len(snapshots)} snapshot(s))")
        except ArchiveError as exc:
            print(f"Archive error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif action == "list":
        try:
            entries = list_archive(args.archive)
            if not entries:
                print("Archive is empty.")
            else:
                for entry in entries:
                    print(f"  {entry['label']}  ->  {entry['file']}")
        except ArchiveError as exc:
            print(f"Archive error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif action == "extract":
        try:
            if args.label:
                snapshots = [extract_one(args.archive, args.label)]
            else:
                snapshots = extract_archive(args.archive)
            for snap in snapshots:
                out_path = f"{snap['label']}.json"
                save(snap, out_path)
                print(f"Extracted: {out_path}")
        except ArchiveError as exc:
            print(f"Archive error: {exc}", file=sys.stderr)
            sys.exit(1)

    else:
        print(f"Unknown archive action: {action}", file=sys.stderr)
        sys.exit(1)


def add_archive_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("archive", help="Bundle snapshots into a zip archive.")
    archive_sub = parser.add_subparsers(dest="archive_action", required=True)

    p_create = archive_sub.add_parser("create", help="Create an archive from snapshot files.")
    p_create.add_argument("snapshots", nargs="+", help="Snapshot JSON files to include.")
    p_create.add_argument("-o", "--output", required=True, help="Output archive path (.zip).")

    p_list = archive_sub.add_parser("list", help="List snapshots in an archive.")
    p_list.add_argument("archive", help="Path to the archive file.")

    p_extract = archive_sub.add_parser("extract", help="Extract snapshots from an archive.")
    p_extract.add_argument("archive", help="Path to the archive file.")
    p_extract.add_argument("--label", default=None, help="Extract only the named snapshot.")

    parser.set_defaults(func=cmd_archive)
