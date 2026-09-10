"""Unit tests for hashing helpers."""

from __future__ import annotations

import hashlib

from flight_plan_ledger.crypto.hashing import sha256_hex, sha256_prefixed


def test_sha256_hex_known_vector():
    assert sha256_hex(b"abc") == hashlib.sha256(b"abc").hexdigest()
    assert sha256_hex(b"") == hashlib.sha256(b"").hexdigest()


def test_sha256_prefixed_format():
    out = sha256_prefixed(b"hello")
    assert out.startswith("sha256:")
    assert out == f"sha256:{hashlib.sha256(b'hello').hexdigest()}"
