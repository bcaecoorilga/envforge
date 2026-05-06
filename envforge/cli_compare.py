"""CLI subcommand for comparing multiple environment snapshots."""

import argparse
import sys

from envforge.snapshot import load
from envforge.compare import compare_all, format_matrix, CompareError
from envforge.diff import format_diff


def cmd_compare(args: argparse.Namespace) -> None:
    """Load two or more snapshot files and print a comparison report."""
    if len(args.files) < 2:
        print("error: at least two snapshot files are required", file=sys.stderr)
        sys.exit(1)

    snapshots = []
    for path in args.files:
        try:
            snap = load(path)
        except Exception as exc:
            print(f"error: could not load '{path}': {exc}", file=sys.stderr)
            sys.exit(1)
        snapshots.append(snap)

    try:
        report = compare_all(snapshots)
    except CompareError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.matrix:
        print(format_matrix(report))
        return

    for pair in report["pairs"]:
        print(f"\n=== {pair['from']} → {pair['to']} ===")
        print(f"Summary: {pair['summary']}")
        if args.verbose:
            print(format_diff(pair["diff"]))


def add_compare_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'compare' subcommand on the given subparsers object."""
    parser = subparsers.add_parser(
        "compare",
        help="Compare two or more snapshot files",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Snapshot files to compare (minimum 2)",
    )
    parser.add_argument(
        "--matrix",
        action="store_true",
        default=False,
        help="Display a full key/value matrix across all snapshots",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Show full diff output for each pair",
    )
    parser.set_defaults(func=cmd_compare)
