"""CLI subcommands for snapshot retention policy management."""

import argparse
import json
import sys

from envforge.snapshot_retention import (
    RetentionError,
    set_retention_policy,
    get_retention_policy,
    remove_retention_policy,
    list_retention_policies,
)

DEFAULT_RETENTION_FILE = ".envforge_retention.json"


def cmd_retention(args: argparse.Namespace) -> None:
    retention_file = getattr(args, "retention_file", DEFAULT_RETENTION_FILE)

    try:
        if args.retention_action == "set":
            entry = set_retention_policy(
                label=args.label,
                path=retention_file,
                policy=args.policy,
                max_count=args.max_count,
                max_age_days=args.max_age_days,
            )
            print(f"Retention policy set for '{entry['label']}' (policy={entry['policy']}).")

        elif args.retention_action == "get":
            entry = get_retention_policy(args.label, retention_file)
            if entry is None:
                print(f"No retention policy found for '{args.label}'.")
            else:
                print(json.dumps(entry, indent=2))

        elif args.retention_action == "remove":
            removed = remove_retention_policy(args.label, retention_file)
            if removed:
                print(f"Retention policy removed for '{args.label}'.")
            else:
                print(f"No retention policy found for '{args.label}'.")

        elif args.retention_action == "list":
            policies = list_retention_policies(retention_file)
            if not policies:
                print("No retention policies defined.")
            else:
                for p in policies:
                    age_info = (
                        f", max_age_days={p['max_age_days']}"
                        if p.get("max_age_days")
                        else ""
                    )
                    print(
                        f"{p['label']}: policy={p['policy']}, "
                        f"max_count={p['max_count']}{age_info}"
                    )
        else:
            print(f"Unknown retention action: {args.retention_action}", file=sys.stderr)
            sys.exit(1)

    except RetentionError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_retention_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("retention", help="Manage snapshot retention policies")
    parser.add_argument(
        "--retention-file",
        default=DEFAULT_RETENTION_FILE,
        dest="retention_file",
        help="Path to the retention policy store",
    )
    sub = parser.add_subparsers(dest="retention_action", required=True)

    # set
    p_set = sub.add_parser("set", help="Set a retention policy for a label")
    p_set.add_argument("label", help="Snapshot label")
    p_set.add_argument("--policy", default="count", choices=["count", "age", "both"])
    p_set.add_argument("--max-count", type=int, default=10, dest="max_count")
    p_set.add_argument("--max-age-days", type=int, default=None, dest="max_age_days")

    # get
    p_get = sub.add_parser("get", help="Get the retention policy for a label")
    p_get.add_argument("label", help="Snapshot label")

    # remove
    p_rm = sub.add_parser("remove", help="Remove the retention policy for a label")
    p_rm.add_argument("label", help="Snapshot label")

    # list
    sub.add_parser("list", help="List all retention policies")

    parser.set_defaults(func=cmd_retention)
