"""Import environment variables into a snapshot from external formats."""

import os
import json
import re
from typing import Optional
from envforge.snapshot import capture


class ImportError(Exception):
    """Raised when an import operation fails."""


def _parse_dotenv(content: str) -> dict:
    """Parse a .env file content into a key/value dict."""
    variables = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)', line)
        if not match:
            continue
        key, value = match.group(1), match.group(2)
        # Strip inline comments and surrounding quotes
        value = re.sub(r'\s+#.*$', '', value).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        variables[key] = value
    return variables


def from_dotenv(path: str, label: Optional[str] = None) -> dict:
    """Import a snapshot from a .env file."""
    if not os.path.isfile(path):
        raise ImportError(f"File not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        raise ImportError(f"Cannot read file: {exc}") from exc
    variables = _parse_dotenv(content)
    resolved_label = label or os.path.basename(path)
    return capture(variables, label=resolved_label)


def from_json(path: str, label: Optional[str] = None) -> dict:
    """Import a snapshot from a JSON key/value file."""
    if not os.path.isfile(path):
        raise ImportError(f"File not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise ImportError(f"Cannot parse JSON file: {exc}") from exc
    if not isinstance(data, dict):
        raise ImportError("JSON file must contain a top-level object.")
    variables = {str(k): str(v) for k, v in data.items()}
    resolved_label = label or os.path.basename(path)
    return capture(variables, label=resolved_label)


def from_shell_env(prefix: Optional[str] = None, label: str = "shell-import") -> dict:
    """Import a snapshot from the current shell environment."""
    env = dict(os.environ)
    if prefix:
        env = {k: v for k, v in env.items() if k.startswith(prefix)}
    return capture(env, label=label)
