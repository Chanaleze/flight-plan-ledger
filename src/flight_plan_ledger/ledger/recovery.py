"""
Recovery service – reconstruct the last known good set of accepted flight plans
from the integrity ledger after a primary system outage.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from flight_plan_ledger.ledger.store import LedgerStore
from flight_plan_ledger.models.ledger_entry import EntryStatus, LedgerEntry


class RecoveryService:
    def __init__(self, store: LedgerStore):
        self.store = store

    def last_known_good(
        self,
        as_of: Optional[datetime] = None,
        only_accepted: bool = True,
    ) -> List[LedgerEntry]:
        """
        Return the set of entries that represent the last known good state.

        Logic (v0.1 – simple and conservative):
        - Walk the chain in order.
        - Keep the latest entry per plan_hash (or per callsign+dof as a proxy).
        - Optionally filter to ACCEPTED only.
        - Optionally stop at a given timestamp (as_of).
        """
        entries = self.store.get_all()
        if as_of is not None:
            entries = [e for e in entries if e.timestamp <= as_of]

        # Latest entry wins per plan_hash
        latest_by_hash: Dict[str, LedgerEntry] = {}
        for e in entries:
            latest_by_hash[e.plan_hash] = e

        result = list(latest_by_hash.values())

        if only_accepted:
            result = [e for e in result if e.status == EntryStatus.ACCEPTED]

        # Stable order by sequence
        result.sort(key=lambda e: e.sequence)
        return result

    def export_json(self, entries: List[LedgerEntry], path: Path) -> None:
        """Write a clean JSON export suitable for hand-off or further processing."""
        payload = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "entry_count": len(entries),
            "entries": [e.model_dump(mode="json") for e in entries],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def export_summary(self, entries: List[LedgerEntry]) -> str:
        """Human-readable summary for operators."""
        lines = [
            f"Last known good set – {len(entries)} accepted plan(s)",
            "-" * 60,
        ]
        for e in entries:
            meta = e.metadata
            lines.append(
                f"  [{e.sequence:04d}] {meta.get('callsign', '?'):8s}  "
                f"{meta.get('origin', '?')} → {meta.get('destination', '?')}  "
                f"aircraft={meta.get('aircraft_id', '?')}  "
                f"dof={meta.get('dof', '?')}  "
                f"recorded={e.timestamp.strftime('%Y-%m-%d %H:%M:%SZ')}"
            )
        lines.append("-" * 60)
        return "\n".join(lines)

    def recovery_report(self, as_of: Optional[datetime] = None) -> Dict[str, Any]:
        """Structured report useful for post-incident analysis."""
        entries = self.last_known_good(as_of=as_of)
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "as_of": as_of.isoformat() if as_of else None,
            "accepted_plan_count": len(entries),
            "plans": [
                {
                    "sequence": e.sequence,
                    "entry_id": e.entry_id,
                    "plan_hash": e.plan_hash,
                    "callsign": e.metadata.get("callsign"),
                    "origin": e.metadata.get("origin"),
                    "destination": e.metadata.get("destination"),
                    "aircraft_id": e.metadata.get("aircraft_id"),
                    "dof": e.metadata.get("dof"),
                    "recorded_at": e.timestamp.isoformat(),
                    "submitter_id": e.submitter_id,
                }
                for e in entries
            ],
        }
