# Flight Plan Integrity Ledger – Ops & Admin Rules (ECC-aligned)

## Core principles (from ECC)
1. Plan before execute
2. Security-first
3. Prefer immutable / append-only behaviour
4. Record every operational action
5. Never invent or expose secrets

## Must Always
- Work from the project root with the correct Python environment
- Run `verify-chain` after any ledger write
- Log admin actions in `ops/TASK-LOG.md`
- Keep private keys out of git and out of shared artefacts
- Treat the ledger as append-only
- Use sample flight plans only for demos and outreach

## Must Never
- Commit `data/keys/*.private.pem` or any secret
- Delete or rewrite historical ledger entries
- Claim the system replaces NATS / FPRSA-R / NAS
- Share recovery exports that contain sensitive real-world data
- Skip verification after a write

## Preferred command surface
- list
- verify / verify-chain
- recover [--output ...]
- record (only with sample plans unless explicitly authorised)
- demo

## When unsure
Stop → log the question in TASK-LOG.md → ask before acting.
