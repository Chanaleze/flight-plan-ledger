"""LedgerEntry data model."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class EntryStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    AMENDED = "AMENDED"
    CANCELLED = "CANCELLED"


class Signature(BaseModel):
    alg: str = "Ed25519"
    key_id: str
    value: str  # base64


class LedgerEntry(BaseModel):
    """
    Minimal on-ledger record.
    Full flight plan stays off-ledger; only its hash appears here.
    """

    entry_id: str = Field(default_factory=lambda: str(uuid4()))
    sequence: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    submitter_id: str  # e.g. "org:qatar-airways" or "org:nats"
    plan_hash: str  # "sha256:..."
    plan_hash_alg: str = "sha256"
    status: EntryStatus
    previous_entry_hash: Optional[str] = None  # None for genesis
    metadata: dict[str, Any] = Field(default_factory=dict)
    signature: Optional[Signature] = None

    # Optional link for amendments / cancellations
    replaces_entry_id: Optional[str] = None

    def content_for_signing(self) -> bytes:
        """
        Deterministic bytes that are actually signed.
        Signature itself is excluded.
        """
        import json

        data = self.model_dump(mode="json", exclude={"signature"})
        return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")

    def entry_hash(self) -> str:
        """Hash of this entry (used as previous_entry_hash for the next one)."""
        import hashlib
        import json

        # Include the signature once it is present
        data = self.model_dump(mode="json")
        raw = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
        return f"sha256:{hashlib.sha256(raw).hexdigest()}"
