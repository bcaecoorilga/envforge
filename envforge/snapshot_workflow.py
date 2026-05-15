"""Workflow support: define ordered sequences of snapshot operations."""

from __future__ import annotations

import json
import os
from typing import Any

WORKFLOW_SCHEMA_VERSION = 1


class WorkflowError(Exception):
    """Raised when a workflow operation fails."""


def _load_workflows(workflow_file: str) -> dict:
    if not os.path.exists(workflow_file):
        return {}
    with open(workflow_file, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_workflows(workflow_file: str, data: dict) -> None:
    with open(workflow_file, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def create_workflow(name: str, steps: list[str], workflow_file: str, description: str = "") -> dict:
    """Create a named workflow with an ordered list of step labels."""
    if not name or not name.strip():
        raise WorkflowError("Workflow name must not be empty.")
    if not steps:
        raise WorkflowError("Workflow must have at least one step.")

    data = _load_workflows(workflow_file)
    if name in data:
        raise WorkflowError(f"Workflow '{name}' already exists.")

    entry = {
        "name": name,
        "description": description,
        "steps": list(steps),
        "schema_version": WORKFLOW_SCHEMA_VERSION,
    }
    data[name] = entry
    _save_workflows(workflow_file, data)
    return entry


def get_workflow(name: str, workflow_file: str) -> dict:
    """Retrieve a workflow by name."""
    data = _load_workflows(workflow_file)
    if name not in data:
        raise WorkflowError(f"Workflow '{name}' not found.")
    return data[name]


def delete_workflow(name: str, workflow_file: str) -> None:
    """Delete a workflow by name."""
    data = _load_workflows(workflow_file)
    if name not in data:
        raise WorkflowError(f"Workflow '{name}' not found.")
    del data[name]
    _save_workflows(workflow_file, data)


def list_workflows(workflow_file: str) -> list[dict]:
    """Return all defined workflows."""
    data = _load_workflows(workflow_file)
    return list(data.values())


def append_step(name: str, step: str, workflow_file: str) -> dict:
    """Append a step label to an existing workflow."""
    data = _load_workflows(workflow_file)
    if name not in data:
        raise WorkflowError(f"Workflow '{name}' not found.")
    if not step or not step.strip():
        raise WorkflowError("Step label must not be empty.")
    data[name]["steps"].append(step)
    _save_workflows(workflow_file, data)
    return data[name]
