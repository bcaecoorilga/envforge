"""Interpolate variable references within snapshot values."""

import re
from typing import Optional

REF_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


class InterpolateError(Exception):
    """Raised when interpolation fails."""


def _validate_snapshot(snapshot: dict) -> None:
    required = {"label", "variables", "checksum", "timestamp"}
    if not isinstance(snapshot, dict) or not required.issubset(snapshot):
        raise InterpolateError("Invalid snapshot structure.")


def interpolate(snapshot: dict, context: Optional[dict] = None, strict: bool = False) -> dict:
    """Return a new snapshot with variable references resolved.

    References like ${VAR} or $VAR within values are replaced with the
    corresponding value from the snapshot's own variables or an optional
    external context dict.  When *strict* is True an unresolved reference
    raises InterpolateError; otherwise the placeholder is left unchanged.
    """
    _validate_snapshot(snapshot)
    variables = snapshot["variables"]
    lookup = {**variables, **(context or {})}

    resolved = {}
    for key, value in variables.items():
        if not isinstance(value, str):
            resolved[key] = value
            continue

        def replace(match: re.Match) -> str:
            ref = match.group(1) or match.group(2)
            if ref in lookup:
                return lookup[ref]
            if strict:
                raise InterpolateError(f"Unresolved reference '${ref}' in key '{key}'.")
            return match.group(0)

        resolved[key] = REF_PATTERN.sub(replace, value)

    return {**snapshot, "variables": resolved}


def list_references(snapshot: dict) -> dict:
    """Return a mapping of key -> list of variable names it references."""
    _validate_snapshot(snapshot)
    result = {}
    for key, value in snapshot["variables"].items():
        if not isinstance(value, str):
            continue
        refs = [m.group(1) or m.group(2) for m in REF_PATTERN.finditer(value)]
        if refs:
            result[key] = refs
    return result


def has_unresolved(snapshot: dict, context: Optional[dict] = None) -> bool:
    """Return True if any value contains an unresolved reference."""
    _validate_snapshot(snapshot)
    lookup = {**snapshot["variables"], **(context or {})}
    for value in snapshot["variables"].values():
        if not isinstance(value, str):
            continue
        for match in REF_PATTERN.finditer(value):
            ref = match.group(1) or match.group(2)
            if ref not in lookup:
                return True
    return False
