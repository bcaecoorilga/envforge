"""Tests for envforge.snapshot_access."""

import json
import pytest

from envforge.snapshot_access import (
    AccessError,
    grant_access,
    revoke_access,
    get_access,
    check_access,
    list_principals,
)


@pytest.fixture()
def access_file(tmp_path):
    return str(tmp_path / "access.json")


# --- grant_access ---

def test_grant_access_creates_entry(access_file):
    result = grant_access("prod", "alice", "read", access_file)
    assert result["label"] == "prod"
    assert result["principal"] == "alice"
    assert result["role"] == "read"


def test_grant_access_persists_to_file(access_file):
    grant_access("prod", "alice", "write", access_file)
    data = json.loads(open(access_file).read())
    assert data["prod"]["alice"] == "write"


def test_grant_access_overwrites_existing_role(access_file):
    grant_access("prod", "alice", "read", access_file)
    grant_access("prod", "alice", "admin", access_file)
    assert get_access("prod", access_file)["alice"] == "admin"


def test_grant_access_multiple_principals(access_file):
    grant_access("prod", "alice", "read", access_file)
    grant_access("prod", "bob", "write", access_file)
    grants = get_access("prod", access_file)
    assert grants["alice"] == "read"
    assert grants["bob"] == "write"


def test_grant_access_raises_on_empty_label(access_file):
    with pytest.raises(AccessError, match="label"):
        grant_access("", "alice", "read", access_file)


def test_grant_access_raises_on_empty_principal(access_file):
    with pytest.raises(AccessError, match="principal"):
        grant_access("prod", "", "read", access_file)


def test_grant_access_raises_on_invalid_role(access_file):
    with pytest.raises(AccessError, match="role"):
        grant_access("prod", "alice", "superuser", access_file)


# --- revoke_access ---

def test_revoke_access_removes_entry(access_file):
    grant_access("prod", "alice", "read", access_file)
    removed = revoke_access("prod", "alice", access_file)
    assert removed is True
    assert get_access("prod", access_file) == {}


def test_revoke_access_returns_false_when_not_present(access_file):
    assert revoke_access("prod", "nobody", access_file) is False


def test_revoke_access_cleans_up_empty_label(access_file):
    grant_access("prod", "alice", "read", access_file)
    revoke_access("prod", "alice", access_file)
    data = json.loads(open(access_file).read())
    assert "prod" not in data


def test_revoke_access_raises_on_empty_label(access_file):
    with pytest.raises(AccessError):
        revoke_access("", "alice", access_file)


# --- check_access ---

def test_check_access_returns_true_for_sufficient_role(access_file):
    grant_access("prod", "alice", "write", access_file)
    assert check_access("prod", "alice", "read", access_file) is True
    assert check_access("prod", "alice", "write", access_file) is True


def test_check_access_returns_false_for_insufficient_role(access_file):
    grant_access("prod", "alice", "read", access_file)
    assert check_access("prod", "alice", "write", access_file) is False


def test_check_access_returns_false_for_unknown_principal(access_file):
    assert check_access("prod", "ghost", "read", access_file) is False


def test_check_access_admin_passes_all_levels(access_file):
    grant_access("prod", "alice", "admin", access_file)
    for role in ("read", "write", "admin"):
        assert check_access("prod", "alice", role, access_file) is True


# --- list_principals ---

def test_list_principals_returns_all_unique(access_file):
    grant_access("prod", "alice", "read", access_file)
    grant_access("staging", "bob", "write", access_file)
    grant_access("dev", "alice", "admin", access_file)
    principals = list_principals(access_file)
    assert principals == ["alice", "bob"]


def test_list_principals_empty_when_no_grants(access_file):
    assert list_principals(access_file) == []
