"""Snapshot versioning: assign and manage semantic version strings for snapshots."""

import json
import re
from pathlib import Path

VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+$')


class VersionError(Exception):
    """Raised when a versioning operation fails."""


def _load_versions(version_file: str) -> dict:
    path = Path(version_file)
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def _save_versions(version_file: str, data: dict) -> None:
    with open(version_file, "w") as f:
        json.dump(data, f, indent=2)


def set_version(label: str, version: str, version_file: str) -> dict:
    """Assign a semantic version string to a snapshot label."""
    if not label or not label.strip():
        raise VersionError("Snapshot label must not be empty.")
    if not VERSION_PATTERN.match(version):
        raise VersionError(
            f"Invalid version '{version}'. Expected format: MAJOR.MINOR.PATCH"
        )
    versions = _load_versions(version_file)
    versions[label] = version
    _save_versions(version_file, versions)
    return {"label": label, "version": version}


def get_version(label: str, version_file: str) -> str | None:
    """Retrieve the version string assigned to a snapshot label."""
    if not label or not label.strip():
        raise VersionError("Snapshot label must not be empty.")
    versions = _load_versions(version_file)
    return versions.get(label)


def remove_version(label: str, version_file: str) -> bool:
    """Remove the version entry for a snapshot label. Returns True if removed."""
    if not label or not label.strip():
        raise VersionError("Snapshot label must not be empty.")
    versions = _load_versions(version_file)
    if label not in versions:
        return False
    del versions[label]
    _save_versions(version_file, versions)
    return True


def list_versions(version_file: str) -> list[dict]:
    """Return all label-version pairs as a sorted list of dicts."""
    versions = _load_versions(version_file)
    return [
        {"label": label, "version": ver}
        for label, ver in sorted(versions.items())
    ]


def bump_version(label: str, part: str, version_file: str) -> dict:
    """Increment major, minor, or patch component of an existing version."""
    if part not in ("major", "minor", "patch"):
        raise VersionError("part must be one of: major, minor, patch")
    current = get_version(label, version_file)
    if current is None:
        raise VersionError(f"No version found for label '{label}'.")
    major, minor, patch = map(int, current.split("."))
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    new_version = f"{major}.{minor}.{patch}"
    return set_version(label, new_version, version_file)
