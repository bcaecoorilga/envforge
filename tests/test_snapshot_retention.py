"""Tests for envforge.snapshot_retention."""

import json
import os
import pytest
from datetime import datetime, timedelta

from envforge.snapshot_retention import (
    RetentionError,
    set_retention_policy,
    get_retention_policy,
    remove_retention_policy,
    list_retention_policies,
    evaluate_retention,
)


@pytest.fixture
def retention_file(tmp_path):
    return str(tmp_path / "retention.json")


# --- set_retention_policy ---

def test_set_retention_creates_entry(retention_file):
    entry = set_retention_policy("prod", retention_file)
    assert entry["label"] == "prod"


def test_set_retention_persists_to_file(retention_file):
    set_retention_policy("prod", retention_file, max_count=5)
    with open(retention_file) as fh:
        data = json.load(fh)
    assert "prod" in data
    assert data["prod"]["max_count"] == 5


def test_set_retention_default_policy_is_count(retention_file):
    entry = set_retention_policy("staging", retention_file)
    assert entry["policy"] == "count"


def test_set_retention_age_policy_requires_max_age_days(retention_file):
    with pytest.raises(RetentionError, match="max_age_days"):
        set_retention_policy("prod", retention_file, policy="age")


def test_set_retention_both_policy_requires_max_age_days(retention_file):
    with pytest.raises(RetentionError, match="max_age_days"):
        set_retention_policy("prod", retention_file, policy="both")


def test_set_retention_age_policy_stores_max_age_days(retention_file):
    entry = set_retention_policy("prod", retention_file, policy="age", max_age_days=30)
    assert entry["max_age_days"] == 30


def test_set_retention_raises_on_empty_label(retention_file):
    with pytest.raises(RetentionError, match="label"):
        set_retention_policy("", retention_file)


def test_set_retention_raises_on_invalid_policy(retention_file):
    with pytest.raises(RetentionError, match="unknown policy"):
        set_retention_policy("prod", retention_file, policy="forever")


def test_set_retention_raises_on_zero_max_count(retention_file):
    with pytest.raises(RetentionError, match="max_count"):
        set_retention_policy("prod", retention_file, max_count=0)


def test_set_retention_created_at_is_set(retention_file):
    entry = set_retention_policy("prod", retention_file)
    assert "created_at" in entry


# --- get_retention_policy ---

def test_get_retention_returns_entry(retention_file):
    set_retention_policy("prod", retention_file, max_count=7)
    result = get_retention_policy("prod", retention_file)
    assert result["max_count"] == 7


def test_get_retention_returns_none_for_missing(retention_file):
    assert get_retention_policy("nonexistent", retention_file) is None


def test_get_retention_raises_on_empty_label(retention_file):
    with pytest.raises(RetentionError):
        get_retention_policy("", retention_file)


# --- remove_retention_policy ---

def test_remove_retention_deletes_entry(retention_file):
    set_retention_policy("prod", retention_file)
    removed = remove_retention_policy("prod", retention_file)
    assert removed is True
    assert get_retention_policy("prod", retention_file) is None


def test_remove_retention_returns_false_for_missing(retention_file):
    assert remove_retention_policy("ghost", retention_file) is False


def test_remove_retention_raises_on_empty_label(retention_file):
    with pytest.raises(RetentionError):
        remove_retention_policy("", retention_file)


# --- list_retention_policies ---

def test_list_retention_returns_all(retention_file):
    set_retention_policy("prod", retention_file)
    set_retention_policy("staging", retention_file)
    policies = list_retention_policies(retention_file)
    labels = [p["label"] for p in policies]
    assert "prod" in labels
    assert "staging" in labels


def test_list_retention_sorted_by_label(retention_file):
    set_retention_policy("staging", retention_file)
    set_retention_policy("dev", retention_file)
    set_retention_policy("prod", retention_file)
    labels = [p["label"] for p in list_retention_policies(retention_file)]
    assert labels == sorted(labels)


def test_list_retention_empty_when_no_file(retention_file):
    assert list_retention_policies(retention_file) == []


# --- evaluate_retention ---

def _make_history(labels_and_ages):
    """labels_and_ages: list of (label, days_ago)"""
    entries = []
    for label, days_ago in labels_and_ages:
        captured = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
        entries.append({"label": label, "captured_at": captured})
    return entries


def test_evaluate_retention_prunes_oldest_by_count(retention_file):
    set_retention_policy("prod", retention_file, policy="count", max_count=2)
    history = _make_history([("prod-1", 10), ("prod-2", 5), ("prod-3", 1)])
    prunable = evaluate_retention("prod", history, retention_file)
    assert "prod-1" in prunable
    assert "prod-2" not in prunable
    assert "prod-3" not in prunable


def test_evaluate_retention_no_prune_when_within_count(retention_file):
    set_retention_policy("prod", retention_file, policy="count", max_count=5)
    history = _make_history([("prod-1", 3), ("prod-2", 1)])
    assert evaluate_retention("prod", history, retention_file) == []


def test_evaluate_retention_prunes_by_age(retention_file):
    set_retention_policy("prod", retention_file, policy="age", max_age_days=7)
    history = _make_history([("old", 10), ("recent", 2)])
    prunable = evaluate_retention("prod", history, retention_file)
    assert "old" in prunable
    assert "recent" not in prunable


def test_evaluate_retention_returns_empty_for_no_policy(retention_file):
    history = _make_history([("prod-1", 1)])
    assert evaluate_retention("unregistered", history, retention_file) == []
