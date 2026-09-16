# Documentation Index

Categorised map of everything under `docs/`. Start at the top and go deeper
only as needed. Agent rule for keeping these in sync:
`../.opencode/instructions/knowledge-base.md`.

Published as a website via GitHub Pages (source: `main` / `docs` folder):
the public front page is [index.md](index.md) (Jekyll config: [_config.yml](_config.yml)).

## Start here
- [Project Profile, Business Model & Way Forward](PROJECT-PROFILE-AND-WAY-FORWARD.md) — the single high-level profile: problem, product, business model, roadmap, non-goals.
- [Principles](PRINCIPLES.md) — non-negotiable rules for building, running, and talking about this project.
- [Operational Limitations](OPERATIONAL-LIMITATIONS.md) — the product boundary for external readers: six limits, pilot preconditions, comms rule.
- [Decision Log](DECISIONS.md) — what we decided and why (ADRs hold the detail).
- [SWOT](SWOT.md) — one-page briefable strengths/weaknesses/opportunities/threats.
- [R&D Agenda](RD-AGENDA.md) — answered vs open research questions and evidence.

## Background research
- [NATS System Background](research/nats-system-background.md) — how flight plans flow (IFPS → AMS-UK → FPRSA-R → NAS) and why an integrity sidecar helps.
- [NATS History and SWOT](research/nats-history-and-swot.md) — from 1962/NATCS and 1970s NAS to FPRSA-R, incident pattern, and SWOT of NATS tech.
- [NATS Incident Reports](research/nats-incident-reports.md) — retrieved official reports (NATS preliminary + final, CAA CAP2993 + 34 recommendations) with links and verified findings.

## Architecture & design
- [Architecture Overview](architecture/overview.md) — goal, principles, components, data flow.
- [Hybrid Design](architecture/hybrid-design.md) — why a sidecar, integration points, what stays off the critical path.
- [NATS Integration Fit](architecture/nats-integration-fit.md) — tap-in points, touch/never-touch, CAA-recommendation mapping, pilot scope.

## Data model
- [Flight Plan Hashing](data-model/flight-plan-hash.md) — canonical form and hashing rules.
- [Ledger Entry Model](data-model/ledger-entry.md) — minimal on-ledger record.

## Governance & operations
- [Participants](governance/participants.md) — who runs nodes and writes.
- [Key Management](governance/key-management.md) — writer keys and rotation.
- Operational procedures and task history live in `ops/` (see `ops/TASK-LOG.md`).

## Outreach
- [Technical Note](technical-note/flight-plan-integrity-ledger.md) — the paper for external review.
- [Public Interactive Demo](demo.md) — browser demo architecture, security model, and deployment (static `demo/` + stateless `/api/demo`).

## Decisions
- [ADR 0001 – Permissioned Ledger](adr/0001-permissioned-ledger.md) — why permissioned, why hash-chain first.
- [ADR 0002 – Sidecar Architecture](adr/0002-sidecar-architecture.md) — never in the safety-critical path.
- [ADR 0003 – Minimal On-Ledger Data](adr/0003-minimal-on-ledger-data.md) — hash + metadata only.
- [ADR 0004 – Public Demo Architecture](adr/0004-public-demo.md) — stateless function, ephemeral keys, Vercel default.
- [ADR 0005 – Deferred Hosted Persistence](adr/0005-deferred-hosted-persistence.md) — file-backed until a pilot demands otherwise.
