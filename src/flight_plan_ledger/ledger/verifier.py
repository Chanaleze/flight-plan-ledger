"""Independent verification of ledger entries."""

from __future__ import annotations

from typing import List, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from flight_plan_ledger.crypto.keys import verify
from flight_plan_ledger.models.canonical import FlightPlanCanonicalV1
from flight_plan_ledger.models.ledger_entry import LedgerEntry
from flight_plan_ledger.ledger.store import LedgerStore


class VerificationResult:
    def __init__(
        self,
        found: bool,
        entries: List[LedgerEntry],
        signature_valid: Optional[bool] = None,
        chain_valid: Optional[bool] = None,
        message: str = "",
    ):
        self.found = found
        self.entries = entries
        self.signature_valid = signature_valid
        self.chain_valid = chain_valid
        self.message = message

    def __repr__(self) -> str:
        return (
            f"VerificationResult(found={self.found}, "
            f"signature_valid={self.signature_valid}, "
            f"chain_valid={self.chain_valid}, "
            f"entries={len(self.entries)}, message={self.message!r})"
        )


class Verifier:
    def __init__(self, store: LedgerStore, public_keys: dict[str, Ed25519PublicKey]):
        """
        public_keys: mapping of key_id → public key
        """
        self.store = store
        self.public_keys = public_keys

    def verify_plan(self, plan: FlightPlanCanonicalV1) -> VerificationResult:
        plan_hash = plan.content_hash()
        entries = self.store.get_by_plan_hash(plan_hash)

        if not entries:
            return VerificationResult(
                found=False,
                entries=[],
                message=f"No ledger entry found for plan_hash={plan_hash}",
            )

        # Verify signatures on the matching entries
        all_sigs_ok = True
        for entry in entries:
            if entry.signature is None:
                all_sigs_ok = False
                continue
            pub = self.public_keys.get(entry.signature.key_id)
            if pub is None:
                all_sigs_ok = False
                continue
            ok = verify(pub, entry.content_for_signing(), entry.signature.value)
            if not ok:
                all_sigs_ok = False

        return VerificationResult(
            found=True,
            entries=entries,
            signature_valid=all_sigs_ok,
            message=f"Found {len(entries)} entry(ies) for this plan",
        )

    def verify_chain(self) -> Tuple[bool, str]:
        """
        Walk the entire chain and check that previous_entry_hash links are correct.
        """
        entries = self.store.get_all()
        if not entries:
            return True, "Empty ledger - chain is trivially valid"

        for i, entry in enumerate(entries):
            if i == 0:
                if entry.previous_entry_hash is not None:
                    return False, "Genesis entry must have previous_entry_hash=None"
                continue

            expected_prev = entries[i - 1].entry_hash()
            if entry.previous_entry_hash != expected_prev:
                return (
                    False,
                    f"Chain break at sequence={entry.sequence}: "
                    f"expected previous {expected_prev}, got {entry.previous_entry_hash}",
                )

        return True, f"Chain valid - {len(entries)} entries"
