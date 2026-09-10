"""Unit tests for LedgerWriter."""

from __future__ import annotations

from flight_plan_ledger.crypto.keys import verify
from flight_plan_ledger.models.ledger_entry import EntryStatus


def test_record_first_entry_is_genesis(writer, sample_plan, keypair, key_id):
    _, pub = keypair
    entry = writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    assert entry.sequence == 1
    assert entry.previous_entry_hash is None
    assert entry.plan_hash == sample_plan.content_hash()
    assert entry.submitter_id == "org:test"
    assert entry.signature is not None
    assert entry.signature.key_id == key_id
    assert entry.signature.alg == "Ed25519"
    assert verify(pub, entry.content_for_signing(), entry.signature.value) is True


def test_record_increments_sequence_and_chains(writer, sample_plan):
    from tests.conftest import make_plan

    e1 = writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    e2 = writer.record(make_plan("BAW12"), status=EntryStatus.ACCEPTED)
    assert e2.sequence == e1.sequence + 1
    assert e2.previous_entry_hash == e1.entry_hash()


def test_record_enriches_metadata(writer, sample_plan):
    entry = writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    assert entry.metadata["callsign"] == "QTR23"
    assert entry.metadata["origin"] == "OTHH"
    assert entry.metadata["destination"] == "EGLL"
    assert entry.metadata["aircraft_id"] == "A7-BAA"
    assert entry.metadata["dof"] == "2026-09-09"


def test_record_merges_extra_metadata(writer, sample_plan):
    entry = writer.record(
        sample_plan, status=EntryStatus.ACCEPTED, metadata={"source": "ifps", "callsign": "OVERRIDE"}
    )
    assert entry.metadata["source"] == "ifps"
    # explicit extra metadata wins over derived defaults
    assert entry.metadata["callsign"] == "OVERRIDE"


def test_record_preserves_replaces_link(writer, sample_plan):
    entry = writer.record(
        sample_plan, status=EntryStatus.AMENDED, replaces_entry_id="prev-id-123"
    )
    assert entry.status == EntryStatus.AMENDED
    assert entry.replaces_entry_id == "prev-id-123"


def test_record_all_statuses(writer, sample_plan):
    for status in EntryStatus:
        e = writer.record(sample_plan, status=status)
        assert e.status == status
