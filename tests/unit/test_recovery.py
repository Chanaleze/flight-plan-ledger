"""Unit tests for RecoveryService."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from flight_plan_ledger.ledger.recovery import RecoveryService
from flight_plan_ledger.models.ledger_entry import EntryStatus
from tests.conftest import make_plan


def test_last_known_good_empty(store):
    svc = RecoveryService(store)
    assert svc.last_known_good() == []


def test_last_known_good_returns_only_accepted(writer, store, sample_plan):
    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    writer.record(make_plan("BAW12"), status=EntryStatus.REJECTED)
    writer.record(make_plan("EZY1", origin="EGKK", destination="LEPA"),
                 status=EntryStatus.CANCELLED)
    svc = RecoveryService(store)
    accepted = svc.last_known_good(only_accepted=True)
    assert len(accepted) == 1
    assert accepted[0].status == EntryStatus.ACCEPTED
    # Without filter, all distinct hashes show up
    all_entries = svc.last_known_good(only_accepted=False)
    assert len(all_entries) == 3


def test_latest_entry_wins_per_plan_hash(writer, store, sample_plan):
    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    writer.record(sample_plan, status=EntryStatus.CANCELLED)  # same plan_hash, later
    svc = RecoveryService(store)
    assert svc.last_known_good(only_accepted=True) == []
    everything = svc.last_known_good(only_accepted=False)
    assert len(everything) == 1
    assert everything[0].status == EntryStatus.CANCELLED


def test_as_of_filters_future_entries(writer, store, sample_plan):
    e1 = writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    e2 = writer.record(make_plan("BAW12"), status=EntryStatus.ACCEPTED)
    assert e1.timestamp <= e2.timestamp
    svc = RecoveryService(store)
    cutoff = e1.timestamp  # include first only
    result = svc.last_known_good(as_of=cutoff)
    assert [e.sequence for e in result] == [e1.sequence]


def test_results_sorted_by_sequence(writer, store, sample_plan):
    writer.record(make_plan("C"), status=EntryStatus.ACCEPTED)
    writer.record(make_plan("A"), status=EntryStatus.ACCEPTED)
    writer.record(make_plan("B"), status=EntryStatus.ACCEPTED)
    svc = RecoveryService(store)
    result = svc.last_known_good()
    seqs = [e.sequence for e in result]
    assert seqs == sorted(seqs)


def test_export_json(writer, store, tmp_path, sample_plan):
    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    svc = RecoveryService(store)
    entries = svc.last_known_good()
    out = tmp_path / "out" / "recovery.json"
    svc.export_json(entries, out)
    assert out.exists()
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["entry_count"] == 1
    assert len(payload["entries"]) == 1
    assert payload["entries"][0]["plan_hash"] == sample_plan.content_hash()
    assert "exported_at" in payload


def test_export_summary(writer, store, sample_plan):
    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    svc = RecoveryService(store)
    text = svc.export_summary(svc.last_known_good())
    assert "1 accepted plan" in text
    assert "QTR23" in text
    assert "OTHH" in text and "EGLL" in text


def test_recovery_report(writer, store, sample_plan):
    writer.record(sample_plan, status=EntryStatus.ACCEPTED)
    svc = RecoveryService(store)
    report = svc.recovery_report()
    assert report["accepted_plan_count"] == 1
    assert report["as_of"] is None
    assert report["plans"][0]["callsign"] == "QTR23"
    assert report["plans"][0]["plan_hash"] == sample_plan.content_hash()
    # as_of variant
    as_of = datetime.now(timezone.utc)
    report2 = svc.recovery_report(as_of=as_of)
    assert report2["as_of"] == as_of.isoformat()
