"""Command-line interface for envforge."""

import argparse
import json
import os
import sys

from envforge.snapshot import capture, save, load
from envforge.diff import diff_snapshots, format_diff, has_differences
from envforge.restore import restore_from_file, rollback_to_snapshot, RestoreError


def cmd_capture(args):
    """Capture the current environment and save to a file."""
    snap = capture(label=args.label)
    save(snap, args.output)
    print(f"Snapshot '{args.label}' saved to {args.output}")
    print(f"  Variables captured: {len(snap['variables'])}")
    print(f"  Checksum: {snap['checksum']}")


def cmd_diff(args):
    """Show differences between two snapshot files."""
    snap_a = load(args.snapshot_a)
    snap_b = load(args.snapshot_b)
    diff = diff_snapshots(snap_a, snap_b)
    if not has_differences(diff):
        print("No differences found.")
        return
    print(format_diff(diff))


def cmd_restore(args):
    """Restore environment variables from a snapshot file."""
    try:
        result = restore_from_file(args.snapshot, overwrite=not args.no_overwrite)
    except RestoreError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Restored snapshot '{result['label']}' from {args.snapshot}")
    print(f"  Set:     {len(result['set'])} variable(s)")
    print(f"  Skipped: {len(result['skipped'])} variable(s)")


def cmd_rollback(args):
    """Rollback environment to exactly match a snapshot (removes extra keys)."""
    snap = load(args.snapshot)
    result = rollback_to_snapshot(snap)
    print(f"Rollback to snapshot '{snap.get('label', '')}'")
    print(f"  Set:     {len(result['set'])} variable(s)")
    print(f"  Cleared: {len(result['cleared'])} variable(s)")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="envforge",
        description="Snapshot, diff, and restore environment variable sets.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # capture
    p_capture = sub.add_parser("capture", help="Capture current environment.")
    p_capture.add_argument("--label", default="snapshot", help="Label for the snapshot.")
    p_capture.add_argument("--output", required=True, help="Output JSON file path.")
    p_capture.set_defaults(func=cmd_capture)

    # diff
    p_diff = sub.add_parser("diff", help="Diff two snapshot files.")
    p_diff.add_argument("snapshot_a", help="First snapshot file.")
    p_diff.add_argument("snapshot_b", help="Second snapshot file.")
    p_diff.set_defaults(func=cmd_diff)

    # restore
    p_restore = sub.add_parser("restore", help="Restore variables from a snapshot.")
    p_restore.add_argument("snapshot", help="Snapshot file to restore.")
    p_restore.add_argument("--no-overwrite", action="store_true",
                           help="Skip variables already set in the environment.")
    p_restore.set_defaults(func=cmd_restore)

    # rollback
    p_rollback = sub.add_parser("rollback", help="Rollback env to exactly match a snapshot.")
    p_rollback.add_argument("snapshot", help="Snapshot file to rollback to.")
    p_rollback.set_defaults(func=cmd_rollback)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
