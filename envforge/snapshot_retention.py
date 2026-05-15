"""Retention policy management for snapshots."""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

RETENTION_FIELDS = {"label", "policy", "max_count", "max_age_days", "created_at"}


class RetentionError(Exception):
    """Raised when a retention policy operation fails."""


def _load_retention(path: str) -> Dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as fh:
        return json.load(fh)


def _save_retention(path: str, data: Dict) -> None:
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def set_retention_policy(
    label: str,
    path: str,
    policy: str = "count",
    max_count: int = 10,
    max_age_days: Optional[int] = None,
) -> Dict:
    """Assign a retention policy to a snapshot label."""
    if not label:
        raise RetentionError("label must not be empty")
    if policy not in ("count", "age", "both"):
        raise RetentionError(f"unknown policy '{policy}'; expected count, age, or both")
    if max_count < 1:
        raise RetentionError("max_count must be at least 1")
    if policy in ("age", "both") and (max_age_days is None or max_age_days < 1):
        raise RetentionError("max_age_days must be a positive integer for age-based policies")

    data = _load_retention(path)
    entry = {
        "label": label,
        "policy": policy,
        "max_count": max_count,
        "max_age_days": max_age_days,
        "created_at": datetime.utcnow().isoformat(),
    }
    data[label] = entry
    _save_retention(path, data)
    return entry


def get_retention_policy(label: str, path: str) -> Optional[Dict]:
    """Return the retention policy for a label, or None if not set."""
    if not label:
        raise RetentionError("label must not be empty")
    data = _load_retention(path)
    return data.get(label)


def remove_retention_policy(label: str, path: str) -> bool:
    """Remove the retention policy for a label. Returns True if removed."""
    if not label:
        raise RetentionError("label must not be empty")
    data = _load_retention(path)
    if label not in data:
        return False
    del data[label]
    _save_retention(path, data)
    return True


def list_retention_policies(path: str) -> List[Dict]:
    """Return all retention policies sorted by label."""
    data = _load_retention(path)
    return sorted(data.values(), key=lambda e: e["label"])


def evaluate_retention(label: str, history: List[Dict], path: str) -> List[str]:
    """Return labels from history that should be pruned based on the policy.

    Each entry in *history* must have at least ``label`` and ``captured_at`` keys.
    Returns a list of snapshot labels that exceed the policy limits.
    """
    policy_entry = get_retention_policy(label, path)
    if not policy_entry:
        return []

    prunable: List[str] = []
    policy = policy_entry["policy"]

    sorted_history = sorted(history, key=lambda e: e.get("captured_at", ""))

    if policy in ("count", "both"):
        max_count = policy_entry["max_count"]
        if len(sorted_history) > max_count:
            excess = sorted_history[: len(sorted_history) - max_count]
            prunable.extend(e["label"] for e in excess)

    if policy in ("age", "both"):
        max_age_days = policy_entry.get("max_age_days")
        if max_age_days:
            cutoff = datetime.utcnow() - timedelta(days=max_age_days)
            for entry in sorted_history:
                if entry["label"] in prunable:
                    continue
                try:
                    captured = datetime.fromisoformat(entry["captured_at"])
                    if captured < cutoff:
                        prunable.append(entry["label"])
                except (ValueError, KeyError):
                    pass

    return list(dict.fromkeys(prunable))
