"""CLI subcommands for snapshot encryption and decryption."""

import argparse
import json
import sys
from pathlib import Path

from envforge.encrypt import EncryptError, encrypt_snapshot, decrypt_snapshot, is_encrypted


def cmd_encrypt(args: argparse.Namespace) -> None:
    """Encrypt a snapshot file in-place (or to --output)."""
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as fh:
        snapshot = json.load(fh)

    if is_encrypted(snapshot):
        print("Snapshot is already encrypted.", file=sys.stderr)
        sys.exit(1)

    try:
        result = encrypt_snapshot(snapshot, args.passphrase)
    except EncryptError as exc:
        print(f"Encrypt error: {exc}", file=sys.stderr)
        sys.exit(1)

    out = Path(args.output) if args.output else path
    with open(out, "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"Snapshot encrypted -> {out}")


def cmd_decrypt(args: argparse.Namespace) -> None:
    """Decrypt a snapshot file in-place (or to --output)."""
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as fh:
        snapshot = json.load(fh)

    if not is_encrypted(snapshot):
        print("Snapshot is not encrypted.", file=sys.stderr)
        sys.exit(1)

    try:
        result = decrypt_snapshot(snapshot, args.passphrase)
    except EncryptError as exc:
        print(f"Decrypt error: {exc}", file=sys.stderr)
        sys.exit(1)

    out = Path(args.output) if args.output else path
    with open(out, "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"Snapshot decrypted -> {out}")


def add_encrypt_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register 'encrypt' and 'decrypt' subcommands."""
    enc = subparsers.add_parser("encrypt", help="Encrypt a snapshot file")
    enc.add_argument("file", help="Path to snapshot JSON file")
    enc.add_argument("--passphrase", required=True, help="Encryption passphrase")
    enc.add_argument("--output", default=None, help="Output file (default: overwrite input)")
    enc.set_defaults(func=cmd_encrypt)

    dec = subparsers.add_parser("decrypt", help="Decrypt a snapshot file")
    dec.add_argument("file", help="Path to snapshot JSON file")
    dec.add_argument("--passphrase", required=True, help="Decryption passphrase")
    dec.add_argument("--output", default=None, help="Output file (default: overwrite input)")
    dec.set_defaults(func=cmd_decrypt)
