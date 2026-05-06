"""CLI subcommand for audit log inspection in envforge."""

import argparse
import sys

from envforge.audit import (
    AuditError,
    get_audit_log,
    filter_by_action,
    clear_audit_log,
    format_audit_log,
)

DEFAULT_AUDIT_FILE = ".envforge_audit.json"


def cmd_audit(args: argparse.Namespace) -> int:
    audit_file = getattr(args, "audit_file", DEFAULT_AUDIT_FILE)

    try:
        if args.audit_action == "list":
            if args.filter_action:
                entries = filter_by_action(audit_file, args.filter_action)
            else:
                entries = get_audit_log(audit_file)
            print(format_audit_log(entries))
            return 0

        if args.audit_action == "clear":
            count = clear_audit_log(audit_file)
            print(f"Cleared {count} audit entries.")
            return 0

    except AuditError as exc:
        print(f"Audit error: {exc}", file=sys.stderr)
        return 1

    print(f"Unknown audit subcommand: {args.audit_action}", file=sys.stderr)
    return 1


def add_audit_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "audit",
        help="View or manage the audit log",
    )
    parser.add_argument(
        "--audit-file",
        dest="audit_file",
        default=DEFAULT_AUDIT_FILE,
        help="Path to audit log file (default: .envforge_audit.json)",
    )

    audit_sub = parser.add_subparsers(dest="audit_action", required=True)

    list_parser = audit_sub.add_parser("list", help="List audit log entries")
    list_parser.add_argument(
        "--action",
        dest="filter_action",
        default=None,
        help="Filter entries by action name",
    )

    audit_sub.add_parser("clear", help="Clear all audit log entries")

    parser.set_defaults(func=cmd_audit)
