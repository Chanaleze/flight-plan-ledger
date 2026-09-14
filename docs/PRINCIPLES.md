# Project Principles — Non-Negotiable Rules

Canonical rule set for everyone (and every agent) who solves, runs, or
operates this project. Principles change by explicit decision only
(recorded in `docs/DECISIONS.md`, architectural ones by ADR).
Safety position lives in `docs/PROJECT-PROFILE-AND-WAY-FORWARD.md` §6.

## P1 — Product principles (what the system is)

1. **Sidecar, not replacement.** Nothing we build sits in, gates, or slows
   the real-time ATC decision path. The ledger observes and remembers; it
   never decides. (ADR 0002)
2. **Minimal on-ledger data.** Hash + key metadata only. Never full plans,
   PII, or commercial data. (ADR 0003)
3. **Permissioned only.** No public chain, no tokenomics. Writers are known
   organisations. (ADR 0001)
4. **Low operational cost.** Simple, auditable primitives first (hash chain +
   signatures); heavier consensus only if a consortium demands it.
5. **Recoverability.** The ledger must always be sufficient to rebuild the
   last known good accepted set — otherwise it has failed its purpose.
6. **Eventually consistent and fail-closed.** A plan accepted seconds ago may
   not be recorded yet — never use the ledger for live decisions. Writer
   failures write nothing (never a half-signed entry). Nothing goes on the
   critical path: no consensus rounds, no cross-node partitions, no smart
   contracts, no non-deterministic crypto latency.

## P2 — Engineering principles (how we build)

1. **Tests first for behaviour changes.** `python -m pytest tests -q` before
   every commit; 100% coverage on code touched (real behaviour + error
   paths, not trivial lines).
2. **Docs ride with code.** New capability ⇒ update `docs/` + `docs/README.md`
   index + `tests/test_docs.py` guardrail where it makes sense.
3. **Decisions are written down.** Architecture/trust/data-handling choices ⇒
   short ADR under `docs/adr/`; product/process choices ⇒ `docs/DECISIONS.md`.
4. **Append-only thinking.** History is never rewritten — in the ledger
   (corrections are new linked entries) and in docs (fix by new commit).
5. **Small, reviewable changes.** One concern per change; sketches stay
   marked sketch (`services/`, `contracts/` are future, never product).

## P3 — Evidence principles (how we claim)

1. **Evidence before synthesis.** Statements rest on inspected files, executed
   commands, or cited reports — never on memory or assumption.
2. **No safety or operational over-claims.** No DAL compliance, no separation
   assurance, no capacity management, no production readiness. Every external
   claim stays consistent with the profile §6 and `ops/LIMITATIONS.md`.
3. **Sources are cited.** NATS/CAA claims point to the retrieval note
   (`docs/research/nats-incident-reports.md`); numbers carry their origin.
4. **Hash semantics are exact.** No ledger match is not proof of
   non-acceptance; a hash without the original plan proves nothing (lost
   plans stay lost); verification is only as good as the caller's public-key
   map; a `status` field reports what was recorded, not an ATC guarantee.

## P4 — Operations principles (how we run)

1. **Verify after every write; log every action.** `verify-chain` after
   appends; every command and result in `ops/TASK-LOG.md`.
2. **Recovery is read-only.** Snapshot first, never auto re-feed into a live
   processor (`ops/RECOVERY-RUNBOOK.md`).
3. **Keys are secrets.** Never commit, share, or export private keys or
   sensitive recovery data (`.opencode/skills/ops-security-hygiene`).
4. **Rehearse, don't just document.** A runbook never drilled is
   documentation, not capability.
5. **Key lifecycle is explicit.** Identity separate from signing keys;
   rotation every 90–180 days; history is never re-signed; revocation is
   procedural in v0.1 (verifier does not enforce it) — see
   `docs/governance/key-management.md`, `ops/KEY-ROTATION-DRILL.md`.

## P5 — Outreach principles (Phase A)

Quiet technical outreach: ask for feedback, not money or pilots. Link the
technical note + project profile + working demo; keep claims modest
(`.opencode/skills/ops-outreach-prep`).

*End of principles. Challenge by proposal, change by decision.*
