"""Integration helpers: wire tag CLI into the main envforge parser.

This module is intentionally thin — it re-exports add_tag_subcommand so
the main cli.py can import from a single, stable location.
"""

from envforge.cli_tag import add_tag_subcommand, cmd_tag

__all__ = ["add_tag_subcommand", "cmd_tag"]
