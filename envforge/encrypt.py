"""Encryption support for snapshots using symmetric key encryption."""

import base64
import hashlib
import json
import os
from typing import Dict, Any

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore


class EncryptError(Exception):
    """Raised when encryption or decryption fails."""


def _require_cryptography() -> None:
    if Fernet is None:
        raise EncryptError(
            "cryptography package is required: pip install cryptography"
        )


def derive_key(passphrase: str) -> bytes:
    """Derive a Fernet-compatible key from a passphrase."""
    _require_cryptography()
    digest = hashlib.sha256(passphrase.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_snapshot(snapshot: Dict[str, Any], passphrase: str) -> Dict[str, Any]:
    """Return a new snapshot dict with variables encrypted.

    The returned dict has an ``encrypted`` flag and a ``ciphertext`` field
    instead of the plain ``variables`` mapping.
    """
    _require_cryptography()
    if snapshot.get("encrypted"):
        raise EncryptError("Snapshot is already encrypted.")

    key = derive_key(passphrase)
    f = Fernet(key)
    plaintext = json.dumps(snapshot["variables"]).encode()
    ciphertext = f.encrypt(plaintext).decode()

    result = {k: v for k, v in snapshot.items() if k != "variables"}
    result["encrypted"] = True
    result["ciphertext"] = ciphertext
    return result


def decrypt_snapshot(snapshot: Dict[str, Any], passphrase: str) -> Dict[str, Any]:
    """Return a snapshot dict with variables decrypted from ciphertext."""
    _require_cryptography()
    if not snapshot.get("encrypted"):
        raise EncryptError("Snapshot is not encrypted.")

    key = derive_key(passphrase)
    f = Fernet(key)
    try:
        plaintext = f.decrypt(snapshot["ciphertext"].encode())
    except InvalidToken as exc:
        raise EncryptError("Decryption failed: invalid passphrase or corrupted data.") from exc

    variables = json.loads(plaintext.decode())
    result = {k: v for k, v in snapshot.items() if k not in ("encrypted", "ciphertext")}
    result["variables"] = variables
    result["encrypted"] = False
    return result


def is_encrypted(snapshot: Dict[str, Any]) -> bool:
    """Return True if the snapshot has been encrypted."""
    return bool(snapshot.get("encrypted"))
