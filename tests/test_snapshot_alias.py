"""Tests for envforge/snapshot_alias.py."""

import json
import os
import pytest

from envforge.snapshot_alias import (
    AliasError,
    add_alias,
    update_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
)


@pytest.fixture
def alias_file(tmp_path):
    return str(tmp_path / "aliases.json")


def test_add_alias_creates_entry(alias_file):
    add_alias("prod", "production-2024-01", alias_file)
    with open(alias_file) as f:
        data = json.load(f)
    assert data["prod"] == "production-2024-01"


def test_add_alias_multiple_aliases(alias_file):
    add_alias("prod", "production-2024-01", alias_file)
    add_alias("staging", "staging-2024-01", alias_file)
    aliases = list_aliases(alias_file)
    assert len(aliases) == 2


def test_add_alias_raises_on_empty_alias(alias_file):
    with pytest.raises(AliasError, match="must not be empty"):
        add_alias("", "some-label", alias_file)


def test_add_alias_raises_on_empty_label(alias_file):
    with pytest.raises(AliasError, match="must not be empty"):
        add_alias("prod", "", alias_file)


def test_add_alias_raises_on_duplicate(alias_file):
    add_alias("prod", "production-2024-01", alias_file)
    with pytest.raises(AliasError, match="already exists"):
        add_alias("prod", "production-2024-02", alias_file)


def test_update_alias_changes_label(alias_file):
    add_alias("prod", "production-2024-01", alias_file)
    update_alias("prod", "production-2024-02", alias_file)
    assert resolve_alias("prod", alias_file) == "production-2024-02"


def test_update_alias_raises_on_missing(alias_file):
    with pytest.raises(AliasError, match="does not exist"):
        update_alias("nonexistent", "some-label", alias_file)


def test_remove_alias_deletes_entry(alias_file):
    add_alias("prod", "production-2024-01", alias_file)
    remove_alias("prod", alias_file)
    assert resolve_alias("prod", alias_file) is None


def test_remove_alias_raises_on_missing(alias_file):
    with pytest.raises(AliasError, match="not found"):
        remove_alias("ghost", alias_file)


def test_resolve_alias_returns_label(alias_file):
    add_alias("dev", "dev-snapshot-42", alias_file)
    assert resolve_alias("dev", alias_file) == "dev-snapshot-42"


def test_resolve_alias_returns_none_for_missing(alias_file):
    assert resolve_alias("unknown", alias_file) is None


def test_list_aliases_returns_sorted(alias_file):
    add_alias("staging", "staging-label", alias_file)
    add_alias("prod", "prod-label", alias_file)
    result = list_aliases(alias_file)
    assert result[0]["alias"] == "prod"
    assert result[1]["alias"] == "staging"


def test_list_aliases_empty_when_no_file(alias_file):
    result = list_aliases(alias_file)
    assert result == []
