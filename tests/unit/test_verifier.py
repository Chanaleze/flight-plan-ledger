"""Unit tests for Verifier (plan lookup + chain checks)."""

from __future__ import annotations

from flight_plan_ledger.crypto.keys import generate_keypair
from flight_plan_ledger.ledger.verifier import Verifier
from flight_plan_ledger.models.ledger_entry import EntryStatus
from tests.conftest import make_plan


def test_verify_plan_found_and_valid(writer, verifier, sample_plan):
    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    result = verifier.verify_plan(sample_plan)
    assert result.found is True
    assert result.signature_valid is True
    assert len(result.entries) == 1


def test_verify_plan_not_found(verifier, sample_plan):
    result = verifier.verify_plan(sample_plan)
    assert result.found is False
    assert result.entries == []


def test_verify_plan_missing_signature(writer, store, keypair, key_id, sample_plan):
    from flight_plan_ledger.ledger.store import LedgerStore  # noqa: F401
    from flight_plan_ledger.models.ledger_entry import LedgerEntry

    entry = writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    # Strip signature and rewrite store with a single unsigned entry
    unsigned = LedgerEntry.model_validate(
        {**entry.model_dump(mode="json"), "signature": None}
    )
    store.path.write_text(unsigned.model_dump_json() + "\n", encoding="utf-8")
    _, pub = keypair
    v = Verifier(store, public_keys={key_id: pub})
    result = v.verify_plan(sample_plan)
    assert result.found is True
    assert result.signature_valid is False


def test_verify_plan_unknown_key_id(writer, store, sample_plan):
    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    v = Verifier(store, public_keys={})  # no known keys
    result = v.verify_plan(sample_plan)
    assert result.found is True
    assert result.signature_valid is False


def test_verify_plan_tampered_entry_detected(writer, verifier, store, sample_plan):
    entry = writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    # Tamper with the stored metadata without re-signing
    data = entry.model_dump(mode="json")
    data["metadata"]["callsign"] = "FAKE01"
    import json

    store.path.write_text(json.dumps(data) + "\n", encoding="utf-8")
    result = verifier.verify_plan(sample_plan)
    # Hash lookup still finds it (plan_hash unchanged) but signature fails
    assert result.found is True
    assert result.signature_valid is False


def test_verify_plan_wrong_key_fails(writer, store, sample_plan):
    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    _, other_pub = generate_keypair()
    # Verifier knows a *different* key under the same key_id
    from flight_plan_ledger.ledger.store import LedgerStore  # noqa: F401

    entries = store.get_all()
    key_id = entries[0].signature.key_id
    v = Verifier(store, public_keys={key_id: other_pub})
    result = v.verify_plan(sample_plan)
    assert result.signature_valid is False


def test_verify_chain_empty(store, verifier):
    ok, msg = verifier.verify_chain()
    assert ok is True
    assert "Empty" in msg


def test_verify_chain_valid(writer, verifier, sample_plan):
    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    writer.record(make_plan("BAW12"), status=EntryStatus.ACCEPTED)
    writer.record(make_plan("EZY8567", origin="EGKK", destination="LEPA"),
                 status=EntryStatus.ACCEPTED)
    ok, msg = verifier.verify_chain()
    assert ok is True
    assert "3 entries" in msg


def test_verify_chain_rejects_bad_genesis(store, verifier):
    writer = verifier.store  # store fixture
    from flight_plan_ledger.models.ledger_entry import LedgerEntry

    bad_genesis = LedgerEntry(
        sequence=1,
        submitter_id="org:test",
        plan_hash="sha256:x",
        status=EntryStatus.ACCEPTED,
        previous_entry_hash="sha256:should-be-none",
    )
    writer.append(bad_genesis)
    ok, msg = verifier.verify_chain()
    assert ok is False
    assert "Genesis" in msg


def test_verify_chain_detects_break(writer, verifier, store, sample_plan):
    import json

    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    writer.record(make_plan("BAW12"), status=EntryStatus.ACCEPTED)
    # Corrupt the second entry's previous hash
    lines = store.path.read_text(encoding="utf-8").strip().splitlines()
    second = json.loads(lines[1])
    second["previous_entry_hash"] = "sha256:deadbeef"
    store.path.write_text(lines[0] + "\n" + json.dumps(second) + "\n", encoding="utf-8")
    ok, msg = verifier.verify_chain()
    assert ok is False
    assert "Chain break" in msg
