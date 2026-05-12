"""Tests for envforge.snapshot_chain."""

import json
import os
import pytest

from envforge.snapshot_chain import (
    ChainError,
    link_snapshot,
    get_parent,
    get_lineage,
    list_children,
)


def make_snapshot(label: str) -> dict:
    return {"label": label, "variables": {"KEY": "val"}}


@pytest.fixture
def chain_file(tmp_path):
    return str(tmp_path / "chain.json")


def test_link_snapshot_creates_entry(chain_file):
    link_snapshot(make_snapshot("v2"), "v1", chain_file)
    with open(chain_file) as fh:
        data = json.load(fh)
    assert data["v2"]["parent"] == "v1"


def test_link_snapshot_raises_on_empty_parent(chain_file):
    with pytest.raises(ChainError, match="parent_label"):
        link_snapshot(make_snapshot("v2"), "", chain_file)


def test_link_snapshot_raises_on_self_reference(chain_file):
    with pytest.raises(ChainError, match="own parent"):
        link_snapshot(make_snapshot("v1"), "v1", chain_file)


def test_link_snapshot_raises_on_invalid_snapshot(chain_file):
    with pytest.raises(ChainError):
        link_snapshot({"label": "v2"}, "v1", chain_file)


def test_get_parent_returns_parent(chain_file):
    link_snapshot(make_snapshot("v2"), "v1", chain_file)
    assert get_parent("v2", chain_file) == "v1"


def test_get_parent_returns_none_for_root(chain_file):
    assert get_parent("v1", chain_file) is None


def test_get_parent_raises_on_empty_label(chain_file):
    with pytest.raises(ChainError):
        get_parent("", chain_file)


def test_get_lineage_single_root(chain_file):
    assert get_lineage("v1", chain_file) == ["v1"]


def test_get_lineage_two_levels(chain_file):
    link_snapshot(make_snapshot("v2"), "v1", chain_file)
    assert get_lineage("v2", chain_file) == ["v1", "v2"]


def test_get_lineage_three_levels(chain_file):
    link_snapshot(make_snapshot("v2"), "v1", chain_file)
    link_snapshot(make_snapshot("v3"), "v2", chain_file)
    assert get_lineage("v3", chain_file) == ["v1", "v2", "v3"]


def test_get_lineage_raises_on_empty_label(chain_file):
    with pytest.raises(ChainError):
        get_lineage("", chain_file)


def test_get_lineage_raises_on_cycle(chain_file):
    # Manually create a cycle
    data = {"v1": {"parent": "v2"}, "v2": {"parent": "v1"}}
    with open(chain_file, "w") as fh:
        json.dump(data, fh)
    with pytest.raises(ChainError, match="cycle"):
        get_lineage("v1", chain_file)


def test_list_children_returns_direct_children(chain_file):
    link_snapshot(make_snapshot("v2"), "v1", chain_file)
    link_snapshot(make_snapshot("v3"), "v1", chain_file)
    children = list_children("v1", chain_file)
    assert sorted(children) == ["v2", "v3"]


def test_list_children_empty_when_no_children(chain_file):
    assert list_children("v1", chain_file) == []


def test_list_children_raises_on_empty_parent(chain_file):
    with pytest.raises(ChainError):
        list_children("", chain_file)


def test_link_snapshot_overwrites_existing_parent(chain_file):
    link_snapshot(make_snapshot("v2"), "v1", chain_file)
    link_snapshot(make_snapshot("v2"), "v0", chain_file)
    assert get_parent("v2", chain_file) == "v0"
