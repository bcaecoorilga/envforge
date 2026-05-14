"""Tests for envforge.snapshot_rating."""

import json
import pytest
from envforge.snapshot_rating import (
    RatingError,
    rate_snapshot,
    get_rating,
    remove_rating,
    list_ratings,
    top_rated,
)


@pytest.fixture
def rating_file(tmp_path):
    return str(tmp_path / "ratings.json")


def test_rate_snapshot_creates_entry(rating_file):
    result = rate_snapshot("prod-v1", 4, rating_file=rating_file)
    assert result["rating"] == 4


def test_rate_snapshot_persists_to_file(rating_file):
    rate_snapshot("prod-v1", 3, rating_file=rating_file)
    data = json.loads(open(rating_file).read())
    assert "prod-v1" in data
    assert data["prod-v1"]["rating"] == 3


def test_rate_snapshot_stores_comment(rating_file):
    rate_snapshot("staging", 5, comment="looks great", rating_file=rating_file)
    entry = get_rating("staging", rating_file=rating_file)
    assert entry["comment"] == "looks great"


def test_rate_snapshot_overwrites_existing(rating_file):
    rate_snapshot("prod-v1", 2, rating_file=rating_file)
    rate_snapshot("prod-v1", 5, rating_file=rating_file)
    entry = get_rating("prod-v1", rating_file=rating_file)
    assert entry["rating"] == 5


def test_rate_snapshot_raises_on_empty_label(rating_file):
    with pytest.raises(RatingError):
        rate_snapshot("", 3, rating_file=rating_file)


def test_rate_snapshot_raises_on_invalid_rating(rating_file):
    with pytest.raises(RatingError):
        rate_snapshot("prod", 6, rating_file=rating_file)


def test_rate_snapshot_raises_on_zero_rating(rating_file):
    with pytest.raises(RatingError):
        rate_snapshot("prod", 0, rating_file=rating_file)


def test_get_rating_returns_none_when_missing(rating_file):
    assert get_rating("unknown", rating_file=rating_file) is None


def test_get_rating_raises_on_empty_label(rating_file):
    with pytest.raises(RatingError):
        get_rating("", rating_file=rating_file)


def test_remove_rating_returns_true_when_found(rating_file):
    rate_snapshot("dev", 2, rating_file=rating_file)
    assert remove_rating("dev", rating_file=rating_file) is True


def test_remove_rating_returns_false_when_not_found(rating_file):
    assert remove_rating("ghost", rating_file=rating_file) is False


def test_remove_rating_deletes_entry(rating_file):
    rate_snapshot("dev", 2, rating_file=rating_file)
    remove_rating("dev", rating_file=rating_file)
    assert get_rating("dev", rating_file=rating_file) is None


def test_list_ratings_returns_all(rating_file):
    rate_snapshot("a", 1, rating_file=rating_file)
    rate_snapshot("b", 3, rating_file=rating_file)
    results = list_ratings(rating_file=rating_file)
    labels = [r["label"] for r in results]
    assert "a" in labels and "b" in labels


def test_list_ratings_empty_when_no_file(rating_file):
    assert list_ratings(rating_file=rating_file) == []


def test_top_rated_returns_highest(rating_file):
    rate_snapshot("low", 1, rating_file=rating_file)
    rate_snapshot("mid", 3, rating_file=rating_file)
    rate_snapshot("high", 5, rating_file=rating_file)
    top = top_rated(n=1, rating_file=rating_file)
    assert top[0]["label"] == "high"


def test_top_rated_respects_n(rating_file):
    for i, label in enumerate(["a", "b", "c", "d"], start=1):
        rate_snapshot(label, i, rating_file=rating_file)
    assert len(top_rated(n=2, rating_file=rating_file)) == 2
