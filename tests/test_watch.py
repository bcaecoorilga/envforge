"""Tests for envforge.watch module."""

import pytest
from unittest.mock import patch, MagicMock

from envforge.watch import (
    WatchError,
    take_baseline,
    poll_once,
    watch,
    format_watch_event,
)


BASE_ENV = {"APP_ENV": "dev", "PORT": "8080", "DEBUG": "true"}


def test_take_baseline_returns_snapshot():
    snap = take_baseline(label="test", env=BASE_ENV)
    assert snap["label"] == "test"
    assert "variables" in snap
    assert snap["variables"]["APP_ENV"] == "dev"


def test_take_baseline_default_label():
    snap = take_baseline(env=BASE_ENV)
    assert snap["label"] == "watch-baseline"


def test_poll_once_no_changes():
    baseline = take_baseline(label="b", env=BASE_ENV)
    diff = poll_once(baseline, env=BASE_ENV)
    assert diff["added"] == {}
    assert diff["removed"] == {}
    assert diff["changed"] == {}


def test_poll_once_detects_added_key():
    baseline = take_baseline(label="b", env=BASE_ENV)
    new_env = {**BASE_ENV, "NEW_VAR": "hello"}
    diff = poll_once(baseline, env=new_env)
    assert "NEW_VAR" in diff["added"]


def test_poll_once_detects_removed_key():
    baseline = take_baseline(label="b", env=BASE_ENV)
    new_env = {k: v for k, v in BASE_ENV.items() if k != "DEBUG"}
    diff = poll_once(baseline, env=new_env)
    assert "DEBUG" in diff["removed"]


def test_poll_once_detects_changed_key():
    baseline = take_baseline(label="b", env=BASE_ENV)
    new_env = {**BASE_ENV, "PORT": "9090"}
    diff = poll_once(baseline, env=new_env)
    assert "PORT" in diff["changed"]


def test_poll_once_raises_on_invalid_baseline():
    with pytest.raises(WatchError):
        poll_once({"not": "a snapshot"}, env=BASE_ENV)


def test_watch_calls_on_change_when_env_changes():
    envs = [BASE_ENV, {**BASE_ENV, "NEW_VAR": "x"}]
    call_count = {"n": 0}

    def provider():
        idx = min(call_count["n"], len(envs) - 1)
        call_count["n"] += 1
        return envs[idx]

    received = []

    with patch("time.sleep"):
        watch(
            interval=0.01,
            on_change=received.append,
            max_iterations=2,
            env_provider=provider,
        )

    assert len(received) == 1
    assert "NEW_VAR" in received[0]["added"]


def test_watch_does_not_call_on_change_when_no_diff():
    provider = lambda: dict(BASE_ENV)
    received = []

    with patch("time.sleep"):
        watch(
            interval=0.01,
            on_change=received.append,
            max_iterations=3,
            env_provider=provider,
        )

    assert received == []


def test_watch_raises_on_non_positive_interval():
    with pytest.raises(WatchError):
        watch(interval=0, max_iterations=1, env_provider=lambda: BASE_ENV)


def test_format_watch_event_contains_header():
    baseline = take_baseline(label="b", env=BASE_ENV)
    new_env = {**BASE_ENV, "ADDED": "1"}
    diff = poll_once(baseline, env=new_env)
    output = format_watch_event(diff)
    assert "[envforge:watch]" in output
    assert "ADDED" in output
