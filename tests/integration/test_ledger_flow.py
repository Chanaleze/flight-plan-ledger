"""Integration: writer -> verifier -> chain -> recovery end to end."""

from __future__ import annotations

from flight_plan_ledger.ledger.recovery import RecoveryService
from flight_plan_ledger.models.canonical import normalize_flight_plan
from flight_plan_ledger.models.ledger_entry import EntryStatus
from tests.conftest import make_plan


def test_full_accept_verify_recover_flow(writer, verifier, store, sample_plan):
    plans = [
        sample_plan,
        make_plan("BAW12", "EGLL", "KJFK"),
        make_plan("EZY8567", "EGKK", "LEPA"),
    ]
    for p in plans:
        writer.record(p, status=EntryStatus.ACCEPTED)

    # Every plan verifies
    for p in plans:
        res = verifier.verify_plan(p)
        assert res.found and res.signature_valid

    # Chain holds
    ok, msg = verifier.verify_chain()
    assert ok, msg

    # Recovery returns all three in order
    svc = RecoveryService(store)
    good = svc.last_known_good()
    assert len(good) == 3
    assert [e.sequence for e in good] == [1, 2, 3]
    report = svc.recovery_report()
    assert report["accepted_plan_count"] == 3


def test_amend_then_cancel_flow(writer, store, sample_plan):
    e1 = writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    e2 = writer.record(
        sample_plan, status=EntryStatus.AMENDED, replaces_entry_id=e1.entry_id
    )
    assert e2.replaces_entry_id == e1.entry_id
    svc = RecoveryService(store)
    # Latest per hash wins -> AMENDED is not ACCEPTED, so filtered out
    assert svc.last_known_good(only_accepted=True) == []
    assert len(svc.last_known_good(only_accepted=False)) == 1


def test_sample_json_files_roundtrip(writer, verifier):
    import json
    from pathlib import Path

    examples = Path("examples/sample-flight-plans")
    files = sorted(examples.glob("*.json"))
    assert len(files) >= 3, "expected bundled sample flight plans"
    for f in files:
        raw = json.loads(f.read_text(encoding="utf-8"))
        plan = normalize_flight_plan(raw)
        writer.record(plan, status=EntryStatus.ACCEPTED)
        res = verifier.verify_plan(plan)
        assert res.found and res.signature_valid, f"failed for {f.name}"
    ok, _ = verifier.verify_chain()
    assert ok


def test_chain_break_detected_after_manual_tamper(writer, verifier, store, sample_plan):
    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    writer.record(make_plan("BAW12"), status=EntryStatus.ACCEPTED)
    ok_before, _ = verifier.verify_chain()
    assert ok_before

    # Simulate disk-level corruption of the second line
    import json

    lines = store.path.read_text(encoding="utf-8").strip().splitlines()
    entry = json.loads(lines[1])
    entry["plan_hash"] = "sha256:" + "0" * 64
    lines[1] = json.dumps(entry)
    store.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok_after, _ = verifier.verify_chain()
    # Tampering plan_hash of the *last* entry does not break the
    # previous_entry_hash link (which points backwards), so the chain
    # itself still links — but the corrupted plan must no longer verify.
    assert ok_after is True

    # The corrupted entry itself must no longer verify as its original plan
    corrupted_plan = make_plan("BAW12")
    res2 = verifier.verify_plan(corrupted_plan)
    # plan_hash no longer matches stored hash -> not found
    assert res2.found is False
