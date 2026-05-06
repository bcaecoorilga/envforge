"""CLI integration for the export subcommand."""

import sys
import argparse
from envforge.snapshot import load
from envforge.export import export_snapshot, ExportError, SUPPORTED_FORMATS


def cmd_export(args: argparse.Namespace) -> int:
    """Handle the 'export' subcommand.

    Loads a snapshot from a file and writes it to stdout (or a file)
    in the requested format.

    Returns:
        Exit code (0 on success, 1 on failure).
    """
    try:
        snapshot = load(args.snapshot_file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"envforge export: error loading snapshot: {exc}", file=sys.stderr)
        return 1

    try:
        output = export_snapshot(snapshot, args.format)
    except ExportError as exc:
        print(f"envforge export: {exc}", file=sys.stderr)
        return 1

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(output)
            print(f"Exported snapshot '{snapshot['label']}' to {args.output} ({args.format})")
        except OSError as exc:
            print(f"envforge export: cannot write to '{args.output}': {exc}", file=sys.stderr)
            return 1
    else:
        sys.stdout.write(output)

    return 0


def add_export_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'export' subcommand on an existing subparsers object."""
    parser = subparsers.add_parser(
        "export",
        help="Export a snapshot to dotenv, shell, or JSON format",
    )
    parser.add_argument(
        "snapshot_file",
        help="Path to the snapshot JSON file to export",
    )
    parser.add_argument(
        "-f", "--format",
        choices=SUPPORTED_FORMATS,
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    parser.set_defaults(func=cmd_export)
