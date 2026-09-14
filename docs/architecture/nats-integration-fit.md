# NATS Integration Fit — Where the Sidecar Taps In

**Status:** Design note for pilot scoping. Demonstration-grade prototype context.
**Principles lock (non-negotiable, from the project profile §3 + ADRs):**
sidecar never in the real-time path (ADR 0002), hash + metadata only
(ADR 0003), permissioned writers (ADR 0001), low operational cost,
recoverability. **Non-claims:** no separation assurance, no capacity
management, no DAL compliance, no production readiness — safety position in
`docs/PROJECT-PROFILE-AND-WAY-FORWARD.md` §6.

Related: [NATS System Background](../research/nats-system-background.md) (flow),
[NATS History and SWOT](../research/nats-history-and-swot.md) (why),
[NATS Incident Reports](../research/nats-incident-reports.md) (evidence),
[Architecture Overview](overview.md), [Hybrid Design](hybrid-design.md).

---

## 1. Tap-in points (three, all outside the control loop)

```
Airline files → Eurocontrol IFPS (ADEXP) → AMS-UK → FPRSA-R → NAS → controllers
                     │                         │                    │
        (A) airline intent hash (optional)      │         (C) recovery handoff (human)
                                                │
                          (B) acceptance-gate write ★ primary tap
```

- **(B) Acceptance-gate write (primary).** When the primary system accepts /
  rejects / amends a plan, it emits the existing acceptance event; the
  Ledger Writer hashes the canonical plan, signs, appends. One-way, async,
  fire-and-forget: if the ledger is down, ATC continues exactly as today.
- **(A) Airline intent hash (optional).** Airline pre-records a hash at
  submission for later filed-vs-accepted correlation. Never required.
- **(C) Recovery handoff (human).** After an outage, Recovery replays the
  ledger to a last-known-good JSON set handed to the restoration team.
  **Never auto re-fed** into a live processor (see `ops/RECOVERY-RUNBOOK.md`
  step 5; prototype-grade rule).

## 2. Touch / never-touch

| Touches (reads events, writes sidecar store) | Never touches |
|----------------------------------------------|---------------|
| Acceptance/rejection event stream (read-only tap) | FPRSA-R / NAS logic, config, or data |
| Canonical plan copy for hashing (discarded after hash) | Controller working positions, flow rates, sectorisation |
| Ledger store, writer keys, verifier queries | Real-time decision loop, safety monitoring, C&M |
| Recovery JSON export (offline handoff) | Live flight-data processor input |

Failure semantics: ledger down ≠ ATC down; ledger corrupt → chain break is
detectable (`verify-chain`) and pre-break entries stay individually
verifiable. Ledger can never present unsafe data to a controller because it
presents nothing to controllers.

## 3. Data minimisation (ADR 0003)

On-ledger: content hash (`sha256:<hex>`), sequence, timestamp, submitter id,
status (ACCEPTED/REJECTED/AMENDED/CANCELLED), previous-entry hash, compact
routing metadata, Ed25519 signature. Off-ledger (forever): full plan content,
passenger data, commercial terms. Rationale: answers "what was accepted at T"
without creating a second flight database or a PII/commercial honeypot —
which is also what keeps the Part-IS / ED-205 assurance bill small (threat T5).

## 4. Trust and governance (permissioned, ADR 0001)

Writers/node operators: NATS (primary writer), CAA (auditor/node),
participating airlines/airports (own plans + verification), Eurocontrol
observer — see `../governance/participants.md`. Keys per
`../governance/key-management.md`: org-owned Ed25519 operational keys,
rotation drills in `ops/KEY-ROTATION-DRILL.md`, revocation procedural in v0.1
(verifier does not enforce revocation — runbook-known gap). Same entries are
shaped to port to Hyperledger Fabric if a consortium later wants consensus;
no re-hashing needed.

## 5. Which CAA recommendations this answers (CAP2993)

R1 contingency capacity (verifiable input for the Traffic Volume Manager) ·
R3/R4 software assurance & diversity (independent memory outside the
common-mode logic) · R5–R8 notification, ATICCC, rehearsals, leadership forum
(shared cryptographic timeline) · R14/R20 change oversight & strategic
resilience (demonstrable, non-invasive win needing no deployment slot under
the one-major-deployment-per-year cap).

## 6. Pilot shape (Phase B, only after Phase A feedback)

Tightly scoped: shadow acceptance recording + verification/recovery exercise
on a plan subset, out of any live safety path, with honest write-up including
limitations (`ops/LIMITATIONS.md`). Success = measurable investigation or
recovery-time improvement + written case study (profile §8). No multi-party
consensus build until demand and governance exist.

## 7. Explicit non-goals (restated so scoping stays honest)

Not a second FDP, not diverse real-time redundancy, not capacity, not a
replacement for FPRSA-R/NAS/iTEC, not a public chain, not a safety case.
Any request to put decisions, coordination, or auto re-feed on-ledger is out
of scope — decline with reference to ADR 0002.

*End of fit note. Change by new commit; principles change by ADR only.*
