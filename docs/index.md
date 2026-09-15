---
layout: home
title: Flight Plan Integrity Ledger
---

# Flight Plan Integrity Ledger

**A low-cost, permissioned integrity and recovery layer for flight-plan processing.**

> An independent, permissioned integrity ledger that records what was accepted, survives the next processing outage, and makes investigation and recovery dramatically cheaper — without touching the real-time safety path.

**Status:** Demonstration-grade prototype (v0.1, September 2026) — ready for technical outreach, not operational use.

---

## Live demo

**Try it in 30 seconds** (no signup, sample data only, nothing stored):
the interactive web demo lets you hash a flight plan, record it with an
ephemeral demo key, verify it, tamper with it, then simulate an outage and
recover. The demo URL is published in [Public Interactive Demo](demo.md)
once deployed; the demo runs the real ledger code with throwaway keys and
`org:demo`-stamped entries, so nothing there can be mistaken for an
operational record.

---

## The problem

On 8 September 2026, the UK's air traffic control provider (NATS) suffered a technical failure in its flight-processing system at Swanwick. Automated processing of flight plans stopped, controllers fell back to slow manual input, and more than 2,000 flights were cancelled or failed to operate across two days. It was the third major technical incident in three years.

The structural gap: when the processing layer fails, there is **no independent, readily queryable, cryptographically verifiable record** of exactly which plans had been accepted. Investigation and recovery are slow and expensive.

## What we are building

A **hybrid integrity sidecar** — not a replacement for NATS systems:

- Every accepted / rejected / amended flight plan produces a signed, hash-chained ledger entry (Ed25519 + SHA-256).
- Only a cryptographic hash + essential metadata is stored on the ledger; the full plan stays off-ledger.
- Any authorised party can independently verify a plan and the integrity of the chain.
- After an outage, the last known good set of accepted plans can be reconstructed from the ledger.

Full profile: [Project Profile, Business Model & Way Forward](PROJECT-PROFILE-AND-WAY-FORWARD.md) · [Principles](PRINCIPLES.md) · [Decision Log](DECISIONS.md)

---

## How to run the demo

The prototype runs locally with zero external infrastructure cost.

```bash
# 1. Install the package with test tools (single source of truth: pyproject.toml)
pip install -e ".[test]"

# 2. Run the full end-to-end demo (record → verify → chain check → recovery)
PYTHONPATH=src python -m flight_plan_ledger.cli.main demo

# 3. Useful commands
PYTHONPATH=src python -m flight_plan_ledger.cli.main list
PYTHONPATH=src python -m flight_plan_ledger.cli.main verify-chain
PYTHONPATH=src python -m flight_plan_ledger.cli.main record --plan examples/sample-flight-plans/qtr23_doha_lhr.json
PYTHONPATH=src python -m flight_plan_ledger.cli.main verify --plan examples/sample-flight-plans/qtr23_doha_lhr.json
```

Recovery drills are documented in `ops/RECOVERY-RUNBOOK.md` (see the repository).

---

## Technical note

For external review: **[A Low-Cost Hybrid Integrity Layer for Flight-Plan Processing](technical-note/flight-plan-integrity-ledger.md)** — the paper motivating the design from the September 2026 NATS outage, with problem statement, design, and deliberately modest scope.

---

## Architecture

```
Airline / Operator
        │
        ▼
   [Ingestor]  ──► validates & normalises flight plan
        │
        ▼
   [Ledger Writer]  ──► hashes plan + signs + appends to permissioned ledger
        │
        ▼
   Permissioned Ledger (nodes run by NATS, major airlines, CAA, etc.)
        │
        ├──► [Verifier]   (any authorised party can verify)
        └──► [Recovery]   (replay ledger to reconstruct last known good state)
```

The primary ATC decision path remains unchanged. This ledger is an integrity & audit sidecar.

Design detail: [Architecture Overview](architecture/overview.md) · [Hybrid Design](architecture/hybrid-design.md) · [NATS Integration Fit](architecture/nats-integration-fit.md) · [Ledger Entry Model](data-model/ledger-entry.md) · [Flight Plan Hashing](data-model/flight-plan-hash.md)

Decisions: [ADR 0001 – Permissioned Ledger](adr/0001-permissioned-ledger.md) · [ADR 0002 – Sidecar Architecture](adr/0002-sidecar-architecture.md) · [ADR 0003 – Minimal On-Ledger Data](adr/0003-minimal-on-ledger-data.md)

---

## Safety position & non-goals

Because the system is a **sidecar / integrity layer** and does **not** sit in the real-time control path:

- Failure of our ledger does not cause loss of separation.
- Primary ATC continues to operate exactly as it does today if the ledger is unavailable.
- We therefore do not require the same Design Assurance Level (DAL) as the primary flight-data processor.

We respect the relevant standards (DO-178C/ED-12C, DO-326B/ED-202A, ED-205, Part-IS, ICAO Annex 19) **without claiming compliance**. Any move toward operational use would require a formal threat & risk assessment with the sponsoring organisation — that work has not started and is not claimed.

Explicit non-goals:

- We will not claim to replace NATS, FPRSA-R, or NAS.
- We will not put real-time traffic management decisions on a blockchain.
- We will not pursue public-chain token models.
- We will not seek operational deployment without a sponsoring organisation and an appropriate assurance process.
- We will not inflate the technology story beyond what the prototype and design actually deliver.

Authoritative statements: [Project Profile §6–§9](PROJECT-PROFILE-AND-WAY-FORWARD.md) · [Principles](PRINCIPLES.md)

---

## Repository

Source code, tests, and full documentation: [github.com/Chanaleze/flight-plan-ledger](https://github.com/Chanaleze/flight-plan-ledger)

*This is an early-stage exploratory project focused on practical resilience for ATM systems.*
