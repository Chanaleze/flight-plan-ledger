# Ledger Writer — Interface Sketch (DRAFT, unimplemented)

> **Status:** sketch only. The proven implementation is
> `src/flight_plan_ledger/ledger/writer.py` (`LedgerWriter.record`) plus the
> `fpl record` CLI command. This document pins the interface a future service
> must honour so the sketch cannot drift from the prototype.

## Operation: record

```
record(plan, status, metadata?, replaces_entry_id?) -> LedgerEntry
```

| Field | Type | Notes |
|-------|------|-------|
| `plan` | `FlightPlanCanonicalV1` | Canonical form; see `docs/data-model/flight-plan-hash.md` |
| `status` | `ACCEPTED \| REJECTED \| AMENDED \| CANCELLED` | Decision being recorded |
| `metadata` | map (optional) | Merged over derived defaults (`callsign`, `origin`, `destination`, `aircraft_id`, `dof`) |
| `replaces_entry_id` | string (optional) | Link for amendments / cancellations |

Behaviour contract (mirrors the prototype exactly):

1. `plan_hash = plan.content_hash()` (`sha256:<hex>` of canonical bytes).
2. `sequence = store.next_sequence()`; `previous_entry_hash = store.previous_entry_hash()` (`None` for genesis).
3. Build `LedgerEntry`, sign `content_for_signing()` with Ed25519 writer key, attach `Signature{alg, key_id, value}`.
4. Append once. Never update or delete.
5. Caller runs chain verification after every write batch.

## Failure modes

- Store unavailable → **fail closed, return error, write nothing** (never a half-signed entry).
- Unknown `status` → reject before hashing.
- Duplicate submission → allowed; recorded as a new entry (dedupe is the reader's job, cf. `RecoveryService.last_known_good`).

## Non-goals

- No real-time guarantees, no consensus rounds, no callbacks into ATC systems.
