"""Unit tests for LedgerStore (file-backed JSONL)."""

from __future__ import annotations

import json

from flight_plan_ledger.models.ledger_entry import EntryStatus, LedgerEntry


def _make_entry(sequence: int, plan_hash: str = "sha256:abc") -> LedgerEntry:
    return LedgerEntry(
        sequence=sequence,
        submitter_id="org:nats",
        plan_hash=plan_hash,
        status=EntryStatus.ACCEPTED,
    )


def test_empty_store(store):
    assert store.get_all() == []
    assert store.get_latest() is None
    assert store.count() == 0
    assert store.next_sequence() == 1
    assert store.previous_entry_hash() is None
    assert list(store.iter_entries()) == []


def test_append_and_read_back(store):
    e = _make_entry(1)
    store.append(e)
    assert store.count() == 1
    latest = store.get_latest()
    assert latest is not None
    assert latest.entry_id == e.entry_id
    assert store.next_sequence() == 2


def test_creates_parent_dirs(tmp_path):
    from flight_plan_ledger.ledger.store import LedgerStore

    nested = tmp_path / "a" / "b" / "ledger.jsonl"
    s = LedgerStore(nested)
    assert nested.exists()
    s.append(_make_entry(1))
    assert s.count() == 1


def test_get_by_id(store):
    e1 = _make_entry(1, "sha256:one")
    e2 = _make_entry(2, "sha256:two")
    store.append(e1)
    store.append(e2)
    assert store.get_by_id(e1.entry_id).plan_hash == "sha256:one"
    assert store.get_by_id("missing") is None


def test_get_by_plan_hash(store):
    store.append(_make_entry(1, "sha256:same"))
    store.append(_make_entry(2, "sha256:other"))
    store.append(_make_entry(3, "sha256:same"))
    found = store.get_by_plan_hash("sha256:same")
    assert len(found) == 2
    assert {e.sequence for e in found} == {1, 3}
    assert store.get_by_plan_hash("sha256:missing") == []


def test_previous_entry_hash_chains(store):
    e1 = _make_entry(1)
    store.append(e1)
    assert store.previous_entry_hash() == e1.entry_hash()


def test_skips_blank_lines(store):
    store.append(_make_entry(1))
    # Inject blank lines directly into the file
    with store.path.open("a", encoding="utf-8") as f:
        f.write("\n   \n")
    store.append(_make_entry(2))
    assert store.count() == 2


def test_persists_jsonl_format(store):
    e = _make_entry(7, "sha256:xyz")
    store.append(e)
    lines = store.path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["sequence"] == 7
    assert data["plan_hash"] == "sha256:xyz"
