# Hybrid Design Notes

## Why hybrid?

A pure “blockchain replaces ATC” approach is neither realistic nor desirable:

- Real-time latency and availability requirements of ATC are extreme.
- Safety certification of a fully distributed system would take years.
- The political and operational risk of putting controllers behind a consensus layer is unacceptable in the short term.

Therefore we deliberately choose a **hybrid** architecture:

```
┌─────────────────────────────────────────────────────────┐
│                 Existing ATM Systems                     │
│  (NATS flight processing, radar, controller tools...)   │
│                                                         │
│  ←── real-time safety-critical path (unchanged) ──→     │
└───────────────────────────┬─────────────────────────────┘
                            │
                            │ (async / parallel write)
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Flight Plan Integrity Ledger                │
│  (this project – integrity, audit, recovery sidecar)    │
└─────────────────────────────────────────────────────────┘
```

## Key properties of the hybrid approach

- **No impact on controller workload or decision latency** in normal operations.
- **Independent failure domain**: ledger can stay up when the primary processor is down (and vice versa).
- **Progressive adoption**: airlines can start verifying their own plans immediately; full multi-party governance can come later.
- **Certification path**: the ledger itself does not need the same DAL level as the primary flight-data processor.

## Integration points

1. **At acceptance gate**  
   When the primary system accepts (or rejects) a flight plan, emit an event → Ledger Writer.

2. **Airline-side submission**  
   Airlines can optionally pre-hash and submit a “intent” entry before the official filing. Useful for later dispute resolution.

3. **Recovery mode**  
   After a primary system outage, the Recovery service reconstructs the last
   known good set for a **human-confirmed handoff** to the restoration team —
   never piped automatically into a live processor (see
   `ops/RECOVERY-RUNBOOK.md` step 5).

## What we explicitly do *not* put on the critical path

- Consensus rounds
- Network partitions between ledger nodes
- Smart-contract execution
- Any cryptographic operation that could add non-deterministic latency
