"""Tests for envforge.snapshot_label."""

import json
import os
import pytest

from envforge.snapshot_label import (
    LabelError,
    list_labels,
    register_label,
    rename_label,
    resolve_label,
    unregister_label,
)


@pytest.fixture
def label_file(tmp_path):
    return str(tmp_path / "labels.json")


def test_register_label_creates_entry(label_file):
    register_label("prod", "/snaps/prod.json", label_file)
    data = json.loads(open(label_file).read())
    assert "prod" in data


def test_register_label_stores_path(label_file):
    register_label("staging", "/snaps/staging.json", label_file)
    data = json.loads(open(label_file).read())
    assert data["staging"] == "/snaps/staging.json"


def test_register_label_multiple(label_file):
    register_label("dev", "/snaps/dev.json", label_file)
    register_label("prod", "/snaps/prod.json", label_file)
    data = json.loads(open(label_file).read())
    assert len(data) == 2


def test_register_label_raises_on_empty_label(label_file):
    with pytest.raises(LabelError, match="empty"):
        register_label("", "/snaps/prod.json", label_file)


def test_register_label_raises_on_empty_path(label_file):
    with pytest.raises(LabelError, match="empty"):
        register_label("prod", "", label_file)


def test_unregister_label_removes_entry(label_file):
    register_label("prod", "/snaps/prod.json", label_file)
    unregister_label("prod", label_file)
    data = json.loads(open(label_file).read())
    assert "prod" not in data


def test_unregister_label_raises_on_missing(label_file):
    with pytest.raises(LabelError, match="not registered"):
        unregister_label("ghost", label_file)


def test_resolve_label_returns_path(label_file):
    register_label("dev", "/snaps/dev.json", label_file)
    assert resolve_label("dev", label_file) == "/snaps/dev.json"


def test_resolve_label_returns_none_for_unknown(label_file):
    assert resolve_label("unknown", label_file) is None


def test_list_labels_returns_all(label_file):
    register_label("dev", "/snaps/dev.json", label_file)
    register_label("prod", "/snaps/prod.json", label_file)
    entries = list_labels(label_file)
    labels = [e["label"] for e in entries]
    assert "dev" in labels
    assert "prod" in labels


def test_list_labels_empty_when_no_file(label_file):
    assert list_labels(label_file) == []


def test_rename_label_updates_key(label_file):
    register_label("old", "/snaps/old.json", label_file)
    rename_label("old", "new", label_file)
    data = json.loads(open(label_file).read())
    assert "new" in data
    assert "old" not in data


def test_rename_label_preserves_path(label_file):
    register_label("old", "/snaps/old.json", label_file)
    rename_label("old", "new", label_file)
    data = json.loads(open(label_file).read())
    assert data["new"] == "/snaps/old.json"


def test_rename_label_raises_on_missing_old(label_file):
    with pytest.raises(LabelError, match="not registered"):
        rename_label("ghost", "new", label_file)


def test_rename_label_raises_on_duplicate_new(label_file):
    register_label("a", "/snaps/a.json", label_file)
    register_label("b", "/snaps/b.json", label_file)
    with pytest.raises(LabelError, match="already registered"):
        rename_label("a", "b", label_file)


def test_rename_label_raises_on_empty_new_label(label_file):
    register_label("old", "/snaps/old.json", label_file)
    with pytest.raises(LabelError, match="empty"):
        rename_label("old", "", label_file)
