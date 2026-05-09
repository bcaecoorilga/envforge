"""CLI subcommand: report — generate a structured diff report between two snapshot files."""

from __future__ import annotations

import argparse
import json
import sys

from envforge.snapshot import load
from envforge.snapshot_diff_report import ReportError, generate_report, format_report


def cmd_report(args: argparse.Namespace) -> int:
    """Entry point for the `report` subcommand."""
    try:
        snap_a = load(args.snapshot_a)
        snap_b = load(args.snapshot_b)
    except (OSError, ValueError) as exc:
        print(f"error: could not load snapshot — {exc}", file=sys.stderr)
        return 1

    try:
        report = generate_report(snap_a, snap_b)
    except ReportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        output = json.dumps(report, indent=2)
    else:
        output = format_report(
            report,
            show_unchanged=args.show_unchanged,
            mask_sensitive=not args.no_mask,
        )

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(output)
                fh.write("\n")
        except OSError as exc:
            print(f"error: could not write output — {exc}", file=sys.stderr)
            return 1
    else:
        print(output)

    return 0


def add_report_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser(
        "report",
        help="Generate a structured diff report between two snapshots",
    )
    parser.add_argument("snapshot_a", help="Path to the base snapshot file")
    parser.add_argument("snapshot_b", help="Path to the target snapshot file")
    parser.add_argument(
        "--show-unchanged",
        action="store_true",
        default=False,
        help="Include unchanged keys in the report output",
    )
    parser.add_argument(
        "--no-mask",
        action="store_true",
        default=False,
        help="Do not redact sensitive values in the output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output the report as JSON",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="FILE",
        default=None,
        help="Write report to FILE instead of stdout",
    )
    parser.set_defaults(func=cmd_report)
