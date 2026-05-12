"""CLI subcommand for snapshot chaining."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from envforge.snapshot_chain import (
    ChainError,
    link_snapshot,
    get_parent,
    get_lineage,
    list_children,
)


def _load_snapshot(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def cmd_chain(args: argparse.Namespace) -> int:
    chain_file = args.chain_file

    try:
        if args.chain_action == "link":
            snapshot = _load_snapshot(args.snapshot)
            link_snapshot(snapshot, args.parent, chain_file)
            print(f"Linked '{snapshot['label']}' -> parent '{args.parent}'")

        elif args.chain_action == "parent":
            parent = get_parent(args.label, chain_file)
            if parent is None:
                print(f"'{args.label}' has no recorded parent (root)")
            else:
                print(parent)

        elif args.chain_action == "lineage":
            lineage = get_lineage(args.label, chain_file)
            for entry in lineage:
                print(entry)

        elif args.chain_action == "children":
            children = list_children(args.label, chain_file)
            if not children:
                print(f"No children found for '{args.label}'")
            else:
                for child in children:
                    print(child)

        else:
            print(f"Unknown chain action: {args.chain_action}", file=sys.stderr)
            return 1

    except ChainError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"File not found: {exc}", file=sys.stderr)
        return 1

    return 0


def add_chain_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("chain", help="Manage snapshot parent-child lineage")
    parser.add_argument(
        "--chain-file",
        default=".envforge_chain.json",
        help="Path to the chain index file",
    )

    chain_sub = parser.add_subparsers(dest="chain_action", required=True)

    p_link = chain_sub.add_parser("link", help="Link a snapshot to a parent")
    p_link.add_argument("snapshot", help="Path to the child snapshot JSON file")
    p_link.add_argument("parent", help="Label of the parent snapshot")

    p_parent = chain_sub.add_parser("parent", help="Show the parent of a snapshot")
    p_parent.add_argument("label", help="Snapshot label")

    p_lineage = chain_sub.add_parser("lineage", help="Show full ancestor chain")
    p_lineage.add_argument("label", help="Snapshot label")

    p_children = chain_sub.add_parser("children", help="List direct children of a snapshot")
    p_children.add_argument("label", help="Snapshot label")

    parser.set_defaults(func=cmd_chain)
