"""Tests for envforge.snapshot_review."""

import json
import pytest
from envforge.snapshot_review import (
    ReviewError,
    request_review,
    resolve_review,
    get_review,
    list_reviews,
)


@pytest.fixture
def review_file(tmp_path):
    return str(tmp_path / "reviews.json")


def test_request_review_creates_entry(review_file):
    entry = request_review("prod-v1", "alice", review_file)
    assert entry["state"] == "pending"
    assert entry["reviewer"] == "alice"


def test_request_review_persists_to_file(review_file):
    request_review("prod-v1", "alice", review_file)
    with open(review_file) as f:
        data = json.load(f)
    assert "prod-v1" in data


def test_request_review_stores_note(review_file):
    entry = request_review("prod-v1", "alice", review_file, note="please check secrets")
    assert entry["note"] == "please check secrets"


def test_request_review_raises_on_empty_label(review_file):
    with pytest.raises(ReviewError, match="label"):
        request_review("", "alice", review_file)


def test_request_review_raises_on_empty_reviewer(review_file):
    with pytest.raises(ReviewError, match="reviewer"):
        request_review("prod-v1", "", review_file)


def test_request_review_has_timestamp(review_file):
    entry = request_review("prod-v1", "alice", review_file)
    assert entry["requested_at"] is not None
    assert "T" in entry["requested_at"]


def test_resolve_review_approves(review_file):
    request_review("prod-v1", "alice", review_file)
    entry = resolve_review("prod-v1", "approved", review_file, comment="LGTM")
    assert entry["state"] == "approved"
    assert entry["comment"] == "LGTM"


def test_resolve_review_rejects(review_file):
    request_review("prod-v1", "alice", review_file)
    entry = resolve_review("prod-v1", "rejected", review_file, comment="needs changes")
    assert entry["state"] == "rejected"


def test_resolve_review_sets_resolved_at(review_file):
    request_review("prod-v1", "alice", review_file)
    entry = resolve_review("prod-v1", "approved", review_file)
    assert entry["resolved_at"] is not None


def test_resolve_review_raises_on_invalid_state(review_file):
    request_review("prod-v1", "alice", review_file)
    with pytest.raises(ReviewError, match="state"):
        resolve_review("prod-v1", "pending", review_file)


def test_resolve_review_raises_on_missing_label(review_file):
    with pytest.raises(ReviewError, match="no review found"):
        resolve_review("nonexistent", "approved", review_file)


def test_resolve_review_raises_when_already_resolved(review_file):
    request_review("prod-v1", "alice", review_file)
    resolve_review("prod-v1", "approved", review_file)
    with pytest.raises(ReviewError, match="already"):
        resolve_review("prod-v1", "rejected", review_file)


def test_get_review_returns_entry(review_file):
    request_review("prod-v1", "alice", review_file)
    entry = get_review("prod-v1", review_file)
    assert entry is not None
    assert entry["reviewer"] == "alice"


def test_get_review_returns_none_for_missing(review_file):
    assert get_review("missing", review_file) is None


def test_list_reviews_returns_all(review_file):
    request_review("prod-v1", "alice", review_file)
    request_review("staging-v2", "bob", review_file)
    entries = list_reviews(review_file)
    assert len(entries) == 2


def test_list_reviews_filters_by_state(review_file):
    request_review("prod-v1", "alice", review_file)
    request_review("staging-v2", "bob", review_file)
    resolve_review("prod-v1", "approved", review_file)
    pending = list_reviews(review_file, state="pending")
    assert len(pending) == 1
    assert pending[0]["label"] == "staging-v2"


def test_list_reviews_includes_label_field(review_file):
    request_review("prod-v1", "alice", review_file)
    entries = list_reviews(review_file)
    assert entries[0]["label"] == "prod-v1"
