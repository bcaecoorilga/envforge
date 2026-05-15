"""Tests for envforge.snapshot_category."""

import json
import pytest

from envforge.snapshot_category import (
    CategoryError,
    assign_category,
    get_category,
    list_by_category,
    list_categories,
    remove_category,
)


@pytest.fixture
def category_file(tmp_path):
    return str(tmp_path / "categories.json")


def test_assign_category_creates_entry(category_file):
    result = assign_category("prod", "production", path=category_file)
    assert result["prod"] == "production"


def test_assign_category_persists_to_file(category_file):
    assign_category("staging", "non-production", path=category_file)
    with open(category_file) as f:
        data = json.load(f)
    assert data["staging"] == "non-production"


def test_assign_category_overwrites_existing(category_file):
    assign_category("prod", "production", path=category_file)
    assign_category("prod", "critical", path=category_file)
    assert get_category("prod", path=category_file) == "critical"


def test_assign_category_multiple_labels(category_file):
    assign_category("prod", "production", path=category_file)
    assign_category("dev", "development", path=category_file)
    cats = list_categories(path=category_file)
    assert cats["prod"] == "production"
    assert cats["dev"] == "development"


def test_assign_category_raises_on_empty_label(category_file):
    with pytest.raises(CategoryError, match="label"):
        assign_category("", "production", path=category_file)


def test_assign_category_raises_on_empty_category(category_file):
    with pytest.raises(CategoryError, match="Category"):
        assign_category("prod", "", path=category_file)


def test_get_category_returns_value(category_file):
    assign_category("prod", "production", path=category_file)
    assert get_category("prod", path=category_file) == "production"


def test_get_category_returns_none_when_not_set(category_file):
    assert get_category("unknown", path=category_file) is None


def test_get_category_raises_on_empty_label(category_file):
    with pytest.raises(CategoryError):
        get_category("", path=category_file)


def test_remove_category_deletes_entry(category_file):
    assign_category("prod", "production", path=category_file)
    remove_category("prod", path=category_file)
    assert get_category("prod", path=category_file) is None


def test_remove_category_raises_when_not_found(category_file):
    with pytest.raises(CategoryError, match="No category"):
        remove_category("ghost", path=category_file)


def test_remove_category_raises_on_empty_label(category_file):
    with pytest.raises(CategoryError):
        remove_category("", path=category_file)


def test_list_by_category_returns_matching_labels(category_file):
    assign_category("prod", "production", path=category_file)
    assign_category("prod-eu", "production", path=category_file)
    assign_category("dev", "development", path=category_file)
    result = list_by_category("production", path=category_file)
    assert sorted(result) == ["prod", "prod-eu"]


def test_list_by_category_returns_empty_for_unknown(category_file):
    assign_category("prod", "production", path=category_file)
    assert list_by_category("staging", path=category_file) == []


def test_list_by_category_raises_on_empty_category(category_file):
    with pytest.raises(CategoryError):
        list_by_category("", path=category_file)


def test_list_categories_returns_all(category_file):
    assign_category("prod", "production", path=category_file)
    assign_category("dev", "development", path=category_file)
    all_cats = list_categories(path=category_file)
    assert len(all_cats) == 2
    assert all_cats["prod"] == "production"
    assert all_cats["dev"] == "development"


def test_list_categories_empty_when_no_file(category_file):
    assert list_categories(path=category_file) == {}
