"""Snapshot alias management: create and resolve human-friendly aliases for snapshot labels."""

import json
import os
from typing import Dict, List, Optional


class AliasError(Exception):
    pass


def _load_aliases(alias_file: str) -> Dict[str, str]:
    if not os.path.exists(alias_file):
        return {}
    with open(alias_file, "r") as f:
        return json.load(f)


def _save_aliases(alias_file: str, aliases: Dict[str, str]) -> None:
    with open(alias_file, "w") as f:
        json.dump(aliases, f, indent=2)


def add_alias(alias: str, label: str, alias_file: str) -> Dict[str, str]:
    """Map an alias to a snapshot label."""
    if not alias or not alias.strip():
        raise AliasError("Alias must not be empty.")
    if not label or not label.strip():
        raise AliasError("Label must not be empty.")
    aliases = _load_aliases(alias_file)
    if alias in aliases:
        raise AliasError(f"Alias '{alias}' already exists. Use update_alias to change it.")
    aliases[alias] = label
    _save_aliases(alias_file, aliases)
    return aliases


def update_alias(alias: str, label: str, alias_file: str) -> Dict[str, str]:
    """Update an existing alias to point to a new label."""
    if not alias or not alias.strip():
        raise AliasError("Alias must not be empty.")
    aliases = _load_aliases(alias_file)
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' does not exist.")
    aliases[alias] = label
    _save_aliases(alias_file, aliases)
    return aliases


def remove_alias(alias: str, alias_file: str) -> Dict[str, str]:
    """Remove an alias."""
    aliases = _load_aliases(alias_file)
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' not found.")
    del aliases[alias]
    _save_aliases(alias_file, aliases)
    return aliases


def resolve_alias(alias: str, alias_file: str) -> Optional[str]:
    """Return the label for a given alias, or None if not found."""
    aliases = _load_aliases(alias_file)
    return aliases.get(alias)


def list_aliases(alias_file: str) -> List[Dict[str, str]]:
    """Return all aliases as a list of dicts with 'alias' and 'label' keys."""
    aliases = _load_aliases(alias_file)
    return [{"alias": k, "label": v} for k, v in sorted(aliases.items())]
