"""CLI subcommand for snapshot rating."""

import argparse
import sys
from envforge.snapshot_rating import (
    RatingError,
    rate_snapshot,
    get_rating,
    remove_rating,
    list_ratings,
    top_rated,
)


def _format_entry(label: str, rating: int, comment: str) -> str:
    """Format a rating entry for display."""
    suffix = f" ({comment})" if comment else ""
    return f"{label}: {rating}/5{suffix}"


def cmd_rating(args: argparse.Namespace) -> None:
    """Dispatch rating subcommands based on parsed arguments."""
    try:
        if args.rating_action == "set":
            entry = rate_snapshot(
                args.label,
                args.score,
                comment=args.comment or "",
                rating_file=args.rating_file,
            )
            print(f"Rated '{args.label}': "
                  + _format_entry(args.label, entry['rating'], entry['comment']).split(": ", 1)[1])

        elif args.rating_action == "get":
            entry = get_rating(args.label, rating_file=args.rating_file)
            if entry is None:
                print(f"No rating found for '{args.label}'.")
            else:
                print(_format_entry(args.label, entry['rating'], entry.get('comment', '')))

        elif args.rating_action == "remove":
            removed = remove_rating(args.label, rating_file=args.rating_file)
            if removed:
                print(f"Removed rating for '{args.label}'.")
            else:
                print(f"No rating found for '{args.label}'.")

        elif args.rating_action == "list":
            entries = list_ratings(rating_file=args.rating_file)
            if not entries:
                print("No ratings recorded.")
            else:
                for e in entries:
                    print(_format_entry(e['label'], e['rating'], e.get('comment', '')))

        elif args.rating_action == "top":
            entries = top_rated(n=args.n, rating_file=args.rating_file)
            for e in entries:
                print(_format_entry(e['label'], e['rating'], e.get('comment', '')))

    except RatingError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_rating_subcommand(subparsers) -> None:
    """Register the 'rating' subcommand and its sub-actions with the given subparsers."""
    parser = subparsers.add_parser("rating", help="Rate snapshots")
    parser.add_argument("--rating-file", default="ratings.json")
    sub = parser.add_subparsers(dest="rating_action", required=True)

    p_set = sub.add_parser("set", help="Assign a rating")
    p_set.add_argument("label")
    p_set.add_argument("score", type=int, choices=[1, 2, 3, 4, 5])
    p_set.add_argument("--comment", default="")

    p_get = sub.add_parser("get", help="Retrieve a rating")
    p_get.add_argument("label")

    p_rm = sub.add_parser("remove", help="Remove a rating")
    p_rm.add_argument("label")

    sub.add_parser("list", help="List all ratings")

    p_top = sub.add_parser("top", help="Show top-rated snapshots")
    p_top.add_argument("--n", type=int, default=5)

    parser.set_defaults(func=cmd_rating)
