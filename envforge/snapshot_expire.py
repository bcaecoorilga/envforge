"""Snapshot expiry: set, check, and clear expiration dates on snapshots."""

import json
import os
from datetime import datetime, timezone
from typing import Optional

EXPIRY_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class ExpireError(Exception):
    """Raised when an expiry operation fails."""


def _load_expiry(expiry_file: str) -> dict:
    if not os.path.exists(expiry_file):
        return {}
    with open(expiry_file, "r") as f:
        return json.load(f)


def _save_expiry(expiry_file: str, data: dict) -> None:
    with open(expiry_file, "w") as f:
        json.dump(data, f, indent=2)


def set_expiry(label: str, expires_at: datetime, expiry_file: str) -> dict:
    """Set an expiration date for a snapshot label."""
    if not label:
        raise ExpireError("Label must not be empty.")
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    data = _load_expiry(expiry_file)
    data[label] = expires_at.strftime(EXPIRY_DATE_FORMAT)
    _save_expiry(expiry_file, data)
    return {"label": label, "expires_at": data[label]}


def get_expiry(label: str, expiry_file: str) -> Optional[datetime]:
    """Return the expiration datetime for a label, or None if not set."""
    if not label:
        raise ExpireError("Label must not be empty.")
    data = _load_expiry(expiry_file)
    raw = data.get(label)
    if raw is None:
        return None
    return datetime.strptime(raw, EXPIRY_DATE_FORMAT).replace(tzinfo=timezone.utc)


def clear_expiry(label: str, expiry_file: str) -> bool:
    """Remove the expiration date for a label. Returns True if removed."""
    if not label:
        raise ExpireError("Label must not be empty.")
    data = _load_expiry(expiry_file)
    if label not in data:
        return False
    del data[label]
    _save_expiry(expiry_file, data)
    return True


def is_expired(label: str, expiry_file: str, now: Optional[datetime] = None) -> bool:
    """Return True if the snapshot has passed its expiry date."""
    expiry = get_expiry(label, expiry_file)
    if expiry is None:
        return False
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now >= expiry


def list_expiry(expiry_file: str) -> list:
    """Return all labels with their expiration dates as a list of dicts."""
    data = _load_expiry(expiry_file)
    return [
        {"label": label, "expires_at": expires_at}
        for label, expires_at in sorted(data.items())
    ]
