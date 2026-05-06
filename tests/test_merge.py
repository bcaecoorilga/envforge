"""Tests for envforge.merge module."""

import pytest
from envforge.merge import MergeError, merge_snapshots, list_conflicts


def make_snapshot(label: str, variables: dict) -> dict:
    import hashlib, json
    checksum = hashlib.sha256(json.dumps(variables, sort_keys=True).encode()).hexdigest()
    return {
        "label": label,
        "timestamp": "2024-01-01T00:00:00+00:00",
        "variables": variables,
        "checksum": checksum,
    }


def test_merge_last_wins_overrides_earlier():
    a = make_snapshot("dev", {"HOST": "localhost", "PORT": "3000"})
    b = make_snapshot("staging", {"HOST": "staging.example.com", "DEBUG": "false"})
    result = merge_snapshots([a, b], label="merged", strategy="last_wins")
    assert result["variables"]["HOST"] == "staging.example.com"
    assert result["variables"]["PORT"] == "3000"
    assert result["variables"]["DEBUG"] == "false"


def test_merge_first_wins_preserves_earlier():
    a = make_snapshot("dev", {"HOST": "localhost"})
    b = make_snapshot("prod", {"HOST": "prod.example.com", "SECRET": "abc"})
    result = merge_snapshots([a, b], label="merged", strategy="first_wins")
    assert result["variables"]["HOST"] == "localhost"
    assert result["variables"]["SECRET"] == "abc"


def test_merge_label_is_set():
    a = make_snapshot("dev", {"X": "1"})
    result = merge_snapshots([a], label="my-merge")
    assert result["label"] == "my-merge"


def test_merge_records_source_labels():
    a = make_snapshot("dev", {"A": "1"})
    b = make_snapshot("prod", {"B": "2"})
    result = merge_snapshots([a, b], label="merged")
    assert "dev" in result["merged_from"]
    assert "prod" in result["merged_from"]


def test_merge_checksum_is_present():
    a = make_snapshot("dev", {"K": "v"})
    result = merge_snapshots([a], label="merged")
    assert "checksum" in result
    assert len(result["checksum"]) == 64


def test_merge_exclude_keys():
    a = make_snapshot("dev", {"SECRET": "hidden", "HOST": "localhost"})
    result = merge_snapshots([a], label="merged", exclude_keys=["SECRET"])
    assert "SECRET" not in result["variables"]
    assert "HOST" in result["variables"]


def test_merge_empty_list_raises():
    with pytest.raises(MergeError, match="empty list"):
        merge_snapshots([], label="merged")


def test_merge_invalid_strategy_raises():
    a = make_snapshot("dev", {"X": "1"})
    with pytest.raises(MergeError, match="Unknown merge strategy"):
        merge_snapshots([a], label="merged", strategy="random")


def test_merge_invalid_snapshot_raises():
    with pytest.raises(MergeError, match="Invalid snapshot"):
        merge_snapshots([{"label": "bad"}], label="merged")


def test_list_conflicts_detects_differing_values():
    a = make_snapshot("dev", {"HOST": "localhost", "PORT": "3000"})
    b = make_snapshot("prod", {"HOST": "prod.example.com", "PORT": "3000"})
    conflicts = list_conflicts([a, b])
    assert "HOST" in conflicts
    assert "PORT" not in conflicts


def test_list_conflicts_returns_labels_and_values():
    a = make_snapshot("dev", {"DB": "dev_db"})
    b = make_snapshot("prod", {"DB": "prod_db"})
    conflicts = list_conflicts([a, b])
    labels = [label for label, _ in conflicts["DB"]]
    assert "dev" in labels
    assert "prod" in labels


def test_list_conflicts_no_conflicts():
    a = make_snapshot("dev", {"X": "same"})
    b = make_snapshot("prod", {"X": "same"})
    conflicts = list_conflicts([a, b])
    assert conflicts == {}
