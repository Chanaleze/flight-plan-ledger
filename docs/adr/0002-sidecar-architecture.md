# ADR 0002: Hybrid sidecar — never in the safety-critical path

## Status

Accepted

## Context

The ledger's purpose is integrity, auditability and post-outage recovery of
flight-plan decisions. A design that placed controllers or the primary
flight-data processor behind the ledger (consensus rounds, signature checks in
the decision loop) would add latency, new failure modes and a certification
burden comparable to the primary system itself — and would be politically and
operationally unacceptable to an ANSP.

## Decision

The ledger is a **hybrid sidecar**:

- The real-time ATC decision path is unchanged; the ledger receives an
  asynchronous copy of each accept/reject/amend decision.
- Ledger downtime never degrades ATC: primary operations continue exactly as
  today if the sidecar is unavailable (fail-safe, lower assurance level than
  the flight-data processor — see the project profile, section 6).
- Integration happens at three points only: the acceptance gate (event out),
  optional airline-side pre-hashing (intent entries), and recovery mode
  (last-known-good set fed back after an outage).

## Consequences

**Positive**
- No impact on controller workload or decision latency.
- Independent failure domain: the record can survive a primary-system outage.
- Progressive adoption: single parties can verify immediately; consortium governance can come later.

**Negative**
- The ledger is eventually consistent with the primary system by design; brief
  divergence windows must be understood by operators.
- Recovery replay into a restored primary system needs its own runbook (not yet written).

## Alternatives considered

- In-path ledger (every decision gated on ledger write) → rejected: latency, availability and certification risk.
- Periodic batch export / signed dumps → rejected: coarser timeline, weaker per-entry proof than a hash chain.
