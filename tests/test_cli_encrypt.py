"""Tests for envforge.cli_encrypt module."""

import argparse
import json
from pathlib import Path

import pytest

pytest.importorskip("cryptography", reason="cryptography package not installed")

from envforge.cli_encrypt import add_encrypt_subcommand, cmd_encrypt, cmd_decrypt


@pytest.fixture
def parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command")
    add_encrypt_subcommand(sub)
    return p


@pytest.fixture
def snapshot_file(tmp_path):
    snap = {
        "label": "dev",
        "timestamp": "2024-01-01T00:00:00",
        "checksum": "abc",
        "encrypted": False,
        "variables": {"KEY": "value", "SECRET": "s3cr3t"},
    }
    f = tmp_path / "snap.json"
    f.write_text(json.dumps(snap))
    return f


def test_parser_encrypt_subcommand(parser):
    args = parser.parse_args(["encrypt", "snap.json", "--passphrase", "pw"])
    assert args.command == "encrypt"
    assert args.file == "snap.json"
    assert args.passphrase == "pw"


def test_parser_decrypt_subcommand(parser):
    args = parser.parse_args(["decrypt", "snap.json", "--passphrase", "pw"])
    assert args.command == "decrypt"
    assert args.file == "snap.json"


def test_parser_encrypt_output_option(parser):
    args = parser.parse_args(["encrypt", "snap.json", "--passphrase", "pw", "--output", "out.json"])
    assert args.output == "out.json"


def test_cmd_encrypt_writes_encrypted_file(snapshot_file, capsys):
    args = argparse.Namespace(
        file=str(snapshot_file), passphrase="testpass", output=None
    )
    cmd_encrypt(args)
    data = json.loads(snapshot_file.read_text())
    assert data["encrypted"] is True
    assert "ciphertext" in data
    assert "variables" not in data


def test_cmd_encrypt_to_output_file(snapshot_file, tmp_path, capsys):
    out = tmp_path / "encrypted.json"
    args = argparse.Namespace(
        file=str(snapshot_file), passphrase="testpass", output=str(out)
    )
    cmd_encrypt(args)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["encrypted"] is True


def test_cmd_encrypt_missing_file_exits(tmp_path):
    args = argparse.Namespace(
        file=str(tmp_path / "nope.json"), passphrase="pw", output=None
    )
    with pytest.raises(SystemExit) as exc:
        cmd_encrypt(args)
    assert exc.value.code == 1


def test_cmd_encrypt_already_encrypted_exits(snapshot_file):
    args = argparse.Namespace(file=str(snapshot_file), passphrase="pw", output=None)
    cmd_encrypt(args)  # first encrypt
    with pytest.raises(SystemExit) as exc:
        cmd_encrypt(args)  # second should fail
    assert exc.value.code == 1


def test_cmd_decrypt_restores_variables(snapshot_file, capsys):
    enc_args = argparse.Namespace(file=str(snapshot_file), passphrase="pw", output=None)
    cmd_encrypt(enc_args)
    dec_args = argparse.Namespace(file=str(snapshot_file), passphrase="pw", output=None)
    cmd_decrypt(dec_args)
    data = json.loads(snapshot_file.read_text())
    assert data["variables"]["KEY"] == "value"


def test_cmd_decrypt_wrong_passphrase_exits(snapshot_file):
    enc_args = argparse.Namespace(file=str(snapshot_file), passphrase="correct", output=None)
    cmd_encrypt(enc_args)
    dec_args = argparse.Namespace(file=str(snapshot_file), passphrase="wrong", output=None)
    with pytest.raises(SystemExit) as exc:
        cmd_decrypt(dec_args)
    assert exc.value.code == 1


def test_cmd_decrypt_non_encrypted_exits(snapshot_file):
    args = argparse.Namespace(file=str(snapshot_file), passphrase="pw", output=None)
    with pytest.raises(SystemExit) as exc:
        cmd_decrypt(args)
    assert exc.value.code == 1
