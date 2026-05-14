"""Tests for envforge.snapshot_checksum."""

import hashlib
import json
import pytest

from envforge.snapshot_checksum import (
    ChecksumError,
    assert_checksum,
    checksum_status,
    recompute_checksum,
    verify_checksum,
)


def make_snapshot(label="prod", variables=None, checksum=None):
    vars_ = variables if variables is not None else {"HOST": "localhost", "PORT": "8080"}
    cs = checksum or _chk(vars_)
    return {"label": label, "variables": vars_, "checksum": cs}


def _chk(variables):
    return hashlib.sha256(json.dumps(variables, sort_keys=True).encode()).hexdigest()


def test_verify_checksum_returns_true_for_valid_snapshot():
    snap = make_snapshot()
    assert verify_checksum(snap) is True


def test_verify_checksum_returns_false_for_tampered_variables():
    snap = make_snapshot()
    snap["variables"]["EXTRA"] = "injected"
    assert verify_checksum(snap) is False


def test_verify_checksum_returns_false_for_wrong_checksum():
    snap = make_snapshot(checksum="deadbeef")
    assert verify_checksum(snap) is False


def test_assert_checksum_passes_for_valid_snapshot():
    snap = make_snapshot()
    assert_checksum(snap)  # should not raise


def test_assert_checksum_raises_on_tampered_snapshot():
    snap = make_snapshot()
    snap["variables"]["INJECTED"] = "bad"
    with pytest.raises(ChecksumError, match="Checksum mismatch"):
        assert_checksum(snap)


def test_assert_checksum_error_includes_label():
    snap = make_snapshot(label="staging", checksum="badhash")
    with pytest.raises(ChecksumError, match="staging"):
        assert_checksum(snap)


def test_recompute_checksum_fixes_bad_checksum():
    snap = make_snapshot(checksum="wronghash")
    fixed = recompute_checksum(snap)
    assert verify_checksum(fixed) is True


def test_recompute_checksum_does_not_mutate_original():
    snap = make_snapshot(checksum="wronghash")
    original_cs = snap["checksum"]
    recompute_checksum(snap)
    assert snap["checksum"] == original_cs


def test_recompute_checksum_preserves_label_and_variables():
    snap = make_snapshot(label="dev", checksum="bad")
    fixed = recompute_checksum(snap)
    assert fixed["label"] == "dev"
    assert fixed["variables"] == snap["variables"]


def test_checksum_status_valid_snapshot():
    snap = make_snapshot()
    status = checksum_status(snap)
    assert status["valid"] is True
    assert status["label"] == snap["label"]
    assert status["stored"] == status["expected"]


def test_checksum_status_invalid_snapshot():
    snap = make_snapshot(checksum="badhash")
    status = checksum_status(snap)
    assert status["valid"] is False
    assert status["stored"] == "badhash"
    assert status["expected"] != "badhash"


def test_verify_checksum_raises_on_invalid_snapshot():
    with pytest.raises(ChecksumError):
        verify_checksum({"label": "x"})


def test_recompute_checksum_raises_on_invalid_snapshot():
    with pytest.raises(ChecksumError):
        recompute_checksum({"variables": {}})
