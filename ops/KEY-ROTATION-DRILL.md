# Key Rotation Drill — prototype procedure + last execution

> Makes the rotation policy in `docs/governance/key-management.md` executable.
> Demo-grade: software keys on disk, single operator. A pilot would use HSM/KMS
> and two-person control — the *steps* transfer, the *key custody* does not.

## Procedure

```powershell
$env:PYTHONPATH="src"
# 1. Snapshot (never rotate against a moving target)
Copy-Item data\ledger.jsonl "data\ledger-snapshot-$(Get-Date -Format 'yyyyMMdd-HHmm').jsonl"

# 2. Generate the successor key (old key stays valid for old entries)
python -m flight_plan_ledger.cli.main init-keys --key-id <new-key-id>

# 3. Record one drill plan with the NEW key (proves the new key works end-to-end)
python -m flight_plan_ledger.cli.main record --plan examples/sample-flight-plans/qtr23_doha_lhr.json --key-id <new-key-id>

# 4. Verify both eras:
#    a plan recorded ONLY under the old key must still verify with the old key
python -m flight_plan_ledger.cli.main verify --plan <old-key-only-plan> --key-id <old-key-id>
#    the drill plan verifies under the new key
python -m flight_plan_ledger.cli.main verify --plan examples/sample-flight-plans/qtr23_doha_lhr.json --key-id <new-key-id>

# 5. Chain must still be valid (rotation appends; it never rewrites)
python -m flight_plan_ledger.cli.main verify-chain

# 6. Log everything in ops/TASK-LOG.md
```

## What "rotation" means here (and what it does not)

- New entries sign with the new key; **old entries keep old signatures forever**
  (append-only — we never re-sign history).
- The CLI verifies one `--key-id` at a time. A plan recorded under two keys
  (e.g. re-filed across a rotation) shows `signature_valid=false` under either
  single key — that is expected, not a failure. Multi-key verification is a
  known CLI gap (see `ops/RECOVERY-RUNBOOK.md` step 6).
- Revocation is procedural in v0.1: retiring a key means (a) stop using it,
  (b) announce it out-of-band, (c) log it here. The verifier does not enforce
  revocation lists yet.

## Execution record

- **2026-09-10**: `nats-writer-01` → `nats-writer-02` (see TASK-LOG). Old-key-only
  plan (BAW12) verifies under `nats-writer-01`; drill plan verifies under
  `nats-writer-02`; chain valid throughout.
