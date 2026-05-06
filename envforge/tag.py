"""Tag and label management for environment snapshots."""

import json
import os
from typing import Dict, List, Optional

TAG_FILE_DEFAULT = ".envforge_tags.json"


class TagError(Exception):
    """Raised when a tagging operation fails."""


def _load_tags(tag_file: str) -> Dict[str, List[str]]:
    """Load tag index from disk. Returns empty dict if file doesn't exist."""
    if not os.path.exists(tag_file):
        return {}
    with open(tag_file, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_tags(tags: Dict[str, List[str]], tag_file: str) -> None:
    """Persist tag index to disk."""
    with open(tag_file, "w", encoding="utf-8") as fh:
        json.dump(tags, fh, indent=2)


def add_tag(snapshot_label: str, tag: str, tag_file: str = TAG_FILE_DEFAULT) -> None:
    """Associate *tag* with *snapshot_label*."""
    if not snapshot_label or not tag:
        raise TagError("snapshot_label and tag must be non-empty strings.")
    tags = _load_tags(tag_file)
    tags.setdefault(snapshot_label, [])
    if tag not in tags[snapshot_label]:
        tags[snapshot_label].append(tag)
    _save_tags(tags, tag_file)


def remove_tag(snapshot_label: str, tag: str, tag_file: str = TAG_FILE_DEFAULT) -> None:
    """Remove *tag* from *snapshot_label*. Silently ignores missing tags."""
    tags = _load_tags(tag_file)
    if snapshot_label in tags and tag in tags[snapshot_label]:
        tags[snapshot_label].remove(tag)
        if not tags[snapshot_label]:
            del tags[snapshot_label]
        _save_tags(tags, tag_file)


def get_tags(snapshot_label: str, tag_file: str = TAG_FILE_DEFAULT) -> List[str]:
    """Return all tags associated with *snapshot_label*."""
    tags = _load_tags(tag_file)
    return list(tags.get(snapshot_label, []))


def find_by_tag(tag: str, tag_file: str = TAG_FILE_DEFAULT) -> List[str]:
    """Return all snapshot labels that carry *tag*."""
    tags = _load_tags(tag_file)
    return [label for label, label_tags in tags.items() if tag in label_tags]


def list_all_tags(tag_file: str = TAG_FILE_DEFAULT) -> Dict[str, List[str]]:
    """Return the full tag index as a dict mapping label -> [tags]."""
    return _load_tags(tag_file)
