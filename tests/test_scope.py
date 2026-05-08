"""Tests for envforge.scope."""

import json
import pytest

from envforge.scope import (
    ScopeError,
    assign_scope,
    remove_scope,
    get_scope,
    list_by_scope,
    all_scopes,
)


@pytest.fixture
def scope_file(tmp_path):
    return str(tmp_path / "scopes.json")


def test_assign_scope_creates_entry(scope_file):
    result = assign_scope("snap-1", "dev", scope_file)
    assert result["label"] == "snap-1"
    assert result["scope"] == "dev"


def test_assign_scope_persists_to_file(scope_file):
    assign_scope("snap-1", "staging", scope_file)
    with open(scope_file) as f:
        data = json.load(f)
    assert data["snap-1"] == "staging"


def test_assign_scope_overwrites_existing(scope_file):
    assign_scope("snap-1", "dev", scope_file)
    assign_scope("snap-1", "prod", scope_file)
    assert get_scope("snap-1", scope_file) == "prod"


def test_assign_scope_raises_on_empty_label(scope_file):
    with pytest.raises(ScopeError, match="Label"):
        assign_scope("", "dev", scope_file)


def test_assign_scope_raises_on_empty_scope(scope_file):
    with pytest.raises(ScopeError, match="Scope"):
        assign_scope("snap-1", "", scope_file)


def test_remove_scope_deletes_entry(scope_file):
    assign_scope("snap-1", "dev", scope_file)
    remove_scope("snap-1", scope_file)
    assert get_scope("snap-1", scope_file) is None


def test_remove_scope_raises_on_missing_label(scope_file):
    with pytest.raises(ScopeError, match="No scope assigned"):
        remove_scope("nonexistent", scope_file)


def test_get_scope_returns_none_for_unknown_label(scope_file):
    assert get_scope("unknown", scope_file) is None


def test_get_scope_returns_correct_scope(scope_file):
    assign_scope("snap-2", "prod", scope_file)
    assert get_scope("snap-2", scope_file) == "prod"


def test_list_by_scope_returns_matching_labels(scope_file):
    assign_scope("snap-1", "dev", scope_file)
    assign_scope("snap-2", "dev", scope_file)
    assign_scope("snap-3", "prod", scope_file)
    result = list_by_scope("dev", scope_file)
    assert set(result) == {"snap-1", "snap-2"}


def test_list_by_scope_returns_empty_for_unknown_scope(scope_file):
    assign_scope("snap-1", "dev", scope_file)
    assert list_by_scope("staging", scope_file) == []


def test_all_scopes_returns_full_mapping(scope_file):
    assign_scope("snap-1", "dev", scope_file)
    assign_scope("snap-2", "prod", scope_file)
    result = all_scopes(scope_file)
    assert result == {"snap-1": "dev", "snap-2": "prod"}


def test_all_scopes_returns_empty_when_no_file(scope_file):
    result = all_scopes(scope_file)
    assert result == {}
