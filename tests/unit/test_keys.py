"""Unit tests for Ed25519 key helpers."""

from __future__ import annotations

import os

from flight_plan_ledger.crypto.keys import (
    generate_keypair,
    load_keypair,
    load_private_key,
    load_public_key,
    save_keypair,
    serialize_private_key,
    serialize_public_key,
    sign,
    verify,
)


def test_generate_keypair_types(keypair):
    priv, pub = keypair
    assert serialize_private_key(priv).startswith(b"-----BEGIN PRIVATE KEY-----")
    assert serialize_public_key(pub).startswith(b"-----BEGIN PUBLIC KEY-----")


def test_serialize_roundtrip(keypair):
    priv, pub = keypair
    assert load_private_key(serialize_private_key(priv)) is not None
    assert load_public_key(serialize_public_key(pub)) is not None


def test_sign_verify_roundtrip(keypair):
    priv, pub = keypair
    sig = sign(priv, b"flight-plan-bytes")
    assert verify(pub, b"flight-plan-bytes", sig) is True


def test_verify_rejects_tampered_data(keypair):
    priv, pub = keypair
    sig = sign(priv, b"original")
    assert verify(pub, b"tampered", sig) is False


def test_verify_rejects_wrong_key(keypair):
    priv, _ = keypair
    other_priv, other_pub = generate_keypair()
    del other_priv
    sig = sign(priv, b"data")
    assert verify(other_pub, b"data", sig) is False


def test_verify_rejects_garbage_signature(keypair):
    _, pub = keypair
    assert verify(pub, b"data", "!!!not-base64!!!") is False
    assert verify(pub, b"data", "aGVsbG8=") is False  # valid b64, wrong length


def test_save_and_load_keypair(tmp_path, keypair):
    priv, pub = keypair
    priv_path = tmp_path / "keys" / "w.private.pem"
    pub_path = tmp_path / "keys" / "w.public.pem"
    save_keypair(priv, pub, priv_path, pub_path)
    assert priv_path.exists()
    assert pub_path.exists()
    loaded_priv, loaded_pub = load_keypair(priv_path, pub_path)
    # Loaded keys must be functionally equivalent
    sig = sign(loaded_priv, b"check")
    assert verify(loaded_pub, b"check", sig) is True
    if os.name != "nt":
        assert oct(priv_path.stat().st_mode & 0o777) == "0o600"
