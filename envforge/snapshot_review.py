"""Snapshot review: request, approve, and reject snapshot reviews."""

import json
import time
from pathlib import Path
from typing import Optional

REVIEW_STATES = ("pending", "approved", "rejected")


class ReviewError(Exception):
    pass


def _load_reviews(review_file: str) -> dict:
    path = Path(review_file)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _save_reviews(review_file: str, data: dict) -> None:
    with open(review_file, "w") as f:
        json.dump(data, f, indent=2)


def request_review(label: str, reviewer: str, review_file: str, note: str = "") -> dict:
    """Open a review request for a snapshot label."""
    if not label:
        raise ReviewError("label must not be empty")
    if not reviewer:
        raise ReviewError("reviewer must not be empty")
    reviews = _load_reviews(review_file)
    entry = {
        "state": "pending",
        "reviewer": reviewer,
        "note": note,
        "requested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "resolved_at": None,
    }
    reviews[label] = entry
    _save_reviews(review_file, reviews)
    return entry


def resolve_review(label: str, state: str, review_file: str, comment: str = "") -> dict:
    """Approve or reject an existing review request."""
    if state not in ("approved", "rejected"):
        raise ReviewError(f"state must be 'approved' or 'rejected', got '{state}'")
    reviews = _load_reviews(review_file)
    if label not in reviews:
        raise ReviewError(f"no review found for label '{label}'")
    entry = reviews[label]
    if entry["state"] != "pending":
        raise ReviewError(f"review for '{label}' is already {entry['state']}")
    entry["state"] = state
    entry["comment"] = comment
    entry["resolved_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    reviews[label] = entry
    _save_reviews(review_file, reviews)
    return entry


def get_review(label: str, review_file: str) -> Optional[dict]:
    """Return the review entry for a label, or None if not found."""
    reviews = _load_reviews(review_file)
    return reviews.get(label)


def list_reviews(review_file: str, state: Optional[str] = None) -> list:
    """Return all review entries, optionally filtered by state."""
    reviews = _load_reviews(review_file)
    entries = [{"label": k, **v} for k, v in reviews.items()]
    if state:
        entries = [e for e in entries if e["state"] == state]
    return entries
