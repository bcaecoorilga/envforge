"""CLI subcommand for envforge watch — monitor environment variable changes."""

import argparse
import sys

from envforge.watch import WatchError, watch, format_watch_event


def cmd_watch(args: argparse.Namespace) -> None:
    """Entry point for the 'watch' subcommand."""
    label = getattr(args, "label", "watch-baseline")
    interval = getattr(args, "interval", 2.0)
    quiet = getattr(args, "quiet", False)

    if interval <= 0:
        print("Error: interval must be a positive number.", file=sys.stderr)
        sys.exit(1)

    def on_change(diff: dict) -> None:
        if not quiet:
            print(format_watch_event(diff), flush=True)
        else:
            added = len(diff.get("added", {}))
            removed = len(diff.get("removed", {}))
            changed = len(diff.get("changed", {}))
            print(
                f"[envforge:watch] +{added} -{removed} ~{changed}",
                flush=True,
            )

    print(
        f"[envforge:watch] Watching environment (interval={interval}s, label='{label}'). "
        "Press Ctrl+C to stop.",
        flush=True,
    )

    try:
        watch(
            interval=interval,
            label=label,
            on_change=on_change,
        )
    except WatchError as exc:
        print(f"Watch error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[envforge:watch] Stopped.", flush=True)


def add_watch_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'watch' subcommand with the given subparsers."""
    parser = subparsers.add_parser(
        "watch",
        help="Monitor environment variables for changes in real time.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 2.0).",
    )
    parser.add_argument(
        "--label",
        default="watch-baseline",
        help="Label for the baseline snapshot (default: watch-baseline).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print a compact summary instead of the full diff.",
    )
    parser.set_defaults(func=cmd_watch)
