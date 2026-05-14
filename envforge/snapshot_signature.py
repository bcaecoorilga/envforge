"""snapshot_signature.py — Sign and verify snapshots with an HMAC-based signature."""

import hashlib
import hmac
import json
from typing import Any, Dict, Optional


class SignatureError(Exception):
    """Raised when a signature operation fails."""


def _validate_snapshot(snapshot: Any) -> None:
    if not isinstance(snapshot, dict):
        raise SignatureError("Snapshot must be a dict.")
    for key in ("label", "variables", "checksum"):
        if key not in snapshot:
            raise SignatureError(f"Snapshot missing required key: '{key}'")


def _canonical_payload(snapshot: Dict[str, Any]) -> bytes:
    """Produce a stable, canonical bytes representation of the snapshot variables."""
    variables = snapshot.get("variables", {})
    canonical = json.dumps(variables, sort_keys=True, separators=(",", ":"))
    return canonical.encode("utf-8")


def sign_snapshot(snapshot: Dict[str, Any], secret: str) -> Dict[str, Any]:
    """Return a copy of *snapshot* with an HMAC-SHA256 signature attached.

    Args:
        snapshot: A valid envforge snapshot dict.
        secret:   A shared secret / passphrase used to sign.

    Returns:
        New snapshot dict with a ``signature`` key added.
    """
    _validate_snapshot(snapshot)
    if not secret:
        raise SignatureError("Secret must not be empty.")

    payload = _canonical_payload(snapshot)
    sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    result = dict(snapshot)
    result["signature"] = sig
    return result


def verify_signature(snapshot: Dict[str, Any], secret: str) -> bool:
    """Return *True* if the snapshot's signature is valid for *secret*.

    Returns *False* (rather than raising) when the signature is missing or
    does not match, so callers can branch on the result.
    """
    _validate_snapshot(snapshot)
    if not secret:
        raise SignatureError("Secret must not be empty.")

    stored_sig: Optional[str] = snapshot.get("signature")
    if not stored_sig:
        return False

    payload = _canonical_payload(snapshot)
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(stored_sig, expected)


def assert_signature(snapshot: Dict[str, Any], secret: str) -> None:
    """Like :func:`verify_signature` but raises :exc:`SignatureError` on failure."""
    if not verify_signature(snapshot, secret):
        raise SignatureError(
            f"Signature verification failed for snapshot '{snapshot.get('label', '?')}'"
        )


def strip_signature(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Return a copy of *snapshot* with the signature key removed."""
    result = dict(snapshot)
    result.pop("signature", None)
    return result
