# Documentation Index

Categorised map of everything under `docs/`. Start at the top and go deeper
only as needed.

## Start here
- [Project Profile, Business Model & Way Forward](PROJECT-PROFILE-AND-WAY-FORWARD.md) — the single high-level profile: problem, product, business model, roadmap, non-goals.

## Background research
- [NATS System Background](research/nats-system-background.md) — how flight plans flow (IFPS → AMS-UK → FPRSA-R → NAS) and why an integrity sidecar helps.

## Architecture & design
- [Architecture Overview](architecture/overview.md) — goal, principles, components, data flow.
- [Hybrid Design](architecture/hybrid-design.md) — why a sidecar, integration points, what stays off the critical path.

## Data model
- [Flight Plan Hashing](data-model/flight-plan-hash.md) — canonical form and hashing rules.
- [Ledger Entry Model](data-model/ledger-entry.md) — minimal on-ledger record.

## Governance & operations
- [Participants](governance/participants.md) — who runs nodes and writes.
- [Key Management](governance/key-management.md) — writer keys and rotation.
- Operational procedures and task history live in `ops/` (see `ops/TASK-LOG.md`).

## Outreach
- [Technical Note](technical-note/flight-plan-integrity-ledger.md) — the paper for external review.

## Decisions
- [ADR 0001 – Permissioned Ledger](adr/0001-permissioned-ledger.md) — why permissioned, why hash-chain first.
- [ADR 0002 – Sidecar Architecture](adr/0002-sidecar-architecture.md) — never in the safety-critical path.
- [ADR 0003 – Minimal On-Ledger Data](adr/0003-minimal-on-ledger-data.md) — hash + metadata only.
