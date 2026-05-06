"""CLI subcommand for merging environment snapshots."""

import json
import sys
from argparse import ArgumentParser, Namespace, _SubParsersAction

from envforge.merge import MergeError, list_conflicts, merge_snapshots
from envforge.snapshot import load, save


def cmd_merge(args: Namespace) -> None:
    """Handle the 'merge' subcommand."""
    snapshots = []
    for path in args.snapshots:
        try:
            snap = load(path)
            snapshots.append(snap)
        except (OSError, ValueError) as exc:
            print(f"[error] Could not load snapshot '{path}': {exc}", file=sys.stderr)
            sys.exit(1)

    if args.show_conflicts:
        try:
            conflicts = list_conflicts(snapshots)
        except MergeError as exc:
            print(f"[error] {exc}", file=sys.stderr)
            sys.exit(1)

        if not conflicts:
            print("No conflicts found.")
        else:
            print(f"Conflicts ({len(conflicts)} key(s)):")
            for key, sources in conflicts.items():
                print(f"  {key}:")
                for label, value in sources:
                    print(f"    [{label}] {value}")
        return

    exclude = args.exclude.split(",") if args.exclude else None

    try:
        merged = merge_snapshots(
            snapshots,
            label=args.label,
            strategy=args.strategy,
            exclude_keys=exclude,
        )
    except MergeError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        try:
            save(merged, args.output)
            print(f"Merged snapshot saved to '{args.output}'.")
        except OSError as exc:
            print(f"[error] Could not save snapshot: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(json.dumps(merged, indent=2))


def add_merge_subcommand(subparsers: _SubParsersAction) -> None:
    """Register the 'merge' subcommand on the given subparsers action."""
    parser: ArgumentParser = subparsers.add_parser(
        "merge",
        help="Merge multiple environment snapshots into one.",
    )
    parser.add_argument(
        "snapshots",
        nargs="+",
        metavar="SNAPSHOT",
        help="Paths to snapshot files to merge (in order).",
    )
    parser.add_argument(
        "--label",
        default="merged",
        help="Label for the resulting merged snapshot (default: 'merged').",
    )
    parser.add_argument(
        "--strategy",
        choices=["last_wins", "first_wins"],
        default="last_wins",
        help="Merge strategy when keys conflict (default: last_wins).",
    )
    parser.add_argument(
        "--exclude",
        metavar="KEYS",
        help="Comma-separated list of keys to exclude from the merged result.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write merged snapshot to FILE instead of stdout.",
    )
    parser.add_argument(
        "--show-conflicts",
        action="store_true",
        help="List conflicting keys across snapshots without merging.",
    )
    parser.set_defaults(func=cmd_merge)
