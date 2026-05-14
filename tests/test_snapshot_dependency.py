"""Tests for envforge.snapshot_dependency."""

import json
import os
import pytest

from envforge.snapshot_dependency import (
    DependencyError,
    add_dependency,
    remove_dependency,
    get_dependencies,
    get_dependents,
    list_all,
)


@pytest.fixture
def dep_file(tmp_path):
    return str(tmp_path / "deps.json")


def test_add_dependency_creates_entry(dep_file):
    result = add_dependency("staging", "dev", dep_file)
    assert any(e["depends_on"] == "dev" for e in result)


def test_add_dependency_persists_to_file(dep_file):
    add_dependency("staging", "dev", dep_file)
    with open(dep_file) as f:
        data = json.load(f)
    assert "staging" in data


def test_add_dependency_stores_reason(dep_file):
    add_dependency("staging", "dev", dep_file, reason="base config")
    deps = get_dependencies("staging", dep_file)
    assert deps[0]["reason"] == "base config"


def test_add_dependency_no_duplicates(dep_file):
    add_dependency("staging", "dev", dep_file)
    add_dependency("staging", "dev", dep_file)
    deps = get_dependencies("staging", dep_file)
    assert len(deps) == 1


def test_add_dependency_raises_on_empty_label(dep_file):
    with pytest.raises(DependencyError):
        add_dependency("", "dev", dep_file)


def test_add_dependency_raises_on_empty_depends_on(dep_file):
    with pytest.raises(DependencyError):
        add_dependency("staging", "", dep_file)


def test_add_dependency_raises_on_self_reference(dep_file):
    with pytest.raises(DependencyError):
        add_dependency("staging", "staging", dep_file)


def test_add_dependency_multiple_deps(dep_file):
    add_dependency("prod", "staging", dep_file)
    add_dependency("prod", "dev", dep_file)
    deps = get_dependencies("prod", dep_file)
    assert len(deps) == 2


def test_remove_dependency_removes_entry(dep_file):
    add_dependency("staging", "dev", dep_file)
    remove_dependency("staging", "dev", dep_file)
    deps = get_dependencies("staging", dep_file)
    assert len(deps) == 0


def test_remove_dependency_raises_on_missing_label(dep_file):
    with pytest.raises(DependencyError):
        remove_dependency("nonexistent", "dev", dep_file)


def test_remove_dependency_raises_on_missing_dep(dep_file):
    add_dependency("staging", "dev", dep_file)
    with pytest.raises(DependencyError):
        remove_dependency("staging", "prod", dep_file)


def test_get_dependencies_returns_empty_for_unknown(dep_file):
    result = get_dependencies("unknown", dep_file)
    assert result == []


def test_get_dependents_returns_labels(dep_file):
    add_dependency("staging", "dev", dep_file)
    add_dependency("prod", "dev", dep_file)
    dependents = get_dependents("dev", dep_file)
    assert "staging" in dependents
    assert "prod" in dependents


def test_get_dependents_returns_empty_when_none(dep_file):
    assert get_dependents("orphan", dep_file) == []


def test_list_all_returns_full_map(dep_file):
    add_dependency("staging", "dev", dep_file)
    add_dependency("prod", "staging", dep_file)
    data = list_all(dep_file)
    assert "staging" in data
    assert "prod" in data
