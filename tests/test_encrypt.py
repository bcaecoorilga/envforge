"""Tests for envforge.encrypt module."""

import pytest

pytest.importorskip("cryptography", reason="cryptography package not installed")

from envforge.encrypt import (
    EncryptError,
    derive_key,
    encrypt_snapshot,
    decrypt_snapshot,
    is_encrypted,
)


def make_snapshot(label="test", variables=None):
    return {
        "label": label,
        "timestamp": "2024-01-01T00:00:00",
        "checksum": "abc123",
        "encrypted": False,
        "variables": variables or {"DB_HOST": "localhost", "API_KEY": "secret"},
    }


def test_derive_key_returns_bytes():
    key = derive_key("my-passphrase")
    assert isinstance(key, bytes)
    assert len(key) == 44  # base64-encoded 32-byte key


def test_derive_key_is_deterministic():
    assert derive_key("same") == derive_key("same")


def test_derive_key_differs_for_different_passphrases():
    assert derive_key("one") != derive_key("two")


def test_encrypt_snapshot_sets_encrypted_flag():
    snap = make_snapshot()
    result = encrypt_snapshot(snap, "pass")
    assert result["encrypted"] is True


def test_encrypt_snapshot_removes_variables():
    snap = make_snapshot()
    result = encrypt_snapshot(snap, "pass")
    assert "variables" not in result


def test_encrypt_snapshot_adds_ciphertext():
    snap = make_snapshot()
    result = encrypt_snapshot(snap, "pass")
    assert "ciphertext" in result
    assert isinstance(result["ciphertext"], str)


def test_encrypt_snapshot_preserves_metadata():
    snap = make_snapshot(label="prod")
    result = encrypt_snapshot(snap, "pass")
    assert result["label"] == "prod"
    assert result["timestamp"] == snap["timestamp"]


def test_encrypt_already_encrypted_raises():
    snap = make_snapshot()
    encrypted = encrypt_snapshot(snap, "pass")
    with pytest.raises(EncryptError, match="already encrypted"):
        encrypt_snapshot(encrypted, "pass")


def test_decrypt_snapshot_restores_variables():
    snap = make_snapshot()
    encrypted = encrypt_snapshot(snap, "pass")
    decrypted = decrypt_snapshot(encrypted, "pass")
    assert decrypted["variables"] == snap["variables"]


def test_decrypt_snapshot_clears_encrypted_flag():
    snap = make_snapshot()
    encrypted = encrypt_snapshot(snap, "pass")
    decrypted = decrypt_snapshot(encrypted, "pass")
    assert decrypted["encrypted"] is False


def test_decrypt_wrong_passphrase_raises():
    snap = make_snapshot()
    encrypted = encrypt_snapshot(snap, "correct")
    with pytest.raises(EncryptError, match="Decryption failed"):
        decrypt_snapshot(encrypted, "wrong")


def test_decrypt_non_encrypted_raises():
    snap = make_snapshot()
    with pytest.raises(EncryptError, match="not encrypted"):
        decrypt_snapshot(snap, "pass")


def test_is_encrypted_true():
    snap = make_snapshot()
    encrypted = encrypt_snapshot(snap, "pass")
    assert is_encrypted(encrypted) is True


def test_is_encrypted_false():
    snap = make_snapshot()
    assert is_encrypted(snap) is False


def test_roundtrip_preserves_all_variables():
    variables = {"A": "1", "B": "hello world", "C": "special=chars&here"}
    snap = make_snapshot(variables=variables)
    decrypted = decrypt_snapshot(encrypt_snapshot(snap, "roundtrip"), "roundtrip")
    assert decrypted["variables"] == variables
