"""CLI subcommand for snapshot locking."""

from __future__ import annotations

import argparse
import sys

from envforge.snapshot_lock import (
    LockError,
    assert_not_locked,
    is_locked,
    list_locked,
    lock_snapshot,
    unlock_snapshot,
)

LOCK_FILE = ".envforge_locks.json"


def cmd_lock(args: argparse.Namespace) -> None:
    sub = args.lock_sub

    if sub == "add":
        try:
            lock_snapshot(args.label, reason=args.reason or "", lock_file=LOCK_FILE)
            print(f"Locked snapshot '{args.label}'.")
            if args.reason:
                print(f"Reason: {args.reason}")
        except LockError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif sub == "remove":
        try:
            unlock_snapshot(args.label, lock_file=LOCK_FILE)
            print(f"Unlocked snapshot '{args.label}'.")
        except LockError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif sub == "list":
        entries = list_locked(lock_file=LOCK_FILE)
        if not entries:
            print("No locked snapshots.")
        else:
            for entry in entries:
                reason_part = f"  # {entry['reason']}" if entry["reason"] else ""
                print(f"  {entry['label']}{reason_part}")

    elif sub == "check":
        locked = is_locked(args.label, lock_file=LOCK_FILE)
        if locked:
            from envforge.snapshot_lock import get_lock_reason
            reason = get_lock_reason(args.label, lock_file=LOCK_FILE)
            print(f"LOCKED: '{args.label}'", end="")
            print(f" — {reason}" if reason else "")
            sys.exit(1)
        else:
            print(f"NOT LOCKED: '{args.label}'")

    else:
        print(f"Unknown lock subcommand: {sub}", file=sys.stderr)
        sys.exit(1)


def add_lock_subcommand(subparsers: argparse._SubParsersAction) -> None:
    lock_parser = subparsers.add_parser("lock", help="Lock or unlock snapshots")
    lock_subs = lock_parser.add_subparsers(dest="lock_sub", required=True)

    add_p = lock_subs.add_parser("add", help="Lock a snapshot")
    add_p.add_argument("label", help="Snapshot label to lock")
    add_p.add_argument("--reason", default="", help="Reason for locking")

    rm_p = lock_subs.add_parser("remove", help="Unlock a snapshot")
    rm_p.add_argument("label", help="Snapshot label to unlock")

    lock_subs.add_parser("list", help="List all locked snapshots")

    chk_p = lock_subs.add_parser("check", help="Check if a snapshot is locked")
    chk_p.add_argument("label", help="Snapshot label to check")

    lock_parser.set_defaults(func=cmd_lock)
