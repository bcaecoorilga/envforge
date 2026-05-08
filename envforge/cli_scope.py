"""CLI subcommand for scope management."""

import argparse
import sys

from envforge.scope import (
    ScopeError,
    assign_scope,
    remove_scope,
    get_scope,
    list_by_scope,
    all_scopes,
)

DEFAULT_SCOPE_FILE = ".envforge_scopes.json"


def cmd_scope(args: argparse.Namespace) -> None:
    scope_file = getattr(args, "scope_file", DEFAULT_SCOPE_FILE)
    try:
        if args.scope_action == "assign":
            result = assign_scope(args.label, args.scope, scope_file)
            print(f"Assigned scope '{result['scope']}' to '{result['label']}'.")

        elif args.scope_action == "remove":
            remove_scope(args.label, scope_file)
            print(f"Removed scope from '{args.label}'.")

        elif args.scope_action == "get":
            scope = get_scope(args.label, scope_file)
            if scope is None:
                print(f"No scope assigned to '{args.label}'.")
            else:
                print(f"{args.label}: {scope}")

        elif args.scope_action == "list":
            labels = list_by_scope(args.scope, scope_file)
            if not labels:
                print(f"No snapshots assigned to scope '{args.scope}'.")
            else:
                for label in labels:
                    print(label)

        elif args.scope_action == "all":
            mapping = all_scopes(scope_file)
            if not mapping:
                print("No scopes defined.")
            else:
                for label, scope in sorted(mapping.items()):
                    print(f"{label}: {scope}")

    except ScopeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_scope_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("scope", help="Manage snapshot scopes")
    parser.add_argument(
        "--scope-file", default=DEFAULT_SCOPE_FILE, help="Path to scope store file"
    )
    scope_sub = parser.add_subparsers(dest="scope_action", required=True)

    p_assign = scope_sub.add_parser("assign", help="Assign a scope to a label")
    p_assign.add_argument("label", help="Snapshot label")
    p_assign.add_argument("scope", help="Scope name (e.g. dev, staging, prod)")

    p_remove = scope_sub.add_parser("remove", help="Remove scope from a label")
    p_remove.add_argument("label", help="Snapshot label")

    p_get = scope_sub.add_parser("get", help="Get scope for a label")
    p_get.add_argument("label", help="Snapshot label")

    p_list = scope_sub.add_parser("list", help="List labels assigned to a scope")
    p_list.add_argument("scope", help="Scope name to filter by")

    scope_sub.add_parser("all", help="Show all label-to-scope assignments")

    parser.set_defaults(func=cmd_scope)
