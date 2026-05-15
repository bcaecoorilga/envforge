"""Tests for envforge.snapshot_workflow."""

import json
import pytest

from envforge.snapshot_workflow import (
    WorkflowError,
    create_workflow,
    get_workflow,
    delete_workflow,
    list_workflows,
    append_step,
)


@pytest.fixture
def workflow_file(tmp_path):
    return str(tmp_path / "workflows.json")


def test_create_workflow_creates_entry(workflow_file):
    entry = create_workflow("deploy", ["dev", "staging", "prod"], workflow_file)
    assert entry["name"] == "deploy"


def test_create_workflow_persists_to_file(workflow_file):
    create_workflow("deploy", ["dev", "prod"], workflow_file)
    with open(workflow_file) as fh:
        data = json.load(fh)
    assert "deploy" in data


def test_create_workflow_stores_steps(workflow_file):
    create_workflow("pipe", ["alpha", "beta"], workflow_file)
    entry = get_workflow("pipe", workflow_file)
    assert entry["steps"] == ["alpha", "beta"]


def test_create_workflow_stores_description(workflow_file):
    create_workflow("pipe", ["alpha"], workflow_file, description="main pipeline")
    entry = get_workflow("pipe", workflow_file)
    assert entry["description"] == "main pipeline"


def test_create_workflow_raises_on_empty_name(workflow_file):
    with pytest.raises(WorkflowError, match="name"):
        create_workflow("", ["dev"], workflow_file)


def test_create_workflow_raises_on_empty_steps(workflow_file):
    with pytest.raises(WorkflowError, match="step"):
        create_workflow("empty", [], workflow_file)


def test_create_workflow_raises_on_duplicate(workflow_file):
    create_workflow("deploy", ["dev"], workflow_file)
    with pytest.raises(WorkflowError, match="already exists"):
        create_workflow("deploy", ["prod"], workflow_file)


def test_get_workflow_raises_on_missing(workflow_file):
    with pytest.raises(WorkflowError, match="not found"):
        get_workflow("nonexistent", workflow_file)


def test_delete_workflow_removes_entry(workflow_file):
    create_workflow("temp", ["dev"], workflow_file)
    delete_workflow("temp", workflow_file)
    with pytest.raises(WorkflowError):
        get_workflow("temp", workflow_file)


def test_delete_workflow_raises_on_missing(workflow_file):
    with pytest.raises(WorkflowError, match="not found"):
        delete_workflow("ghost", workflow_file)


def test_list_workflows_returns_all(workflow_file):
    create_workflow("a", ["x"], workflow_file)
    create_workflow("b", ["y"], workflow_file)
    workflows = list_workflows(workflow_file)
    names = [w["name"] for w in workflows]
    assert "a" in names and "b" in names


def test_list_workflows_empty_file(workflow_file):
    result = list_workflows(workflow_file)
    assert result == []


def test_append_step_adds_step(workflow_file):
    create_workflow("pipe", ["dev"], workflow_file)
    updated = append_step("pipe", "prod", workflow_file)
    assert "prod" in updated["steps"]


def test_append_step_preserves_existing_steps(workflow_file):
    create_workflow("pipe", ["dev", "staging"], workflow_file)
    updated = append_step("pipe", "prod", workflow_file)
    assert updated["steps"] == ["dev", "staging", "prod"]


def test_append_step_raises_on_empty_step(workflow_file):
    create_workflow("pipe", ["dev"], workflow_file)
    with pytest.raises(WorkflowError, match="empty"):
        append_step("pipe", "", workflow_file)


def test_append_step_raises_on_missing_workflow(workflow_file):
    with pytest.raises(WorkflowError, match="not found"):
        append_step("ghost", "prod", workflow_file)
