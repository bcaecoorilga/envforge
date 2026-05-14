"""Wire encryption subcommands into the main CLI parser.

Import and call ``register(subparsers)`` from the main ``cli.py`` entry point
to make ``envforge encrypt`` and ``envforge decrypt`` available.
"""

from __future__ import annotations

import argparse

from envforge.cli_encrypt import add_encrypt_subcommand


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register encryption subcommands with the provided subparser group.

    Adds the following subcommands to the CLI:

    - ``encrypt``: Encrypt a ``.env`` file or individual values using a
      symmetric key.  The encrypted output can be safely committed to
      version control.
    - ``decrypt``: Decrypt a previously encrypted file, restoring the
      original plaintext ``.env`` contents.

    Args:
        subparsers: The subparser action group returned by
            ``ArgumentParser.add_subparsers()``.  Both commands are
            registered directly onto this group.
    """
    add_encrypt_subcommand(subparsers)
