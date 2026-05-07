"""Watch for environment variable changes between two points in time."""

import os
import time
from typing import Callable, Optional

from envforge.snapshot import capture
from envforge.diff import diff_snapshots, has_differences, format_diff


class WatchError(Exception):
    """Raised when watch operations fail."""


def take_baseline(label: str = "watch-baseline", env: Optional[dict] = None) -> dict:
    """Capture a baseline snapshot to watch against."""
    source = env if env is not None else dict(os.environ)
    return capture(source, label=label)


def poll_once(baseline: dict, env: Optional[dict] = None) -> dict:
    """Compare current environment against baseline and return diff result."""
    if not isinstance(baseline, dict) or "variables" not in baseline:
        raise WatchError("baseline must be a valid snapshot dict")
    current_env = env if env is not None else dict(os.environ)
    current = capture(current_env, label="watch-current")
    return diff_snapshots(baseline, current)


def watch(
    interval: float = 2.0,
    label: str = "watch-baseline",
    on_change: Optional[Callable[[dict], None]] = None,
    max_iterations: Optional[int] = None,
    env_provider: Optional[Callable[[], dict]] = None,
) -> None:
    """Poll the environment at a fixed interval and invoke callback on changes.

    Args:
        interval: Seconds between polls.
        label: Label for the baseline snapshot.
        on_change: Callable invoked with the diff dict whenever changes are detected.
        max_iterations: Stop after this many iterations (None = run forever).
        env_provider: Optional callable returning the current env dict (defaults to os.environ).
    """
    if interval <= 0:
        raise WatchError("interval must be a positive number")

    get_env = env_provider if env_provider is not None else lambda: dict(os.environ)
    baseline = take_baseline(label=label, env=get_env())
    iterations = 0

    while max_iterations is None or iterations < max_iterations:
        time.sleep(interval)
        diff = poll_once(baseline, env=get_env())
        if has_differences(diff):
            if on_change is not None:
                on_change(diff)
            baseline = take_baseline(label=label, env=get_env())
        iterations += 1


def format_watch_event(diff: dict) -> str:
    """Format a diff dict into a human-readable watch event string."""
    lines = ["[envforge:watch] Environment change detected:", format_diff(diff)]
    return "\n".join(lines)
