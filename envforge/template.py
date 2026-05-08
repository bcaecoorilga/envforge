"""Template support: generate snapshot stubs from variable name patterns."""
from __future__ import annotations

import re
from typing import Dict, List, Optional


class TemplateError(Exception):
    """Raised when a template operation fails."""


_PLACEHOLDER = "<required>"


def _validate_keys(keys: List[str]) -> None:
    if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
        raise TemplateError("keys must be a list of strings")
    for key in keys:
        if not key.strip():
            raise TemplateError("key names must not be empty or whitespace")


def create_template(
    label: str,
    keys: List[str],
    defaults: Optional[Dict[str, str]] = None,
    placeholder: str = _PLACEHOLDER,
) -> Dict:
    """Build a snapshot template with placeholder values.

    Args:
        label: Name for the template snapshot.
        keys: Variable names to include.
        defaults: Optional mapping of key -> default value.
        placeholder: String used for keys without a default.

    Returns:
        A snapshot-shaped dict with placeholder/default values.
    """
    if not label or not label.strip():
        raise TemplateError("label must not be empty")
    _validate_keys(keys)
    defaults = defaults or {}
    variables = {k: defaults.get(k, placeholder) for k in keys}
    return {
        "label": label,
        "variables": variables,
        "checksum": None,
        "is_template": True,
    }


def fill_template(
    template: Dict,
    values: Dict[str, str],
    allow_missing: bool = False,
) -> Dict:
    """Fill a template snapshot with concrete values.

    Args:
        template: A template dict produced by create_template.
        values: Mapping of key -> concrete value.
        allow_missing: If False, raise when a placeholder is left unfilled.

    Returns:
        A new snapshot dict with all placeholders replaced.
    """
    if not isinstance(template, dict) or not template.get("is_template"):
        raise TemplateError("provided dict is not a template")
    filled: Dict[str, str] = {}
    for key, val in template["variables"].items():
        if key in values:
            filled[key] = values[key]
        elif val == _PLACEHOLDER and not allow_missing:
            raise TemplateError(f"required key '{key}' has no value")
        else:
            filled[key] = val
    import hashlib, json
    checksum = hashlib.sha256(
        json.dumps(filled, sort_keys=True).encode()
    ).hexdigest()
    return {
        "label": template["label"],
        "variables": filled,
        "checksum": checksum,
        "is_template": False,
    }


def list_unfilled(template: Dict) -> List[str]:
    """Return keys that still hold the placeholder value."""
    if not isinstance(template, dict) or not template.get("is_template"):
        raise TemplateError("provided dict is not a template")
    return [
        k for k, v in template["variables"].items() if v == _PLACEHOLDER
    ]
