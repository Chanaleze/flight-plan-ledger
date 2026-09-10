# Contributing to the Flight Plan Integrity Ledger

This is a demonstration-grade prototype for aviation resilience research.
Contributions are welcome if they respect the sidecar design below.

## Non-negotiable rules (from the architecture)

1. **Sidecar, not replacement.** Nothing you add may sit in, gate, or slow the
   real-time ATC decision path. The ledger observes and remembers; it never decides.
2. **No safety or operational over-claims.** Do not claim DAL compliance,
   separation assurance, capacity management, or production readiness. The safety
   position lives in `docs/PROJECT-PROFILE-AND-WAY-FORWARD.md` (section 6) —
   keep every new claim consistent with it.
3. **Minimal on-ledger data.** Hash + key metadata only (ADR 0003). Never commit
   designs that put full plans, PII, or commercial data on the ledger.
4. **Append-only thinking.** History is never rewritten. Corrections are new
   entries that link back (`replaces_entry_id`).

## How to contribute

- **Small, reviewable changes.** One concern per change; update docs alongside code.
- **Tests first for behaviour changes.** Run `python -m pytest tests -q` before
  every commit; keep coverage at 100% for code you touch
  (`--cov=src --cov-report=term-missing`). Do not add tests for trivial lines
  just to chase the number — cover real behaviour and error paths.
- **Docs are part of the change.** New capability ⇒ update `docs/` (and the
  `docs/README.md` index if you add a file) plus a `tests/test_docs.py`
  guardrail where it makes sense.
- **ADRs for decisions.** Anything that changes architecture, trust assumptions
  or data handling needs a short ADR under `docs/adr/` (copy the
  Status/Context/Decision/Consequences/Alternatives format of ADR 0001).
- **Ops hygiene.** Never commit private keys, `data/`, or recovery exports
  (all git-ignored). Log ledger-affecting drills in `ops/TASK-LOG.md`.
  See `.opencode/skills/ops-security-hygiene/SKILL.md` before any push.

## Outreach discipline (Phase A)

We are in quiet technical outreach: ask for feedback, not money or pilots.
Link the technical note + project profile + working demo; keep claims modest
(see `.opencode/skills/ops-outreach-prep/SKILL.md`).
