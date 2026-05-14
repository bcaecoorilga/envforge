"""Snapshot rating: assign quality/confidence ratings to snapshots."""

import json
from pathlib import Path
from typing import Dict, List, Optional

VALID_RATINGS = {1, 2, 3, 4, 5}


class RatingError(Exception):
    """Raised when a rating operation fails."""


def _load_ratings(rating_file: str) -> Dict:
    path = Path(rating_file)
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_ratings(ratings: Dict, rating_file: str) -> None:
    Path(rating_file).write_text(json.dumps(ratings, indent=2))


def rate_snapshot(label: str, rating: int, comment: str = "",
                  rating_file: str = "ratings.json") -> Dict:
    """Assign a numeric rating (1-5) to a snapshot."""
    if not label:
        raise RatingError("Label must not be empty.")
    if rating not in VALID_RATINGS:
        raise RatingError(f"Rating must be one of {sorted(VALID_RATINGS)}, got {rating}.")
    ratings = _load_ratings(rating_file)
    ratings[label] = {"rating": rating, "comment": comment}
    _save_ratings(ratings, rating_file)
    return ratings[label]


def get_rating(label: str, rating_file: str = "ratings.json") -> Optional[Dict]:
    """Return the rating entry for a snapshot label, or None if not rated."""
    if not label:
        raise RatingError("Label must not be empty.")
    return _load_ratings(rating_file).get(label)


def remove_rating(label: str, rating_file: str = "ratings.json") -> bool:
    """Remove the rating for a snapshot. Returns True if removed, False if not found."""
    if not label:
        raise RatingError("Label must not be empty.")
    ratings = _load_ratings(rating_file)
    if label not in ratings:
        return False
    del ratings[label]
    _save_ratings(ratings, rating_file)
    return True


def list_ratings(rating_file: str = "ratings.json") -> List[Dict]:
    """Return all ratings as a sorted list of dicts with label included."""
    ratings = _load_ratings(rating_file)
    return [
        {"label": label, **entry}
        for label, entry in sorted(ratings.items())
    ]


def top_rated(n: int = 5, rating_file: str = "ratings.json") -> List[Dict]:
    """Return the top-n highest-rated snapshots."""
    all_ratings = list_ratings(rating_file)
    return sorted(all_ratings, key=lambda x: x["rating"], reverse=True)[:n]
