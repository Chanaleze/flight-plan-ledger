"""
Simple append-only hash-chain ledger.

v0.1 is file-backed (JSON lines) for zero-dependency local demos.
The interface is deliberately small so it can later be swapped for
a real permissioned DLT or a proper database.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, List, Optional

from flight_plan_ledger.models.ledger_entry import LedgerEntry


class LedgerStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def _read_all(self) -> List[LedgerEntry]:
        entries: List[LedgerEntry] = []
        if not self.path.exists() or self.path.stat().st_size == 0:
            return entries
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                entries.append(LedgerEntry.model_validate(data))
        return entries

    def append(self, entry: LedgerEntry) -> None:
        """Append a fully formed (and preferably signed) entry."""
        with self.path.open("a", encoding="utf-8") as f:
            f.write(entry.model_dump_json() + "\n")

    def get_all(self) -> List[LedgerEntry]:
        return self._read_all()

    def get_latest(self) -> Optional[LedgerEntry]:
        entries = self._read_all()
        return entries[-1] if entries else None

    def get_by_id(self, entry_id: str) -> Optional[LedgerEntry]:
        for e in self._read_all():
            if e.entry_id == entry_id:
                return e
        return None

    def get_by_plan_hash(self, plan_hash: str) -> List[LedgerEntry]:
        return [e for e in self._read_all() if e.plan_hash == plan_hash]

    def next_sequence(self) -> int:
        latest = self.get_latest()
        return 1 if latest is None else latest.sequence + 1

    def previous_entry_hash(self) -> Optional[str]:
        latest = self.get_latest()
        return None if latest is None else latest.entry_hash()

    def iter_entries(self) -> Iterator[LedgerEntry]:
        yield from self._read_all()

    def count(self) -> int:
        return len(self._read_all())
