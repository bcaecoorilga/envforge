"""CLI subcommands for snapshot tagging."""

import argparse
import sys

from envforge.tag import (
    TagError,
    add_tag,
    remove_tag,
    get_tags,
    find_by_tag,
    list_all_tags,
    TAG_FILE_DEFAULT,
)


def cmd_tag(args: argparse.Namespace) -> int:
    """Dispatch tag subcommands."""
    tag_file = getattr(args, "tag_file", TAG_FILE_DEFAULT)
    try:
        if args.tag_action == "add":
            add_tag(args.label, args.tag, tag_file)
            print(f"Tag '{args.tag}' added to snapshot '{args.label}'.")

        elif args.tag_action == "remove":
            remove_tag(args.label, args.tag, tag_file)
            print(f"Tag '{args.tag}' removed from snapshot '{args.label}'.")

        elif args.tag_action == "list":
            tags = get_tags(args.label, tag_file)
            if tags:
                print(f"Tags for '{args.label}': {', '.join(tags)}")
            else:
                print(f"No tags found for '{args.label}'.")

        elif args.tag_action == "find":
            labels = find_by_tag(args.tag, tag_file)
            if labels:
                print(f"Snapshots tagged '{args.tag}':")
                for label in labels:
                    print(f"  - {label}")
            else:
                print(f"No snapshots found with tag '{args.tag}'.")

        elif args.tag_action == "all":
            index = list_all_tags(tag_file)
            if not index:
                print("No tags recorded.")
            else:
                for label, tags in index.items():
                    print(f"  {label}: {', '.join(tags)}")

    except TagError as exc:
        print(f"Tag error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130

    return 0


def add_tag_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'tag' subcommand and its sub-actions."""
    tag_parser = subparsers.add_parser("tag", help="Manage snapshot tags")
    tag_parser.add_argument(
        "--tag-file", default=TAG_FILE_DEFAULT, help="Path to tag index file"
    )
    tag_sub = tag_parser.add_subparsers(dest="tag_action", required=True)

    # add
    p_add = tag_sub.add_parser("add", help="Add a tag to a snapshot")
    p_add.add_argument("label", help="Snapshot label")
    p_add.add_argument("tag", help="Tag to add")

    # remove
    p_remove = tag_sub.add_parser("remove", help="Remove a tag from a snapshot")
    p_remove.add_argument("label", help="Snapshot label")
    p_remove.add_argument("tag", help="Tag to remove")

    # list
    p_list = tag_sub.add_parser("list", help="List tags for a snapshot")
    p_list.add_argument("label", help="Snapshot label")

    # find
    p_find = tag_sub.add_parser("find", help="Find snapshots by tag")
    p_find.add_argument("tag", help="Tag to search for")

    # all
    tag_sub.add_parser("all", help="List all tags across all snapshots")

    tag_parser.set_defaults(func=cmd_tag)
