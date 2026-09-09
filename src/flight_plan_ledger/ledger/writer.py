"""Ledger Writer – creates, signs and appends entries."""

from __future__ import annotations

from typing import Any, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from flight_plan_ledger.crypto.keys import sign
from flight_plan_ledger.models.canonical import FlightPlanCanonicalV1
from flight_plan_ledger.models.ledger_entry import EntryStatus, LedgerEntry, Signature
from flight_plan_ledger.ledger.store import LedgerStore


class LedgerWriter:
    def __init__(
        self,
        store: LedgerStore,
        private_key: Ed25519PrivateKey,
        key_id: str,
        submitter_id: str,
    ):
        self.store = store
        self.private_key = private_key
        self.key_id = key_id
        self.submitter_id = submitter_id

    def record(
        self,
        plan: FlightPlanCanonicalV1,
        status: EntryStatus,
        metadata: Optional[dict[str, Any]] = None,
        replaces_entry_id: Optional[str] = None,
    ) -> LedgerEntry:
        """
        Create a signed ledger entry for the given flight plan + decision.
        """
        plan_hash = plan.content_hash()
        sequence = self.store.next_sequence()
        previous_hash = self.store.previous_entry_hash()

        # Build rich but still minimal metadata
        meta = {
            "origin": plan.origin,
            "destination": plan.destination,
            "aircraft_id": plan.aircraft_id,
            "callsign": plan.callsign,
            "dof": plan.dof.isoformat(),
        }
        if metadata:
            meta.update(metadata)

        entry = LedgerEntry(
            sequence=sequence,
            submitter_id=self.submitter_id,
            plan_hash=plan_hash,
            status=status,
            previous_entry_hash=previous_hash,
            metadata=meta,
            replaces_entry_id=replaces_entry_id,
        )

        # Sign the entry content
        signature_value = sign(self.private_key, entry.content_for_signing())
        entry.signature = Signature(
            alg="Ed25519",
            key_id=self.key_id,
            value=signature_value,
        )

        self.store.append(entry)
        return entry
