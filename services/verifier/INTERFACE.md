# Verifier — Interface Sketch (DRAFT, unimplemented)

> **Status:** sketch only. The proven implementation is
> `src/flight_plan_ledger/ledger/verifier.py` (`Verifier`) plus the
> `fpl verify` / `fpl verify-chain` CLI commands.

## Operation: verify_plan

```
verify_plan(plan, public_keys) -> { found, entries[], signature_valid?, chain_valid?, message }
```

1. `plan_hash = plan.content_hash()`; look up entries by exact hash match.
2. No match → `{ found: false }` (plan was never recorded — not proof of anything else).
3. For each match: entry must carry a signature whose `key_id` resolves in
   `public_keys`, and Ed25519 verification over `content_for_signing()` must pass.
4. Any missing/unknown/invalid signature → `signature_valid: false`.

## Operation: verify_chain

```
verify_chain() -> (ok: bool, message: string)
```

- Empty ledger → `(true, "Empty ledger - chain is trivially valid")`.
- Genesis entry must have `previous_entry_hash = None`.
- Every later entry's `previous_entry_hash` must equal the previous entry's
  `entry_hash()` (which covers the signature). First mismatch → chain break
  naming the offending `sequence`.

## Guarantees and limits

- Read-only: never writes, never repairs. A broken chain is **reported**, not fixed.
- Verification is only as good as the `public_keys` map supplied by the caller
  (key distribution is a governance matter — see `docs/governance/key-management.md`).
- Verifying a plan proves *it was recorded with a valid signature*; it says
  nothing about operational ATC acceptance beyond the recorded `status`.
