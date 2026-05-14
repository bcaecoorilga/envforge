"""CLI subcommand for snapshot dependency management."""

import argparse
import json
import sys

from envforge.snapshot_dependency import (
    DependencyError,
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    list_all,
)

DEFAULT_DEP_FILE = ".envforge_deps.json"


def cmd_dependency(args: argparse.Namespace) -> int:
    dep_file = getattr(args, "dep_file", DEFAULT_DEP_FILE)
    try:
        if args.dep_action == "add":
            add_dependency(args.label, args.depends_on, dep_file, reason=args.reason or "")
            print(f"Added dependency: {args.label} -> {args.depends_on}")

        elif args.dep_action == "remove":
            remove_dependency(args.label, args.depends_on, dep_file)
            print(f"Removed dependency: {args.label} -> {args.depends_on}")

        elif args.dep_action == "list":
            deps = get_dependencies(args.label, dep_file)
            if not deps:
                print(f"No dependencies for '{args.label}'")
            else:
                for entry in deps:
                    reason = f" ({entry['reason']}" + ")" if entry["reason"] else ""
                    print(f"  {args.label} -> {entry['depends_on']}{reason}")

        elif args.dep_action == "dependents":
            dependents = get_dependents(args.label, dep_file)
            if not dependents:
                print(f"No snapshots depend on '{args.label}'")
            else:
                for lbl in dependents:
                    print(f"  {lbl}")

        elif args.dep_action == "all":
            data = list_all(dep_file)
            print(json.dumps(data, indent=2))

    except DependencyError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


def add_dependency_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("dependency", help="Manage snapshot dependencies")
    p.add_argument("--dep-file", default=DEFAULT_DEP_FILE, help="Dependency store file")
    dep_sub = p.add_subparsers(dest="dep_action", required=True)

    add_p = dep_sub.add_parser("add", help="Add a dependency")
    add_p.add_argument("label", help="Snapshot label")
    add_p.add_argument("depends_on", help="Label this snapshot depends on")
    add_p.add_argument("--reason", default="", help="Optional reason")

    rem_p = dep_sub.add_parser("remove", help="Remove a dependency")
    rem_p.add_argument("label")
    rem_p.add_argument("depends_on")

    lst_p = dep_sub.add_parser("list", help="List dependencies for a label")
    lst_p.add_argument("label")

    dep_p = dep_sub.add_parser("dependents", help="List snapshots that depend on a label")
    dep_p.add_argument("label")

    dep_sub.add_parser("all", help="Show full dependency map")

    p.set_defaults(func=cmd_dependency)
