"""CLI subcommand for importing snapshots from external formats."""

import argparse
import json
import sys

from envforge.snapshot_import import ImportError, from_dotenv, from_json, from_shell_env


def cmd_import(args: argparse.Namespace) -> None:
    """Handle the import subcommand."""
    try:
        if args.format == "dotenv":
            if not args.input:
                print("error: --input is required for dotenv format", file=sys.stderr)
                sys.exit(1)
            snapshot = from_dotenv(args.input, label=args.label)
        elif args.format == "json":
            if not args.input:
                print("error: --input is required for json format", file=sys.stderr)
                sys.exit(1)
            snapshot = from_json(args.input, label=args.label)
        elif args.format == "shell":
            snapshot = from_shell_env(
                prefix=args.prefix,
                label=args.label or "shell-import",
            )
        else:
            print(f"error: unknown format '{args.format}'", file=sys.stderr)
            sys.exit(1)
    except ImportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(snapshot, indent=2)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(output)
            print(f"Snapshot '{snapshot['label']}' imported to {args.output}")
        except OSError as exc:
            print(f"error: cannot write output file: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


def add_import_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the import subcommand."""
    parser = subparsers.add_parser(
        "import",
        help="Import environment variables from an external format into a snapshot.",
    )
    parser.add_argument(
        "format",
        choices=["dotenv", "json", "shell"],
        help="Source format to import from.",
    )
    parser.add_argument(
        "--input", "-i",
        metavar="FILE",
        help="Path to the source file (required for dotenv and json formats).",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write the resulting snapshot to this file (default: stdout).",
    )
    parser.add_argument(
        "--label", "-l",
        metavar="LABEL",
        help="Override the snapshot label.",
    )
    parser.add_argument(
        "--prefix",
        metavar="PREFIX",
        help="Filter by key prefix (shell format only).",
    )
    parser.set_defaults(func=cmd_import)
