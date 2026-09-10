# Recovery Runbook — post-outage reconstruction (prototype, demo-grade)

> Fills the gap flagged in ADR 0002 ("recovery replay needs its own runbook").
> Written for the v0.1 file-backed prototype. Any pilot would adapt — not copy —
> these steps to its own store and governance.

## When to use this runbook

The primary flight-processing system (or your copy of its state) has failed or
is suspect, and you need the ledger's independent memory of what was accepted.
The ledger itself is a sidecar: it never caused the outage and cannot fix the
primary system — it only answers *"what had been accepted up to time T?"*

## Preconditions

- Access to the ledger file (`data/ledger.jsonl`) and at least one writer
  public key (`data/keys/*.public.pem`).
- Python environment with the package installed (`pip install -e ".[test]"`).
- A scribe: every command and its output goes into `ops/TASK-LOG.md`.

## Procedure

### 1. Freeze and snapshot (do not write to the ledger)

Copy — never move — the current state first:

```powershell
Copy-Item data\ledger.jsonl "data\ledger-snapshot-$(Get-Date -Format 'yyyyMMdd-HHmm').jsonl"
```

Rationale: recovery is read-only. If anyone is still able to append, stop them
first; a moving target cannot be reconstructed.

### 2. List what is there

```powershell
$env:PYTHONPATH="src"
python -m flight_plan_ledger.cli.main list
```

Record the entry count and the highest `sequence`. If the ledger is empty,
stop: there is nothing to recover — say so in the log.

### 3. Verify the chain

```powershell
python -m flight_plan_ledger.cli.main verify-chain
```

- `Chain valid - N entries` → proceed.
- `Chain break at sequence=X` → **do not proceed past step 3.** Entries before
  the break are still independently verifiable plan-by-plan (`verify`), but the
  ordered timeline is suspect. Escalate, log, and treat every entry after the
  break as unverified.

### 4. Export the last known good set

```powershell
python -m flight_plan_ledger.cli.main recover --output data/recovery-<date>.json
```

Inspect the summary: each line is one accepted plan (latest entry per plan
wins; duplicates from re-filings are collapsed — see `RecoveryService`).
Optionally re-run with a cutoff once the failure time is known. (The CLI
currently exports "everything accepted"; time-bounded export is a
`RecoveryService.last_known_good(as_of=...)` call — see step 6.)

### 5. Hand off, don't re-feed automatically

Give the JSON export to the team restoring the primary system. **Never pipe
recovery output straight back into a live flight-data processor** in this
prototype grade: re-feeding needs human confirmation per plan and a pilot-grade
runbook that does not exist yet (Phase B work).

### 6. Known CLI gaps (do not work around silently)

- No `--as-of` flag on `recover` yet — time-bounded recovery needs a Python call.
- `verify` loads one `--key-id` at a time — multi-key verification means
  repeated calls (see the key rotation drill below).
- Revocation entries are described in `docs/governance/key-management.md` but
  not enforced by the verifier — a revoked key's old signatures still verify.
  Key compromise handling is therefore procedural, not automatic.

### 7. Close out

- Log every command, result, and decision in `ops/TASK-LOG.md`.
- Keep the snapshot and the export (both are git-ignored runtime data).
- File a follow-up: what failed, what the ledger proved, what to change.

## Rehearsal

Run this runbook end-to-end as a drill (see `ops-recovery-drill` skill):
`list` → `verify-chain` → `recover --output ...` → inspect → log.
A runbook never rehearsed is documentation, not capability.
