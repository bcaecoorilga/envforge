"""Tests for envforge.promote."""

import pytest
from envforge.promote import (
    PromoteError,
    promote,
    list_promotion_changes,
)


def make_snapshot(label="dev", variables=None):
    import hashlib, json, datetime
    variables = variables or {"APP_ENV": "development", "DB_HOST": "localhost"}
    checksum = hashlib.sha256(json.dumps(variables, sort_keys=True).encode()).hexdigest()
    return {
        "label": label,
        "variables": variables,
        "checksum": checksum,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


def test_promote_sets_target_label():
    snap = make_snapshot()
    result = promote(snap, "staging")
    assert result["label"] == "staging"


def test_promote_records_promoted_from():
    snap = make_snapshot(label="dev")
    result = promote(snap, "staging")
    assert result["promoted_from"] == "dev"


def test_promote_copies_variables():
    snap = make_snapshot(variables={"FOO": "bar", "BAZ": "qux"})
    result = promote(snap, "staging")
    assert result["variables"]["FOO"] == "bar"
    assert result["variables"]["BAZ"] == "qux"


def test_promote_does_not_mutate_original():
    snap = make_snapshot(variables={"FOO": "bar"})
    promote(snap, "staging", overrides={"FOO": "changed"})
    assert snap["variables"]["FOO"] == "bar"


def test_promote_applies_overrides():
    snap = make_snapshot(variables={"APP_ENV": "development"})
    result = promote(snap, "staging", overrides={"APP_ENV": "staging"})
    assert result["variables"]["APP_ENV"] == "staging"


def test_promote_adds_new_keys_via_overrides():
    snap = make_snapshot(variables={"FOO": "bar"})
    result = promote(snap, "prod", overrides={"NEW_KEY": "new_val"})
    assert result["variables"]["NEW_KEY"] == "new_val"


def test_promote_exclude_keys_drops_variables():
    snap = make_snapshot(variables={"FOO": "bar", "SECRET": "s3cr3t"})
    result = promote(snap, "staging", exclude_keys=["SECRET"])
    assert "SECRET" not in result["variables"]
    assert "FOO" in result["variables"]


def test_promote_add_prefix_renames_keys():
    snap = make_snapshot(variables={"HOST": "localhost"})
    result = promote(snap, "staging", add_prefix="STG_")
    assert "STG_HOST" in result["variables"]
    assert "HOST" not in result["variables"]


def test_promote_updates_checksum():
    snap = make_snapshot(variables={"FOO": "bar"})
    result = promote(snap, "staging", overrides={"FOO": "different"})
    assert result["checksum"] != snap["checksum"]


def test_promote_raises_on_empty_label():
    snap = make_snapshot()
    with pytest.raises(PromoteError, match="target_label"):
        promote(snap, "  ")


def test_promote_raises_on_invalid_snapshot():
    with pytest.raises(PromoteError):
        promote({"label": "bad"}, "staging")


def test_promote_raises_on_invalid_overrides():
    snap = make_snapshot()
    with pytest.raises(PromoteError, match="overrides"):
        promote(snap, "staging", overrides="not-a-dict")


def test_list_promotion_changes_added():
    src = make_snapshot(variables={"FOO": "bar"})
    promoted = promote(src, "staging", overrides={"NEW": "val"})
    changes = list_promotion_changes(src, promoted)
    assert "NEW" in changes["added"]


def test_list_promotion_changes_removed():
    src = make_snapshot(variables={"FOO": "bar", "OLD": "gone"})
    promoted = promote(src, "staging", exclude_keys=["OLD"])
    changes = list_promotion_changes(src, promoted)
    assert "OLD" in changes["removed"]


def test_list_promotion_changes_overridden():
    src = make_snapshot(variables={"APP_ENV": "dev"})
    promoted = promote(src, "staging", overrides={"APP_ENV": "staging"})
    changes = list_promotion_changes(src, promoted)
    assert "APP_ENV" in changes["overridden"]
    assert changes["overridden"]["APP_ENV"]["from"] == "dev"
    assert changes["overridden"]["APP_ENV"]["to"] == "staging"
