"""Tests for envforge.tag module."""

import json
import os
import pytest

from envforge.tag import (
    TagError,
    add_tag,
    remove_tag,
    get_tags,
    find_by_tag,
    list_all_tags,
)


@pytest.fixture
def tag_file(tmp_path):
    return str(tmp_path / "tags.json")


def test_add_tag_creates_entry(tag_file):
    add_tag("prod-2024", "production", tag_file)
    assert "production" in get_tags("prod-2024", tag_file)


def test_add_tag_multiple_tags(tag_file):
    add_tag("prod-2024", "production", tag_file)
    add_tag("prod-2024", "stable", tag_file)
    tags = get_tags("prod-2024", tag_file)
    assert "production" in tags
    assert "stable" in tags


def test_add_tag_no_duplicates(tag_file):
    add_tag("prod-2024", "stable", tag_file)
    add_tag("prod-2024", "stable", tag_file)
    assert get_tags("prod-2024", tag_file).count("stable") == 1


def test_add_tag_raises_on_empty_label(tag_file):
    with pytest.raises(TagError):
        add_tag("", "stable", tag_file)


def test_add_tag_raises_on_empty_tag(tag_file):
    with pytest.raises(TagError):
        add_tag("prod-2024", "", tag_file)


def test_remove_tag_removes_entry(tag_file):
    add_tag("prod-2024", "production", tag_file)
    remove_tag("prod-2024", "production", tag_file)
    assert get_tags("prod-2024", tag_file) == []


def test_remove_tag_cleans_up_empty_label(tag_file):
    add_tag("prod-2024", "only-tag", tag_file)
    remove_tag("prod-2024", "only-tag", tag_file)
    assert "prod-2024" not in list_all_tags(tag_file)


def test_remove_tag_silent_on_missing(tag_file):
    # Should not raise even if tag or label don't exist
    remove_tag("nonexistent", "ghost", tag_file)


def test_get_tags_empty_for_unknown_label(tag_file):
    assert get_tags("unknown", tag_file) == []


def test_find_by_tag_returns_matching_labels(tag_file):
    add_tag("prod-2024", "stable", tag_file)
    add_tag("staging-2024", "stable", tag_file)
    add_tag("dev-2024", "experimental", tag_file)
    result = find_by_tag("stable", tag_file)
    assert "prod-2024" in result
    assert "staging-2024" in result
    assert "dev-2024" not in result


def test_find_by_tag_empty_when_none_match(tag_file):
    add_tag("prod-2024", "stable", tag_file)
    assert find_by_tag("nonexistent", tag_file) == []


def test_list_all_tags_returns_full_index(tag_file):
    add_tag("prod-2024", "production", tag_file)
    add_tag("dev-2024", "experimental", tag_file)
    index = list_all_tags(tag_file)
    assert "prod-2024" in index
    assert "dev-2024" in index


def test_list_all_tags_empty_file(tag_file):
    assert list_all_tags(tag_file) == {}
