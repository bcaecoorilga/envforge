"""Access control for snapshots — grant, revoke, and check access by role."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

ACCESS_FILE_DEFAULT = ".envforge_access.json"
VALID_ROLES = {"read", "write", "admin"}


class AccessError(Exception):
    """Raised when an access control operation fails."""


def _load_access(access_file: str) -> Dict:
    path = Path(access_file)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_access(data: Dict, access_file: str) -> None:
    with open(access_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def grant_access(
    label: str,
    principal: str,
    role: str,
    access_file: str = ACCESS_FILE_DEFAULT,
) -> Dict:
    """Grant *principal* the given *role* on snapshot *label*."""
    if not label:
        raise AccessError("label must not be empty")
    if not principal:
        raise AccessError("principal must not be empty")
    if role not in VALID_ROLES:
        raise AccessError(f"role must be one of {sorted(VALID_ROLES)}, got {role!r}")

    data = _load_access(access_file)
    entry = data.setdefault(label, {})
    entry[principal] = role
    _save_access(data, access_file)
    return {"label": label, "principal": principal, "role": role}


def revoke_access(
    label: str,
    principal: str,
    access_file: str = ACCESS_FILE_DEFAULT,
) -> bool:
    """Revoke *principal*'s access on snapshot *label*. Returns True if removed."""
    if not label:
        raise AccessError("label must not be empty")
    if not principal:
        raise AccessError("principal must not be empty")

    data = _load_access(access_file)
    if label not in data or principal not in data[label]:
        return False
    del data[label][principal]
    if not data[label]:
        del data[label]
    _save_access(data, access_file)
    return True


def get_access(
    label: str,
    access_file: str = ACCESS_FILE_DEFAULT,
) -> Dict[str, str]:
    """Return mapping of principal -> role for snapshot *label*."""
    if not label:
        raise AccessError("label must not be empty")
    data = _load_access(access_file)
    return dict(data.get(label, {}))


def check_access(
    label: str,
    principal: str,
    required_role: str,
    access_file: str = ACCESS_FILE_DEFAULT,
) -> bool:
    """Return True if *principal* holds at least *required_role* on *label*."""
    role_rank = {"read": 0, "write": 1, "admin": 2}
    if required_role not in role_rank:
        raise AccessError(f"unknown required_role {required_role!r}")
    grants = get_access(label, access_file)
    actual = grants.get(principal)
    if actual is None:
        return False
    return role_rank.get(actual, -1) >= role_rank[required_role]


def list_principals(
    access_file: str = ACCESS_FILE_DEFAULT,
) -> List[str]:
    """Return sorted list of all principals across all snapshots."""
    data = _load_access(access_file)
    principals: set = set()
    for roles in data.values():
        principals.update(roles.keys())
    return sorted(principals)
