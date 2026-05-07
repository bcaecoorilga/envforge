"""Tests for envforge.interpolate."""

import pytest
from envforge.interpolate import (
    InterpolateError,
    interpolate,
    list_references,
    has_unresolved,
)


def make_snapshot(variables: dict, label: str = "test") -> dict:
    return {
        "label": label,
        "variables": variables,
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00",
    }


def test_interpolate_resolves_braced_reference():
    snap = make_snapshot({"BASE": "/home/user", "PATH": "${BASE}/bin"})
    result = interpolate(snap)
    assert result["variables"]["PATH"] == "/home/user/bin"


def test_interpolate_resolves_dollar_reference():
    snap = make_snapshot({"HOST": "localhost", "URL": "http://$HOST:8080"})
    result = interpolate(snap)
    assert result["variables"]["URL"] == "http://localhost:8080"


def test_interpolate_uses_context_override():
    snap = make_snapshot({"GREETING": "Hello, ${NAME}!"})
    result = interpolate(snap, context={"NAME": "World"})
    assert result["variables"]["GREETING"] == "Hello, World!"


def test_interpolate_leaves_unresolved_when_not_strict():
    snap = make_snapshot({"VAL": "${MISSING}_suffix"})
    result = interpolate(snap, strict=False)
    assert result["variables"]["VAL"] == "${MISSING}_suffix"


def test_interpolate_raises_on_unresolved_when_strict():
    snap = make_snapshot({"VAL": "${MISSING}"})
    with pytest.raises(InterpolateError, match="Unresolved reference"):
        interpolate(snap, strict=True)


def test_interpolate_does_not_mutate_original():
    variables = {"A": "1", "B": "${A}"}
    snap = make_snapshot(variables)
    interpolate(snap)
    assert snap["variables"]["B"] == "${A}"


def test_interpolate_preserves_metadata():
    snap = make_snapshot({"X": "${X}"}, label="prod")
    result = interpolate(snap, strict=False)
    assert result["label"] == "prod"
    assert result["checksum"] == snap["checksum"]
    assert result["timestamp"] == snap["timestamp"]


def test_interpolate_raises_on_invalid_snapshot():
    with pytest.raises(InterpolateError):
        interpolate({"bad": "data"})


def test_list_references_returns_refs():
    snap = make_snapshot({"A": "1", "B": "${A}/path", "C": "$A and ${A}"})
    refs = list_references(snap)
    assert refs["B"] == ["A"]
    assert refs["C"] == ["A", "A"]
    assert "A" not in refs


def test_list_references_empty_when_no_refs():
    snap = make_snapshot({"A": "plain", "B": "also plain"})
    assert list_references(snap) == {}


def test_has_unresolved_true_when_missing():
    snap = make_snapshot({"VAL": "${GHOST}"})
    assert has_unresolved(snap) is True


def test_has_unresolved_false_when_all_resolved():
    snap = make_snapshot({"A": "1", "B": "${A}"})
    assert has_unresolved(snap) is False


def test_has_unresolved_resolves_via_context():
    snap = make_snapshot({"VAL": "${EXTERNAL}"})
    assert has_unresolved(snap, context={"EXTERNAL": "value"}) is False
