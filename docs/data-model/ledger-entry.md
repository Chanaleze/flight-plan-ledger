# Ledger Entry Data Model

## Design goal

Store the **minimum information** required to prove:

1. What flight plan content was presented
2. Who submitted it
3. When it was recorded
4. What decision was taken (accepted / rejected / amended)
5. That the record has not been altered afterwards

## Canonical LedgerEntry (v0.1)

```json
{
  "entry_id": "uuid-v7-or-ulid",
  "sequence": 184392,                     // monotonic per ledger
  "timestamp": "2026-09-08T14:32:17.123Z", // when written to ledger
  "submitter_id": "org:qatar-airways",    // DID or registered org ID
  "plan_hash": "sha256:a1b2c3...",        // hash of canonical flight plan
  "plan_hash_alg": "sha256",
  "status": "ACCEPTED",                   // ACCEPTED | REJECTED | AMENDED | CANCELLED
  "previous_entry_hash": "sha256:...",    // hash of previous LedgerEntry (chain)
  "metadata": {
    "origin": "LFPG",
    "destination": "EGLL",
    "aircraft_id": "A7-BAA",
    "callsign": "QTR23",
    "dof": "2026-09-09"                   // date of flight (useful for queries)
  },
  "signature": {
    "alg": "Ed25519",
    "key_id": "nats-writer-01",
    "value": "base64..."
  }
}
```

## What is deliberately *not* stored on the ledger

- Full route, altitude, speed, equipment, etc.
- Passenger or commercial data
- Any free-text remarks that could contain PII

The full canonical flight plan is stored off-ledger (existing systems or a separate encrypted store). Only its hash appears here.

## Hashing rules (critical for interoperability)

1. Flight plan is normalised to a canonical JSON or FIXM representation.
2. Fields are sorted, whitespace normalised, encodings fixed.
3. SHA-256 (or stronger) is computed over the canonical bytes.
4. The resulting hash is what is written to `plan_hash`.

Exact canonicalisation rules will live in `packages/models`.

## Chaining

Each entry contains the hash of the previous entry (`previous_entry_hash`).  
This creates a simple hash chain. A Merkle tree can be layered on top later for efficient proofs of inclusion.

## Status values

| Status     | Meaning                                      |
|------------|----------------------------------------------|
| ACCEPTED   | Plan accepted by ATM system                  |
| REJECTED   | Plan rejected (reason code in future field)  |
| AMENDED    | A previous plan was superseded               |
| CANCELLED  | Plan was cancelled after acceptance          |

When status = AMENDED or CANCELLED, an optional `replaces_entry_id` field will be added in a later version.
