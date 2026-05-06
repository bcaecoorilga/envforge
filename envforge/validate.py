"""Snapshot validation and schema enforcement for envforge."""

import re
from typing import Any

REQUIRED_KEYS = {"label", "variables", "checksum", "timestamp"}
VALID_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class ValidationError(Exception):
    """Raised when a snapshot fails validation."""


def validate_snapshot(snapshot: Any) -> None:
    """Raise ValidationError if the snapshot is structurally invalid."""
    if not isinstance(snapshot, dict):
        raise ValidationError("Snapshot must be a dictionary.")

    missing = REQUIRED_KEYS - snapshot.keys()
    if missing:
        raise ValidationError(f"Snapshot missing required keys: {sorted(missing)}")

    if not isinstance(snapshot["label"], str) or not snapshot["label"].strip():
        raise ValidationError("Snapshot 'label' must be a non-empty string.")

    if not isinstance(snapshot["variables"], dict):
        raise ValidationError("Snapshot 'variables' must be a dictionary.")

    for k, v in snapshot["variables"].items():
        if not isinstance(k, str):
            raise ValidationError(f"Variable key must be a string, got: {type(k).__name__}")
        if not VALID_KEY_PATTERN.match(k):
            raise ValidationError(f"Invalid variable key name: '{k}'")
        if not isinstance(v, str):
            raise ValidationError(f"Variable value for '{k}' must be a string, got: {type(v).__name__}")

    if not isinstance(snapshot["checksum"], str):
        raise ValidationError("Snapshot 'checksum' must be a string.")

    if not isinstance(snapshot["timestamp"], str):
        raise ValidationError("Snapshot 'timestamp' must be a string.")


def validate_variables(variables: Any) -> None:
    """Raise ValidationError if the variables dict is invalid."""
    if not isinstance(variables, dict):
        raise ValidationError("Variables must be a dictionary.")

    for k, v in variables.items():
        if not isinstance(k, str):
            raise ValidationError(f"Variable key must be a string, got: {type(k).__name__}")
        if not VALID_KEY_PATTERN.match(k):
            raise ValidationError(f"Invalid variable key name: '{k}'")
        if not isinstance(v, str):
            raise ValidationError(f"Variable value for '{k}' must be a string, got: {type(v).__name__}")


def is_valid_snapshot(snapshot: Any) -> bool:
    """Return True if snapshot passes validation, False otherwise."""
    try:
        validate_snapshot(snapshot)
        return True
    except ValidationError:
        return False
