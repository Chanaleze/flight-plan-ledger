# Flight Plan Integrity Ledger

**Permissioned immutable ledger for flight-plan integrity, auditability and faster recovery**

This project implements a low-cost, hybrid integrity layer for Air Traffic Management (ATM) flight plans.  
It runs **alongside** existing flight-processing systems (e.g. NATS) and provides:

- Cryptographic proof of every accepted / amended flight plan
- Tamper-evident audit trail (hash chain + Ed25519 signatures)
- Independent source of truth for airlines, ANSPs, airports and regulators
- Faster post-incident investigation and state recovery

> **Design principle**: Minimal on-ledger data + hybrid architecture = low operational cost while delivering high integrity value.

## Current status (v0.1 prototype)

Working local prototype with:

- Canonical flight-plan model + deterministic SHA-256 hashing
- Ed25519 key generation, signing and verification
- Append-only hash-chain ledger (file-backed for zero-ops demos)
- Ledger Writer + independent Verifier
- Recovery service that reconstructs the last known good set of accepted plans and can export JSON
- End-to-end CLI demo that records plans, verifies them, checks the chain, and demonstrates recovery after a simulated outage
- Technical note ready for outreach (see `docs/technical-note/`)

```bash
# Quick demo (from repo root)
PYTHONPATH=src python -m flight_plan_ledger.cli.main demo
```

Interactive web demo (hash → sign → verify → recover in the browser):
see [docs/demo.md](docs/demo.md) — static frontend + one stateless serverless
function running the real logic with ephemeral demo keys (sample data only).

## Why this exists

Major flight-processing outages (such as the September 2026 NATS event) expose the cost of single points of failure and opaque internal state.  
An independent, immutable record of what was submitted and accepted dramatically reduces investigation time, dispute cost, and recovery complexity.

## High-level architecture

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

## Repository structure

```
flight-plan-ledger/
├── src/flight_plan_ledger/     # Working Python prototype
│   ├── models/                 # Canonical plan + LedgerEntry
│   ├── crypto/                 # Hashing + Ed25519
│   ├── ledger/                 # Store, Writer, Verifier, Recovery
│   └── cli/                    # Command-line interface + demo
├── tests/                      # Unit, integration, e2e + docs guardrails (100% cov)
├── docs/                       # Profile, architecture, data model, governance, ADRs
├── ops/                        # Task log + runbooks (see .opencode/skills/)
├── examples/sample-flight-plans/
├── contracts/                  # OpenAPI sketch (draft, unimplemented)
├── services/                   # Service map + interface sketches (future)
├── packages/                   # Future multi-language packages (marked)
├── infra/                      # Docker example only; no k8s/terraform yet
└── scripts/                    # Dev-setup + demo helpers
```

## Quick start

```bash
# 1. Install the package with test tools (single source of truth: pyproject.toml)
pip install -e ".[test]"

# 2. Run the full demo
PYTHONPATH=src python -m flight_plan_ledger.cli.main demo

# 3. Useful commands
PYTHONPATH=src python -m flight_plan_ledger.cli.main list
PYTHONPATH=src python -m flight_plan_ledger.cli.main verify-chain
PYTHONPATH=src python -m flight_plan_ledger.cli.main init-keys
PYTHONPATH=src python -m flight_plan_ledger.cli.main record --plan examples/sample-flight-plans/qtr23_doha_lhr.json
PYTHONPATH=src python -m flight_plan_ledger.cli.main verify --plan examples/sample-flight-plans/qtr23_doha_lhr.json
```

## Design constraints we deliberately accept

Canonical version: [Project Principles](docs/PRINCIPLES.md) (P1). Summary:

1. **Permissioned only** – no public chain, no tokenomics.
2. **Minimal data on ledger** – only hash + metadata; full plan stays off-ledger.
3. **Hybrid** – does not replace the real-time ATC processor.
4. **Low operational cost** – prioritise simple, auditable components over maximum decentralisation.

## Next steps

- [x] Core data model & cryptographic primitives
- [x] Minimal viable ledger writer + verifier + hash chain
- [x] Sample flight-plan ingestion & end-to-end demo
- [x] Richer recovery service (export last-known-good set — `recover --output`, drilled per `ops/RECOVERY-RUNBOOK.md`)
- [ ] Multi-node / multi-writer demo
- [ ] Governance & key-management tooling
- [x] Technical note for outreach to authorities (see `docs/technical-note/`)

## Documentation

Full index: [docs/README.md](docs/README.md). Start here:

- [Project Profile, Business Model & Way Forward](docs/PROJECT-PROFILE-AND-WAY-FORWARD.md)
- [Principles](docs/PRINCIPLES.md) · [Decision Log](docs/DECISIONS.md) · [SWOT](docs/SWOT.md) · [R&D Agenda](docs/RD-AGENDA.md)

Background research:

- [NATS System Background](docs/research/nats-system-background.md)
- [NATS History and SWOT](docs/research/nats-history-and-swot.md)
- [NATS Incident Reports](docs/research/nats-incident-reports.md)

Architecture & design:

- [Architecture Overview](docs/architecture/overview.md)
- [Hybrid Design](docs/architecture/hybrid-design.md)
- [NATS Integration Fit](docs/architecture/nats-integration-fit.md)
- [Ledger Entry Model](docs/data-model/ledger-entry.md)
- [Flight Plan Hashing](docs/data-model/flight-plan-hash.md)
- [ADR 0001 – Permissioned Ledger](docs/adr/0001-permissioned-ledger.md)
- [ADR 0002 – Sidecar Architecture](docs/adr/0002-sidecar-architecture.md)
- [ADR 0003 – Minimal On-Ledger Data](docs/adr/0003-minimal-on-ledger-data.md)

---

*This is an early-stage exploratory project focused on practical resilience for ATM systems.*
