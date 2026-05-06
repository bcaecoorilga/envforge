"""Wire encryption subcommands into the main CLI parser.

Import and call ``register(subparsers)`` from the main ``cli.py`` entry point
to make ``envforge encrypt`` and ``envforge decrypt`` available.
"""

from __future__ import annotations

import argparse

from envforge.cli_encrypt import add_encrypt_subcommand


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register encryption subcommands with the provided subparser group."""
    add_encrypt_subcommand(subparsers)
