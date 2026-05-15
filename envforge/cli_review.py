"""CLI subcommand for snapshot review management."""

import argparse
import sys

from envforge.snapshot_review import (
    ReviewError,
    request_review,
    resolve_review,
    get_review,
    list_reviews,
)

DEFAULT_REVIEW_FILE = ".envforge_reviews.json"


def cmd_review(args: argparse.Namespace) -> None:
    review_file = getattr(args, "review_file", DEFAULT_REVIEW_FILE)
    try:
        if args.review_action == "request":
            entry = request_review(
                args.label,
                args.reviewer,
                review_file,
                note=args.note or "",
            )
            print(f"Review requested for '{args.label}' by {args.reviewer}.")
            print(f"  State: {entry['state']}")
            print(f"  Requested at: {entry['requested_at']}")

        elif args.review_action == "approve":
            entry = resolve_review(
                args.label, "approved", review_file, comment=args.comment or ""
            )
            print(f"Review for '{args.label}' approved.")

        elif args.review_action == "reject":
            entry = resolve_review(
                args.label, "rejected", review_file, comment=args.comment or ""
            )
            print(f"Review for '{args.label}' rejected.")

        elif args.review_action == "show":
            entry = get_review(args.label, review_file)
            if entry is None:
                print(f"No review found for '{args.label}'.")
                sys.exit(1)
            print(f"Label:       {args.label}")
            print(f"State:       {entry['state']}")
            print(f"Reviewer:    {entry['reviewer']}")
            print(f"Note:        {entry.get('note', '')}")
            print(f"Requested:   {entry['requested_at']}")
            print(f"Resolved:    {entry.get('resolved_at') or '-'}")

        elif args.review_action == "list":
            state_filter = getattr(args, "state", None)
            entries = list_reviews(review_file, state=state_filter)
            if not entries:
                print("No reviews found.")
                return
            for e in entries:
                resolved = e.get("resolved_at") or "-"
                print(f"  [{e['state']:8}] {e['label']}  reviewer={e['reviewer']}  resolved={resolved}")

    except ReviewError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def add_review_subcommand(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("review", help="Manage snapshot reviews")
    parser.add_argument("--review-file", default=DEFAULT_REVIEW_FILE)
    sub = parser.add_subparsers(dest="review_action", required=True)

    p_req = sub.add_parser("request", help="Request a review for a snapshot")
    p_req.add_argument("label")
    p_req.add_argument("reviewer")
    p_req.add_argument("--note", default="")

    p_app = sub.add_parser("approve", help="Approve a pending review")
    p_app.add_argument("label")
    p_app.add_argument("--comment", default="")

    p_rej = sub.add_parser("reject", help="Reject a pending review")
    p_rej.add_argument("label")
    p_rej.add_argument("--comment", default="")

    p_show = sub.add_parser("show", help="Show review status for a snapshot")
    p_show.add_argument("label")

    p_list = sub.add_parser("list", help="List all reviews")
    p_list.add_argument("--state", choices=["pending", "approved", "rejected"], default=None)

    parser.set_defaults(func=cmd_review)
