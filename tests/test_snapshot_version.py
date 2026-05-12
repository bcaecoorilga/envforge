"""Tests for envforge.snapshot_version."""

import json
import pytest
from pathlib import Path

from envforge.snapshot_version import (
    VersionError,
    set_version,
    get_version,
    remove_version,
    list_versions,
    bump_version,
)


@pytest.fixture
def version_file(tmp_path):
    return str(tmp_path / "versions.json")


def test_set_version_creates_entry(version_file):
    result = set_version("prod", "1.2.3", version_file)
    assert result["label"] == "prod"
    assert result["version"] == "1.2.3"


def test_set_version_persists_to_file(version_file):
    set_version("staging", "0.1.0", version_file)
    data = json.loads(Path(version_file).read_text())
    assert data["staging"] == "0.1.0"


def test_set_version_overwrites_existing(version_file):
    set_version("prod", "1.0.0", version_file)
    set_version("prod", "2.0.0", version_file)
    assert get_version("prod", version_file) == "2.0.0"


def test_set_version_raises_on_empty_label(version_file):
    with pytest.raises(VersionError, match="empty"):
        set_version("", "1.0.0", version_file)


def test_set_version_raises_on_invalid_format(version_file):
    with pytest.raises(VersionError, match="Invalid version"):
        set_version("prod", "v1.0", version_file)


def test_set_version_raises_on_partial_version(version_file):
    with pytest.raises(VersionError):
        set_version("prod", "1.0", version_file)


def test_get_version_returns_assigned_version(version_file):
    set_version("dev", "3.4.5", version_file)
    assert get_version("dev", version_file) == "3.4.5"


def test_get_version_returns_none_for_unknown_label(version_file):
    assert get_version("unknown", version_file) is None


def test_get_version_raises_on_empty_label(version_file):
    with pytest.raises(VersionError):
        get_version("", version_file)


def test_remove_version_returns_true_when_removed(version_file):
    set_version("prod", "1.0.0", version_file)
    assert remove_version("prod", version_file) is True
    assert get_version("prod", version_file) is None


def test_remove_version_returns_false_when_not_found(version_file):
    assert remove_version("nonexistent", version_file) is False


def test_list_versions_returns_all_entries(version_file):
    set_version("prod", "1.0.0", version_file)
    set_version("staging", "0.9.0", version_file)
    results = list_versions(version_file)
    labels = [r["label"] for r in results]
    assert "prod" in labels
    assert "staging" in labels


def test_list_versions_empty_when_no_entries(version_file):
    assert list_versions(version_file) == []


def test_bump_version_patch(version_file):
    set_version("prod", "1.2.3", version_file)
    result = bump_version("prod", "patch", version_file)
    assert result["version"] == "1.2.4"


def test_bump_version_minor_resets_patch(version_file):
    set_version("prod", "1.2.3", version_file)
    result = bump_version("prod", "minor", version_file)
    assert result["version"] == "1.3.0"


def test_bump_version_major_resets_minor_and_patch(version_file):
    set_version("prod", "1.2.3", version_file)
    result = bump_version("prod", "major", version_file)
    assert result["version"] == "2.0.0"


def test_bump_version_raises_on_unknown_label(version_file):
    with pytest.raises(VersionError, match="No version found"):
        bump_version("ghost", "patch", version_file)


def test_bump_version_raises_on_invalid_part(version_file):
    set_version("prod", "1.0.0", version_file)
    with pytest.raises(VersionError, match="part must be one of"):
        bump_version("prod", "build", version_file)
