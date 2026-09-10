---
name: ops-recovery-drill
description: Run a full recovery drill and document the last-known-good set.
origin: project
---

# Ops – Recovery Drill

## Goal
Prove we can reconstruct the accepted plan set after a simulated primary-system outage.

## Steps
1. `python -m flight_plan_ledger.cli.main list`
2. `python -m flight_plan_ledger.cli.main verify-chain`
3. `python -m flight_plan_ledger.cli.main recover --output data/recovery-drill.json`
4. Inspect the summary and the JSON export
5. Record result + timestamp in `ops/TASK-LOG.md`

## Success criteria
- Chain is valid
- Recovery returns the expected accepted plans
- Export file is written and readable
