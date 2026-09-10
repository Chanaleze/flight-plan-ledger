---
name: ops-ledger-admin
description: Day-to-day administration of the Flight Plan Integrity Ledger prototype (keys, ledger health, recovery, verification).
origin: project
---

# Ops – Ledger Administration

## When to use
- Checking ledger health
- Rotating or inspecting writer keys
- Running recovery after simulated or real disruption
- Verifying individual flight plans
- Exporting last-known-good state

## Standard operating procedure
1. Always work from the project root with `PYTHONPATH=src` (or active venv).
2. Prefer the CLI surface:
   - `python -m flight_plan_ledger.cli.main list`
   - `python -m flight_plan_ledger.cli.main verify-chain`
   - `python -m flight_plan_ledger.cli.main recover`
   - `python -m flight_plan_ledger.cli.main recover --output recovery.json`
3. Never delete `data/ledger.jsonl` or private keys without an explicit, logged decision.
4. After any write operation, immediately run `verify-chain`.
5. Log every admin action in `ops/TASK-LOG.md`.

## Safety rules
- Private keys stay in `data/keys/` and must never be committed.
- Prefer read-only commands first (`list`, `verify`, `recover`).
- Treat the ledger as append-only.
