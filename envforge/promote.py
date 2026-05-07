"""Promote a snapshot from one environment to another with optional key transformations."""

import copy
import hashlib
import json
from typing import Optional


class PromoteError(Exception):
    """Raised when a promotion operation fails."""


def _validate_snapshot(snapshot: dict) -> None:
    required = {"label", "variables", "checksum", "timestamp"}
    if not isinstance(snapshot, dict):
        raise PromoteError("Snapshot must be a dict")
    missing = required - snapshot.keys()
    if missing:
        raise PromoteError(f"Snapshot missing required keys: {missing}")


def _compute_checksum(variables: dict) -> str:
    serialized = json.dumps(variables, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def promote(
    snapshot: dict,
    target_label: str,
    overrides: Optional[dict] = None,
    exclude_keys: Optional[list] = None,
    add_prefix: Optional[str] = None,
) -> dict:
    """Create a promoted copy of a snapshot for a target environment.

    Args:
        snapshot: Source snapshot dict.
        target_label: Label for the promoted snapshot.
        overrides: Key/value pairs to override or add after promotion.
        exclude_keys: List of variable keys to drop during promotion.
        add_prefix: Optional prefix to prepend to all variable keys.

    Returns:
        A new snapshot dict targeted at the destination environment.
    """
    _validate_snapshot(snapshot)
    if not target_label or not target_label.strip():
        raise PromoteError("target_label must be a non-empty string")

    variables = copy.deepcopy(snapshot["variables"])

    if exclude_keys:
        for key in exclude_keys:
            variables.pop(key, None)

    if add_prefix:
        if not isinstance(add_prefix, str) or not add_prefix:
            raise PromoteError("add_prefix must be a non-empty string")
        variables = {f"{add_prefix}{k}": v for k, v in variables.items()}

    if overrides:
        if not isinstance(overrides, dict):
            raise PromoteError("overrides must be a dict")
        variables.update(overrides)

    import datetime
    promoted = {
        "label": target_label.strip(),
        "variables": variables,
        "checksum": _compute_checksum(variables),
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "promoted_from": snapshot["label"],
    }
    return promoted


def list_promotion_changes(source: dict, promoted: dict) -> dict:
    """Return a summary of what changed between source and promoted snapshot."""
    _validate_snapshot(source)
    _validate_snapshot(promoted)

    src_vars = source["variables"]
    dst_vars = promoted["variables"]

    added = {k: dst_vars[k] for k in dst_vars if k not in src_vars}
    removed = {k: src_vars[k] for k in src_vars if k not in dst_vars}
    overridden = {
        k: {"from": src_vars[k], "to": dst_vars[k]}
        for k in src_vars
        if k in dst_vars and src_vars[k] != dst_vars[k]
    }
    return {"added": added, "removed": removed, "overridden": overridden}
