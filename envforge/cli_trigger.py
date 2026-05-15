"""CLI sub-commands for snapshot triggers."""
from __future__ import annotations

import argparse
import json
import sys

from envforge.snapshot_trigger import (
    TriggerError,
    add_trigger,
    remove_trigger,
    get_triggers,
    list_all_triggers,
)


def cmd_trigger(args: argparse.Namespace) -> int:
    sub = args.trigger_subcommand
    tf = args.trigger_file

    try:
        if sub == "add":
            entry = add_trigger(
                args.label,
                args.event,
                args.action,
                condition=args.condition,
                trigger_file=tf,
            )
            print(f"Trigger added: [{args.label}] {entry['event']} -> {entry['action']}")
            if entry["condition"]:
                print(f"  condition: {entry['condition']}")

        elif sub == "remove":
            removed = remove_trigger(args.label, args.event, trigger_file=tf)
            print(f"Removed {removed} trigger(s) for '{args.label}' event '{args.event}'")

        elif sub == "list":
            if args.label:
                triggers = get_triggers(args.label, trigger_file=tf)
                if not triggers:
                    print(f"No triggers for '{args.label}'")
                else:
                    for t in triggers:
                        cond = f" [if: {t['condition']}]" if t["condition"] else ""
                        print(f"  {t['event']} -> {t['action']}{cond}")
            else:
                data = list_all_triggers(trigger_file=tf)
                if not data:
                    print("No triggers registered.")
                else:
                    for label, triggers in data.items():
                        for t in triggers:
                            cond = f" [if: {t['condition']}]" if t["condition"] else ""
                            print(f"  [{label}] {t['event']} -> {t['action']}{cond}")

        elif sub == "dump":
            data = list_all_triggers(trigger_file=tf)
            print(json.dumps(data, indent=2))

        else:
            print(f"Unknown trigger sub-command: {sub}", file=sys.stderr)
            return 1

    except TriggerError as exc:
        print(f"TriggerError: {exc}", file=sys.stderr)
        return 1

    return 0


def add_trigger_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("trigger", help="Manage snapshot triggers")
    p.add_argument("--trigger-file", default="triggers.json", metavar="FILE")
    tsub = p.add_subparsers(dest="trigger_subcommand", required=True)

    # add
    pa = tsub.add_parser("add", help="Register a new trigger")
    pa.add_argument("label")
    pa.add_argument("event", choices=["on_save", "on_restore", "on_diff", "on_promote", "on_expire"])
    pa.add_argument("action")
    pa.add_argument("--condition", default=None, metavar="EXPR")

    # remove
    pr = tsub.add_parser("remove", help="Remove triggers by label and event")
    pr.add_argument("label")
    pr.add_argument("event")

    # list
    pl = tsub.add_parser("list", help="List triggers")
    pl.add_argument("label", nargs="?", default=None)

    # dump
    tsub.add_parser("dump", help="Dump full trigger registry as JSON")

    p.set_defaults(func=cmd_trigger)
