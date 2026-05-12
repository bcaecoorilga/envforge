"""Tests for envforge.snapshot_group."""

import json
import pytest

from envforge.snapshot_group import (
    GroupError,
    create_group,
    add_to_group,
    remove_from_group,
    get_group,
    list_groups,
    delete_group,
)


@pytest.fixture
def group_file(tmp_path):
    return str(tmp_path / "groups.json")


def test_create_group_creates_entry(group_file):
    entry = create_group("prod", group_file=group_file)
    assert entry["name"] == "prod"


def test_create_group_persists_to_file(group_file):
    create_group("staging", group_file=group_file)
    with open(group_file) as f:
        data = json.load(f)
    assert "staging" in data


def test_create_group_sets_description(group_file):
    entry = create_group("dev", description="Development group", group_file=group_file)
    assert entry["description"] == "Development group"


def test_create_group_starts_with_empty_labels(group_file):
    entry = create_group("dev", group_file=group_file)
    assert entry["labels"] == []


def test_create_group_raises_on_empty_name(group_file):
    with pytest.raises(GroupError, match="empty"):
        create_group("", group_file=group_file)


def test_create_group_raises_on_duplicate_name(group_file):
    create_group("prod", group_file=group_file)
    with pytest.raises(GroupError, match="already exists"):
        create_group("prod", group_file=group_file)


def test_add_to_group_appends_label(group_file):
    create_group("prod", group_file=group_file)
    entry = add_to_group("prod", "snap-001", group_file=group_file)
    assert "snap-001" in entry["labels"]


def test_add_to_group_multiple_labels(group_file):
    create_group("prod", group_file=group_file)
    add_to_group("prod", "snap-001", group_file=group_file)
    add_to_group("prod", "snap-002", group_file=group_file)
    entry = get_group("prod", group_file=group_file)
    assert len(entry["labels"]) == 2


def test_add_to_group_raises_on_missing_group(group_file):
    with pytest.raises(GroupError, match="does not exist"):
        add_to_group("nonexistent", "snap-001", group_file=group_file)


def test_add_to_group_raises_on_duplicate_label(group_file):
    create_group("prod", group_file=group_file)
    add_to_group("prod", "snap-001", group_file=group_file)
    with pytest.raises(GroupError, match="already in group"):
        add_to_group("prod", "snap-001", group_file=group_file)


def test_add_to_group_raises_on_empty_label(group_file):
    create_group("prod", group_file=group_file)
    with pytest.raises(GroupError, match="empty"):
        add_to_group("prod", "", group_file=group_file)


def test_remove_from_group_removes_label(group_file):
    create_group("prod", group_file=group_file)
    add_to_group("prod", "snap-001", group_file=group_file)
    entry = remove_from_group("prod", "snap-001", group_file=group_file)
    assert "snap-001" not in entry["labels"]


def test_remove_from_group_raises_on_missing_label(group_file):
    create_group("prod", group_file=group_file)
    with pytest.raises(GroupError, match="not found"):
        remove_from_group("prod", "snap-999", group_file=group_file)


def test_list_groups_returns_all(group_file):
    create_group("dev", group_file=group_file)
    create_group("prod", group_file=group_file)
    groups = list_groups(group_file=group_file)
    names = [g["name"] for g in groups]
    assert "dev" in names and "prod" in names


def test_list_groups_empty_when_no_file(group_file):
    groups = list_groups(group_file=group_file)
    assert groups == []


def test_delete_group_removes_entry(group_file):
    create_group("staging", group_file=group_file)
    delete_group("staging", group_file=group_file)
    with pytest.raises(GroupError):
        get_group("staging", group_file=group_file)


def test_delete_group_raises_on_missing(group_file):
    with pytest.raises(GroupError, match="does not exist"):
        delete_group("ghost", group_file=group_file)
