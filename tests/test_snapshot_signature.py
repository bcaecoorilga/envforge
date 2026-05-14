"""Tests for envforge.snapshot_signature."""

import pytest

from envforge.snapshot_signature import (
    SignatureError,
    assert_signature,
    sign_snapshot,
    strip_signature,
    verify_signature,
)


SECRET = "super-secret-key"


def make_snapshot(label="prod", variables=None):
    variables = variables or {"DB_HOST": "localhost", "PORT": "5432"}
    return {
        "label": label,
        "variables": variables,
        "checksum": "abc123",
        "timestamp": "2024-01-01T00:00:00",
    }


# ---------------------------------------------------------------------------
# sign_snapshot
# ---------------------------------------------------------------------------

def test_sign_snapshot_adds_signature_key():
    snap = make_snapshot()
    signed = sign_snapshot(snap, SECRET)
    assert "signature" in signed


def test_sign_snapshot_signature_is_string():
    snap = make_snapshot()
    signed = sign_snapshot(snap, SECRET)
    assert isinstance(signed["signature"], str)
    assert len(signed["signature"]) == 64  # SHA-256 hex digest


def test_sign_snapshot_does_not_mutate_original():
    snap = make_snapshot()
    sign_snapshot(snap, SECRET)
    assert "signature" not in snap


def test_sign_snapshot_is_deterministic():
    snap = make_snapshot()
    sig1 = sign_snapshot(snap, SECRET)["signature"]
    sig2 = sign_snapshot(snap, SECRET)["signature"]
    assert sig1 == sig2


def test_sign_snapshot_differs_for_different_secrets():
    snap = make_snapshot()
    sig1 = sign_snapshot(snap, "secret-a")["signature"]
    sig2 = sign_snapshot(snap, "secret-b")["signature"]
    assert sig1 != sig2


def test_sign_snapshot_raises_on_empty_secret():
    snap = make_snapshot()
    with pytest.raises(SignatureError, match="Secret must not be empty"):
        sign_snapshot(snap, "")


def test_sign_snapshot_raises_on_invalid_snapshot():
    with pytest.raises(SignatureError):
        sign_snapshot("not-a-dict", SECRET)


# ---------------------------------------------------------------------------
# verify_signature
# ---------------------------------------------------------------------------

def test_verify_signature_returns_true_for_valid_signature():
    snap = make_snapshot()
    signed = sign_snapshot(snap, SECRET)
    assert verify_signature(signed, SECRET) is True


def test_verify_signature_returns_false_for_wrong_secret():
    signed = sign_snapshot(make_snapshot(), SECRET)
    assert verify_signature(signed, "wrong-secret") is False


def test_verify_signature_returns_false_when_signature_missing():
    snap = make_snapshot()
    assert verify_signature(snap, SECRET) is False


def test_verify_signature_returns_false_after_variable_tampered():
    signed = sign_snapshot(make_snapshot(), SECRET)
    signed["variables"]["DB_HOST"] = "evil-host"
    assert verify_signature(signed, SECRET) is False


# ---------------------------------------------------------------------------
# assert_signature
# ---------------------------------------------------------------------------

def test_assert_signature_passes_for_valid_signature():
    signed = sign_snapshot(make_snapshot(), SECRET)
    assert_signature(signed, SECRET)  # should not raise


def test_assert_signature_raises_on_invalid_signature():
    signed = sign_snapshot(make_snapshot(), SECRET)
    with pytest.raises(SignatureError, match="Signature verification failed"):
        assert_signature(signed, "wrong-secret")


# ---------------------------------------------------------------------------
# strip_signature
# ---------------------------------------------------------------------------

def test_strip_signature_removes_signature_key():
    signed = sign_snapshot(make_snapshot(), SECRET)
    stripped = strip_signature(signed)
    assert "signature" not in stripped


def test_strip_signature_does_not_mutate_original():
    signed = sign_snapshot(make_snapshot(), SECRET)
    strip_signature(signed)
    assert "signature" in signed


def test_strip_signature_is_noop_when_no_signature():
    snap = make_snapshot()
    result = strip_signature(snap)
    assert result == snap
