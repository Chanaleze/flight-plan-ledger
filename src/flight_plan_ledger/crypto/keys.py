"""Ed25519 key generation, signing and verification."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def generate_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def serialize_private_key(private_key: Ed25519PrivateKey) -> bytes:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def serialize_public_key(public_key: Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def load_private_key(pem: bytes) -> Ed25519PrivateKey:
    return serialization.load_pem_private_key(pem, password=None)


def load_public_key(pem: bytes) -> Ed25519PublicKey:
    return serialization.load_pem_public_key(pem)


def sign(private_key: Ed25519PrivateKey, data: bytes) -> str:
    signature = private_key.sign(data)
    return base64.b64encode(signature).decode("ascii")


def verify(public_key: Ed25519PublicKey, data: bytes, signature_b64: str) -> bool:
    try:
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, data)
        return True
    except Exception:
        return False


def save_keypair(
    private_key: Ed25519PrivateKey,
    public_key: Ed25519PublicKey,
    private_path: Path,
    public_path: Path,
) -> None:
    private_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(serialize_private_key(private_key))
    public_path.write_bytes(serialize_public_key(public_key))
    # Restrict permissions on private key
    private_path.chmod(0o600)


def load_keypair(private_path: Path, public_path: Path) -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    private_key = load_private_key(private_path.read_bytes())
    public_key = load_public_key(public_path.read_bytes())
    return private_key, public_key
