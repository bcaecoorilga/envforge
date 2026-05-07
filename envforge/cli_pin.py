"""CLI subcommand for managing pinned environment variable values."""

import argparse
import sys

from envforge.pin import (
    PinError,
    pin_key,
    unpin_key,
    list_pins,
    check_pins,
    PIN_FILE_DEFAULT,
)
from envforge.snapshot import load


def cmd_pin(args: argparse.Namespace) -> None:
    pin_file = args.pin_file

    if args.pin_action == "add":
        try:
            pin_key(args.key, args.value, pin_file)
            print(f"Pinned {args.key!r} = {args.value!r}")
        except PinError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.pin_action == "remove":
        try:
            unpin_key(args.key, pin_file)
            print(f"Unpinned {args.key!r}")
        except PinError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

    elif args.pin_action == "list":
        pins = list_pins(pin_file)
        if not pins:
            print("No pinned keys.")
        else:
            for key, value in sorted(pins.items()):
                print(f"  {key}={value}")

    elif args.pin_action == "check":
        try:
            snapshot = load(args.snapshot)
        except Exception as exc:
            print(f"Error loading snapshot: {exc}", file=sys.stderr)
            sys.exit(1)
        try:
            violations = check_pins(snapshot, pin_file)
        except PinError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        if violations:
            print("Pin violations found:")
            for v in violations:
                print(f"  {v}")
            sys.exit(2)
        else:
            print("All pinned values match.")


def add_pin_subcommand(subparsers: argparse._SubParsersAction) -> None:
    pin_parser = subparsers.add_parser("pin", help="Manage pinned environment variable values")
    pin_parser.add_argument(
        "--pin-file",
        default=PIN_FILE_DEFAULT,
        help="Path to pin storage file (default: %(default)s)",
    )
    pin_sub = pin_parser.add_subparsers(dest="pin_action", required=True)

    add_p = pin_sub.add_parser("add", help="Pin a key to a specific value")
    add_p.add_argument("key", help="Environment variable name")
    add_p.add_argument("value", help="Value to pin")

    rm_p = pin_sub.add_parser("remove", help="Remove a pinned key")
    rm_p.add_argument("key", help="Environment variable name to unpin")

    pin_sub.add_parser("list", help="List all pinned keys")

    check_p = pin_sub.add_parser("check", help="Check a snapshot against pinned values")
    check_p.add_argument("snapshot", help="Path to snapshot JSON file")

    pin_parser.set_defaults(func=cmd_pin)
