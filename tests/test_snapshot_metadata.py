"""Tests for envforge.snapshot_metadata."""

import json
import pytest

from envforge.snapshot_metadata import (
    MetadataError,
    set_metadata,
    get_metadata,
    remove_metadata,
    clear_metadata,
    list_metadata,
)


@pytest.fixture
def metadata_file(tmp_path):
    return str(tmp_path / "metadata.json")


def test_set_metadata_creates_entry(metadata_file):
    result = set_metadata("prod", "owner", "alice", metadata_file)
    assert result["owner"] == "alice"


def test_set_metadata_persists_to_file(metadata_file):
    set_metadata("prod", "owner", "alice", metadata_file)
    raw = json.loads(open(metadata_file).read())
    assert raw["prod"]["owner"] == "alice"


def test_set_metadata_multiple_keys(metadata_file):
    set_metadata("prod", "owner", "alice", metadata_file)
    set_metadata("prod", "team", "platform", metadata_file)
    result = get_metadata("prod", metadata_file)
    assert result["owner"] == "alice"
    assert result["team"] == "platform"


def test_set_metadata_overwrites_existing(metadata_file):
    set_metadata("prod", "owner", "alice", metadata_file)
    set_metadata("prod", "owner", "bob", metadata_file)
    result = get_metadata("prod", metadata_file)
    assert result["owner"] == "bob"


def test_set_metadata_raises_on_empty_label(metadata_file):
    with pytest.raises(MetadataError, match="Label"):
        set_metadata("", "owner", "alice", metadata_file)


def test_set_metadata_raises_on_empty_key(metadata_file):
    with pytest.raises(MetadataError, match="key"):
        set_metadata("prod", "", "alice", metadata_file)


def test_get_metadata_returns_empty_for_unknown_label(metadata_file):
    result = get_metadata("unknown", metadata_file)
    assert result == {}


def test_get_metadata_raises_on_empty_label(metadata_file):
    with pytest.raises(MetadataError, match="Label"):
        get_metadata("", metadata_file)


def test_remove_metadata_deletes_key(metadata_file):
    set_metadata("prod", "owner", "alice", metadata_file)
    set_metadata("prod", "team", "platform", metadata_file)
    remove_metadata("prod", "owner", metadata_file)
    result = get_metadata("prod", metadata_file)
    assert "owner" not in result
    assert "team" in result


def test_remove_metadata_raises_on_missing_key(metadata_file):
    set_metadata("prod", "owner", "alice", metadata_file)
    with pytest.raises(MetadataError, match="not found"):
        remove_metadata("prod", "nonexistent", metadata_file)


def test_remove_metadata_raises_on_empty_label(metadata_file):
    with pytest.raises(MetadataError, match="Label"):
        remove_metadata("", "owner", metadata_file)


def test_clear_metadata_removes_all_keys(metadata_file):
    set_metadata("prod", "owner", "alice", metadata_file)
    set_metadata("prod", "team", "platform", metadata_file)
    clear_metadata("prod", metadata_file)
    result = get_metadata("prod", metadata_file)
    assert result == {}


def test_clear_metadata_does_not_affect_other_labels(metadata_file):
    set_metadata("prod", "owner", "alice", metadata_file)
    set_metadata("staging", "owner", "bob", metadata_file)
    clear_metadata("prod", metadata_file)
    assert get_metadata("staging", metadata_file)["owner"] == "bob"


def test_list_metadata_returns_all_labels(metadata_file):
    set_metadata("prod", "owner", "alice", metadata_file)
    set_metadata("staging", "owner", "bob", metadata_file)
    result = list_metadata(metadata_file)
    assert "prod" in result
    assert "staging" in result


def test_list_metadata_empty_file_returns_empty_dict(metadata_file):
    result = list_metadata(metadata_file)
    assert result == {}
