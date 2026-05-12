"""Tests for envforge.snapshot_copy."""

import pytest
from envforge.snapshot_copy import CopyError, copy_keys, list_copy_changes


def make_snapshot(label: str, variables: dict) -> dict:
    import hashlib, json
    checksum = hashlib.sha256(json.dumps(variables, sort_keys=True).encode()).hexdigest()
    return {"label": label, "variables": variables, "checksum": checksum, "timestamp": "2024-01-01T00:00:00"}


@pytest.fixture
def source():
    return make_snapshot("dev", {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"})


@pytest.fixture
def destination():
    return make_snapshot("prod", {"DB_HOST": "prod-db", "APP_ENV": "production"})


def test_copy_keys_adds_new_keys(source, destination):
    result = copy_keys(source, destination, keys=["DB_PORT"])
    assert result["variables"]["DB_PORT"] == "5432"


def test_copy_keys_overwrites_existing_by_default(source, destination):
    result = copy_keys(source, destination, keys=["DB_HOST"])
    assert result["variables"]["DB_HOST"] == "localhost"


def test_copy_keys_overwrite_false_preserves_existing(source, destination):
    result = copy_keys(source, destination, keys=["DB_HOST"], overwrite=False)
    assert result["variables"]["DB_HOST"] == "prod-db"


def test_copy_keys_overwrite_false_still_adds_new_keys(source, destination):
    result = copy_keys(source, destination, keys=["DB_PORT"], overwrite=False)
    assert result["variables"]["DB_PORT"] == "5432"


def test_copy_all_keys_when_none_specified(source, destination):
    result = copy_keys(source, destination)
    for key in source["variables"]:
        assert key in result["variables"]


def test_copy_keys_does_not_mutate_destination(source, destination):
    original_vars = dict(destination["variables"])
    copy_keys(source, destination, keys=["DB_PORT"])
    assert destination["variables"] == original_vars


def test_copy_keys_updates_checksum(source, destination):
    old_checksum = destination["checksum"]
    result = copy_keys(source, destination, keys=["DB_PORT"])
    assert result["checksum"] != old_checksum


def test_copy_keys_records_copied_from_label(source, destination):
    result = copy_keys(source, destination, keys=["DB_PORT"])
    assert result["meta"]["copied_from"] == "dev"


def test_copy_keys_records_copied_keys(source, destination):
    result = copy_keys(source, destination, keys=["DB_PORT", "SECRET"])
    assert "DB_PORT" in result["meta"]["copied_keys"]
    assert "SECRET" in result["meta"]["copied_keys"]


def test_copy_keys_records_skipped_keys(source, destination):
    result = copy_keys(source, destination, keys=["DB_HOST"], overwrite=False)
    assert "DB_HOST" in result["meta"]["skipped_keys"]


def test_copy_keys_raises_on_unknown_key(source, destination):
    with pytest.raises(CopyError, match="MISSING_KEY"):
        copy_keys(source, destination, keys=["MISSING_KEY"])


def test_copy_keys_raises_on_invalid_source(destination):
    with pytest.raises(CopyError):
        copy_keys({"bad": True}, destination)


def test_copy_keys_raises_on_invalid_destination(source):
    with pytest.raises(CopyError):
        copy_keys(source, {"bad": True})


def test_list_copy_changes_add(source, destination):
    changes = list_copy_changes(source, destination, keys=["DB_PORT"])
    assert changes["DB_PORT"] == "add"


def test_list_copy_changes_overwrite(source, destination):
    changes = list_copy_changes(source, destination, keys=["DB_HOST"])
    assert changes["DB_HOST"] == "overwrite"


def test_list_copy_changes_all_keys(source, destination):
    changes = list_copy_changes(source, destination)
    assert set(changes.keys()) == set(source["variables"].keys())
