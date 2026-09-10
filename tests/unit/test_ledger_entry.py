"""Unit tests for LedgerEntry model."""

from __future__ import annotations

from flight_plan_ledger.models.ledger_entry import EntryStatus, LedgerEntry


def _entry(**overrides):
    data = {
        "sequence": 1,
        "submitter_id": "org:nats",
        "plan_hash": "sha256:abc123",
        "status": EntryStatus.ACCEPTED,
    }
    data.update(overrides)
    return LedgerEntry(**data)


def test_defaults():
    e = _entry()
    assert e.entry_id  # uuid generated
    assert e.timestamp is not None
    assert e.previous_entry_hash is None
    assert e.metadata == {}
    assert e.signature is None
    assert e.replaces_entry_id is None


def test_content_for_signing_excludes_signature(keypair, key_id):
    from flight_plan_ledger.crypto.keys import sign as _sign
    from flight_plan_ledger.models.ledger_entry import Signature

    priv, _ = keypair
    e = _entry(sequence=5)
    before = e.content_for_signing()
    e.signature = Signature(alg="Ed25519", key_id=key_id, value=_sign(priv, before))
    after = e.content_for_signing()
    assert before == after  # signing must be stable w.r.t. signature field


def test_entry_hash_changes_once_signed(keypair, key_id):
    from flight_plan_ledger.crypto.keys import sign as _sign
    from flight_plan_ledger.models.ledger_entry import Signature

    priv, _ = keypair
    e = _entry()
    h_unsigned = e.entry_hash()
    e.signature = Signature(
        alg="Ed25519", key_id=key_id, value=_sign(priv, e.content_for_signing())
    )
    assert e.entry_hash() != h_unsigned


def test_entry_hash_deterministic():
    e1 = _entry(entry_id="fixed-id", sequence=2)
    e2 = _entry(entry_id="fixed-id", sequence=2)
    # timestamps default to now -> force equal for determinism check
    e2.timestamp = e1.timestamp
    assert e1.entry_hash() == e2.entry_hash()


def test_all_statuses_accepted():
    for status in EntryStatus:
        e = _entry(status=status)
        assert e.status == status
