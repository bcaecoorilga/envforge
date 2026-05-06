"""Redact sensitive environment variable values from snapshots."""

import re
from typing import List, Optional

DEFAULT_PATTERNS = [
    r"(?i)(password|passwd|secret|token|api[_-]?key|private[_-]?key|auth|credential)",
]

REDACTED_PLACEHOLDER = "***REDACTED***"


class RedactError(Exception):
    """Raised when redaction fails."""


def _validate_snapshot(snapshot: dict) -> None:
    required = {"label", "variables", "checksum", "timestamp"}
    if not isinstance(snapshot, dict) or not required.issubset(snapshot):
        raise RedactError("Invalid snapshot structure.")


def redact_by_patterns(
    snapshot: dict,
    patterns: Optional[List[str]] = None,
    placeholder: str = REDACTED_PLACEHOLDER,
) -> dict:
    """Return a copy of the snapshot with matching keys' values replaced."""
    _validate_snapshot(snapshot)
    patterns = patterns if patterns is not None else DEFAULT_PATTERNS
    compiled = [re.compile(p) for p in patterns]

    redacted_vars = {}
    for key, value in snapshot["variables"].items():
        if any(c.search(key) for c in compiled):
            redacted_vars[key] = placeholder
        else:
            redacted_vars[key] = value

    result = dict(snapshot)
    result["variables"] = redacted_vars
    result["redacted"] = True
    return result


def redact_keys(
    snapshot: dict,
    keys: List[str],
    placeholder: str = REDACTED_PLACEHOLDER,
) -> dict:
    """Return a copy of the snapshot with specific keys' values replaced."""
    _validate_snapshot(snapshot)
    if not isinstance(keys, list):
        raise RedactError("keys must be a list of strings.")

    redacted_vars = dict(snapshot["variables"])
    for key in keys:
        if key in redacted_vars:
            redacted_vars[key] = placeholder

    result = dict(snapshot)
    result["variables"] = redacted_vars
    result["redacted"] = True
    return result


def list_sensitive_keys(snapshot: dict, patterns: Optional[List[str]] = None) -> List[str]:
    """Return keys that match sensitive patterns without modifying the snapshot."""
    _validate_snapshot(snapshot)
    patterns = patterns if patterns is not None else DEFAULT_PATTERNS
    compiled = [re.compile(p) for p in patterns]
    return [key for key in snapshot["variables"] if any(c.search(key) for c in compiled)]
