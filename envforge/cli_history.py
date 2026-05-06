"""CLI subcommand for snapshot history management."""

import argparse
import json
from envforge.history import (
    HistoryError,
    get_history,
    find_by_label,
    latest_entry,
    clear_history,
    HISTORY_FILE,
)


def cmd_history(args: argparse.Namespace) -> None:
    history_path = getattr(args, "history_file", HISTORY_FILE)

    try:
        if args.history_action == "list":
            records = get_history(history_path)
            if not records:
                print("No history recorded.")
                return
            for i, entry in enumerate(records, 1):
                print(
                    f"{i:>3}. [{entry['recorded_at']}] "
                    f"{entry['label']} "
                    f"(checksum: {entry['checksum'][:8]}…, "
                    f"vars: {entry['variable_count']})"
                )

        elif args.history_action == "find":
            results = find_by_label(args.label, history_path)
            if not results:
                print(f"No entries found for label: {args.label}")
                return
            print(json.dumps(results, indent=2))

        elif args.history_action == "latest":
            entry = latest_entry(history_path)
            if entry is None:
                print("History is empty.")
            else:
                print(json.dumps(entry, indent=2))

        elif args.history_action == "clear":
            removed = clear_history(history_path)
            print(f"Cleared {removed} history record(s).")

        else:
            print(f"Unknown history action: {args.history_action}")

    except HistoryError as exc:
        print(f"History error: {exc}")
        raise SystemExit(1)


def add_history_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "history", help="View and manage snapshot history"
    )
    parser.add_argument(
        "--history-file",
        default=HISTORY_FILE,
        help="Path to the history file (default: %(default)s)",
    )
    action_sub = parser.add_subparsers(dest="history_action", required=True)

    action_sub.add_parser("list", help="List all recorded snapshots")

    find_p = action_sub.add_parser("find", help="Find entries by label")
    find_p.add_argument("label", help="Snapshot label to search for")

    action_sub.add_parser("latest", help="Show the most recent history entry")
    action_sub.add_parser("clear", help="Remove all history records")

    parser.set_defaults(func=cmd_history)
