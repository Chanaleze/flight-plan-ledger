# Decision Log — What We Decided and Why

Index of product, process, and research decisions. Architectural decisions
hold full Context/Decision/Consequences in `docs/adr/`; this log records the
one-line rationale and points there. Newest first. Append-only: superseded
decisions stay listed with their replacement.

| ID | Date | Decision | Status | Detail |
|----|------|----------|--------|--------|
| DEC-011 | 2026-09-14 | Collab sweep: fold data-model, key-lifecycle, writer/verifier contracts, rejected alternatives into the five; fix 3 stale doc lines | accepted | this log; PRINCIPLES P1.6/P3.4/P4.5; RD-AGENDA RQ-12–14 |
| DEC-010 | 2026-09-14 | Knowledge base = 5 canonical docs + sync rule; agent solves/runs/operates under them | accepted | this log; rule `.opencode/instructions/knowledge-base.md` |
| DEC-009 | 2026-09-14 | Structure NATS fit as tap-in points + touch/never-touch + CAA mapping, principles locked | accepted | `docs/architecture/nats-integration-fit.md` |
| DEC-008 | 2026-09-14 | Retrieve and file official incident reports (NATS preliminary + final, CAA CAP2993) as evidence base | accepted | `docs/research/nats-incident-reports.md` |
| DEC-007 | 2026-09-14 | Commission full NATS history (1962→) + SWOT as research backbone | accepted | `docs/research/nats-history-and-swot.md` |
| DEC-006 | 2026-09-10 | Recovery replay gets its own runbook (ADR 0002 gap) + LIMITATIONS doc | accepted | `ops/RECOVERY-RUNBOOK.md`, `ops/LIMITATIONS.md` |
| DEC-005 | 2026-09-10 | Pilot economics: £20–80k validation pilots, services not SaaS ARR; Phase A/B/C staging | accepted | Profile §4, §8 |
| DEC-004 | 2026-09-10 | Phase A = quiet technical outreach, feedback not money | accepted | Profile §8; outreach skill |
| DEC-003 | 2026-09-10 | Same ledger entries portable to Hyperledger Fabric later; no re-hashing | accepted | Profile §5; fit note §4 |
| DEC-002 | 2026-09-10 | Start with signed hash-chain (Ed25519 + sequential hashes), not full DLT | accepted | Profile §5 |
| DEC-001 | 2026-09-10 | v0.1 frozen as demonstration-grade; no scope expansion until external interest justifies cost | accepted | Profile §8, §10 |
| ADR-0003 | 2026-09-10 | Minimal on-ledger data (hash + metadata only) | accepted | `docs/adr/0003-minimal-on-ledger-data.md` |
| ADR-0002 | 2026-09-10 | Sidecar architecture, never in safety-critical path | accepted | `docs/adr/0002-sidecar-architecture.md` |
| ADR-0001 | 2026-09-10 | Permissioned ledger, hash-chain first | accepted | `docs/adr/0001-permissioned-ledger.md` |

## Standing rejected alternatives (do not relitigate without new evidence)

| Rejected | Why (one line) | Source |
|----------|----------------|--------|
| Public L1/L2 chain | Cost, privacy, governance aviation would reject | ADR 0001 |
| Centralised DB + audit logs | Gives airlines no independent source of truth | ADR 0001 |
| In-path ledger (gate decisions on writes) | Latency, availability, certification risk | ADR 0002 |
| Periodic batch exports / signed dumps | Coarser timeline, weaker per-entry proof | ADR 0002 |
| Full plans on-ledger | Privacy, commercial confidentiality, size | ADR 0003 |
| Hash only, zero metadata | Recovery/investigation need human-readable keys | ADR 0003 |
| Consensus / smart contracts on critical path | Non-deterministic latency near controllers | Hybrid design |
| Write endpoints on any future HTTP API | Recording stays privileged, never an HTTP call | contracts sketch |
| Auto re-feed of recovery into a live processor | Needs per-plan human confirmation + pilot runbook | Runbook step 5 |

## How to add a decision

1. Architecture / trust / data-handling ⇒ write `docs/adr/NNNN-*.md`
   (Status/Context/Decision/Consequences/Alternatives) and add a row here.
2. Product / process / research ⇒ add a `DEC-NNN` row here with date,
   one-line why, and a pointer to the affected doc.
3. Changing a principle in `docs/PRINCIPLES.md` always needs a row here first.

*End of log. No silent reversals.*
