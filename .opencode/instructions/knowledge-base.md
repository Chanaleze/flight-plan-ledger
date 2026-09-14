# Knowledge-Base Rules — Solve, Run, Operate (ECC-aligned)

Companion to `ops-rules.md`. This rule tells the agent how the five
canonical docs collaborate, and how to act as the expert engineer that
solves (designs), runs (drills), and operates (keys, ledger, hygiene)
inside them.

## The five docs and who owns what (single source per fact)

| Doc | Owns | Never duplicates |
|-----|------|------------------|
| `docs/PRINCIPLES.md` | Non-negotiable rules (P1–P5) | No design detail, no numbers |
| `docs/DECISIONS.md` | Decision log (DEC-*/ADR-*) | No rationale beyond one line (ADRs hold it) |
| `docs/PROJECT-PROFILE-AND-WAY-FORWARD.md` | Product, business model, roadmap, safety position | No deep tech history |
| `docs/SWOT.md` | One-page briefable SWOT + cross-strategies | No evidence prose (research holds it) |
| `docs/RD-AGENDA.md` | Answered/open research questions + evidence log | No outreach claims beyond Answered column |

Deep dives (`docs/research/*`, `docs/architecture/*`, `docs/adr/*`,
`docs/governance/*`) supply evidence; the five supply decisions.

Deep-dive owners (detail lives here, summaries in the five):

| Area | Owner doc | Behaviour contract |
|------|-----------|--------------------|
| Entry schema + canonicalisation | `docs/data-model/*` | `FlightPlanCanonicalV1`, sorted keys, UTC-ms, `sha256:<hex>`; schema versioned, multi-alg migration |
| Key hierarchy + rotation | `docs/governance/key-management.md` | Root → org cert → operational keys; 90–180 d rotation; never re-sign |
| Writer / verifier semantics | `services/*/INTERFACE.md` | Fail-closed writes; duplicates allowed; absence proves nothing; report-only verification |
| Hard limits + drills | `ops/LIMITATIONS.md`, `ops/*DRILL.md`, `ops/RECOVERY-RUNBOOK.md` | 6 limits; snapshot-first; no auto re-feed |

## Must Always (solve)

- Design inside P1: sidecar, minimal data, permissioned, cheap, recoverable.
- Check `DECISIONS.md` + relevant ADR before proposing anything structural.
- Brief from `SWOT.md`; prove from `research/`; claim only from `RD-AGENDA.md` Answered.
- New capability ⇒ code + tests + docs + index + guardrail (P2.2).

## Must Always (run & operate)

- `ops-rules.md` applies in full (verify after writes, log everything).
- Drills follow `ops/RECOVERY-RUNBOOK.md`; results logged in `ops/TASK-LOG.md`.
- Security hygiene skill before any share; keys never leave `data/keys/`.

## Must Never

- Edit a principle without a `DECISIONS.md` row first.
- Update a number in one doc and leave the others stale — propagate or stop.
- Cite the Sep-2026 motivator as sourced history (it is project narrative).
- Claim anything in `RD-AGENDA.md` Open column to outsiders.
- Commit secrets, `data/`, or recovery exports.
- Auto re-feed recovery output into any live processor.
- Add write endpoints to any future API sketch.

## Change protocol (keep the five in sync)

1. Touching behaviour? tests first, then code.
2. Touching design/trust/data? ADR or DEC row first, then docs.
3. Touching any of the five? Update `docs/README.md` index if a file is
   added; extend `tests/test_docs.py`; run full suite; log in TASK-LOG.
4. Touching research? Re-check `SWOT.md` ratings and `RD-AGENDA.md` rows.

## When unsure

Stop → log the question in TASK-LOG.md → ask before acting.
Principles beat cleverness; evidence beats memory.
