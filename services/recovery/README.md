# Recovery Service

After a primary ATM system outage, this service can:

1. Replay the ledger from a known good checkpoint
2. Reconstruct the set of currently active / accepted flight plans
3. Export that set in a format the restored primary system (or a degraded mode) can ingest

This is one of the highest-value capabilities of the whole project.
