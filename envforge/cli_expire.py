"""CLI subcommand for managing snapshot expiry dates."""

import argparse
import sys
from datetime import datetime, timezone

from envforge.snapshot_expire import (
    ExpireError,
    set_expiry,
    get_expiry,
    clear_expiry,
    is_expired,
    list_expiry,
    EXPIRY_DATE_FORMAT,
)

DEFAULT_EXPIRY_FILE = "envforge_expiry.json"


def cmd_expire(args: argparse.Namespace) -> None:
    expiry_file = getattr(args, "expiry_file", DEFAULT_EXPIRY_FILE)
    try:
        if args.expire_action == "set":
            try:
                dt = datetime.strptime(args.date, EXPIRY_DATE_FORMAT).replace(
                    tzinfo=timezone.utc
                )
            except ValueError:
                print(
                    f"Error: date must be in format {EXPIRY_DATE_FORMAT}",
                    file=sys.stderr,
                )
                sys.exit(1)
            result = set_expiry(args.label, dt, expiry_file)
            print(f"Set expiry for '{result['label']}': {result['expires_at']}")

        elif args.expire_action == "get":
            expiry = get_expiry(args.label, expiry_file)
            if expiry is None:
                print(f"No expiry set for '{args.label}'.")
            else:
                status = "EXPIRED" if is_expired(args.label, expiry_file) else "active"
                print(f"{args.label}: {expiry.strftime(EXPIRY_DATE_FORMAT)} [{status}]")

        elif args.expire_action == "clear":
            removed = clear_expiry(args.label, expiry_file)
            if removed:
                print(f"Cleared expiry for '{args.label}'.")
            else:
                print(f"No expiry found for '{args.label}'.")

        elif args.expire_action == "list":
            entries = list_expiry(expiry_file)
            if not entries:
                print("No expiry dates recorded.")
            else:
                for entry in entries:
                    expired = is_expired(entry["label"], expiry_file)
                    flag = " [EXPIRED]" if expired else ""
                    print(f"  {entry['label']}: {entry['expires_at']}{flag}")

    except ExpireError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_expire_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("expire", help="Manage snapshot expiry dates")
    parser.add_argument(
        "--expiry-file", dest="expiry_file", default=DEFAULT_EXPIRY_FILE
    )
    sub = parser.add_subparsers(dest="expire_action", required=True)

    p_set = sub.add_parser("set", help="Set an expiry date for a snapshot")
    p_set.add_argument("label", help="Snapshot label")
    p_set.add_argument("date", help=f"Expiry date ({EXPIRY_DATE_FORMAT})")

    p_get = sub.add_parser("get", help="Get expiry date for a snapshot")
    p_get.add_argument("label", help="Snapshot label")

    p_clear = sub.add_parser("clear", help="Clear expiry date for a snapshot")
    p_clear.add_argument("label", help="Snapshot label")

    sub.add_parser("list", help="List all expiry dates")

    parser.set_defaults(func=cmd_expire)
