# A Low-Cost Hybrid Integrity Layer for Flight-Plan Processing

**Addressing Single Points of Failure Exposed by the September 2026 NATS Outage**

**Version 0.1 – Technical Note**  
September 2026

---

## 1. Purpose and Scope

This note describes a practical, low-cost integrity and audit layer for flight-plan processing in Air Traffic Management (ATM). It is motivated by the system failure at NATS on 8 September 2026 that led to more than 2,000 cancelled flights, multi-day disruption, and an independent investigation ordered by the UK Transport Secretary.

The proposal is deliberately modest in scope:

- It does **not** replace existing flight-processing systems.
- It does **not** sit in the real-time safety-critical control path.
- It adds an independent, cryptographically verifiable record of what was submitted and accepted.

The goal is to reduce the cost and time of post-incident investigation, improve dispute resolution between airlines and the ANSP, and accelerate recovery of the last known good set of flight plans after an outage.

A working prototype implementing the core design is available and can be demonstrated locally with zero external infrastructure.

---

## 2. Problem Statement

On 8 September 2026 a technical fault in the NATS flight-processing system at Swanwick caused automated processing of flight plans to stop. Controllers fell back to manual input, capacity was severely restricted, and the resulting backlog affected operations for days. Officials have indicated the failure was avoidable and not the result of a cyber attack. It is the third major technical incident involving NATS systems in three years.

Key characteristics of the failure mode:

- A centralised processing component became unavailable.
- There was no independent, authoritative, readily queryable record of the exact set of flight plans that had been accepted up to the point of failure.
- Reconstruction of operational state and subsequent investigation therefore relied heavily on internal logs and manual correlation across multiple organisations.

The economic and political cost of such events is high. Airlines incur direct losses (cancellations, crew and aircraft disruption, passenger care). Regulators and government face pressure for accountability and improved resilience. Passengers experience large-scale disruption.

An integrity layer that is cheap to operate, independent of the primary processor, and capable of supporting rapid recovery and investigation addresses a clear operational gap.

---

## 3. Design Principles

1. **Hybrid / sidecar architecture**  
   The integrity layer runs in parallel with existing systems. It never becomes part of the controller decision loop or the primary flight-data processing path.

2. **Minimal on-ledger data**  
   Only a cryptographic hash of a canonical flight-plan representation, plus essential metadata (origin, destination, callsign, aircraft identity, date of flight, status, submitter, timestamp), is stored. Full plan content remains in existing systems.

3. **Permissioned trust model**  
   Writing and validation rights are restricted to authorised organisations (ANSP, regulator, major airlines, selected airports). No public blockchain or token economics are required.

4. **Low operational cost**  
   Preference is given to simple, well-understood primitives (hash chains + digital signatures) that can be run with modest compute and clear auditability. A full distributed-ledger platform remains an optional later evolution, not a prerequisite.

5. **Recoverability**  
   The ledger must be sufficient to reconstruct the last known good set of accepted flight plans after a primary-system outage.

---

## 4. Core Technical Approach

### 4.1 Canonical Flight Plan and Hashing

Incoming flight plans (from ICAO, FIXM/FF-ICE, or airline systems) are normalised into a strict, versioned canonical form (`FlightPlanCanonicalV1`). Deterministic serialisation rules (sorted keys, normalised timestamps, omitted nulls, fixed encoding) ensure that independent parties compute the identical hash for the same logical plan.

The content hash (currently SHA-256, recorded as `sha256:<hex>`) is the primary identifier used on the ledger.

### 4.2 Ledger Entry

Each accepted, rejected, amended or cancelled decision produces a `LedgerEntry` containing:

- Monotonic sequence number
- Timestamp
- Submitter identity
- Plan content hash
- Status (ACCEPTED / REJECTED / AMENDED / CANCELLED)
- Hash of the previous entry (forming a hash chain)
- Compact metadata
- Ed25519 signature over the entry content

The signature is produced by an operational key belonging to the writing organisation (e.g. NATS or an airline). Public keys are distributed under a simple organisational certificate scheme.

### 4.3 Hash Chain and Verification

Entries form a linear hash chain. Any party that holds the public keys can:

- Verify that a given flight plan appears on the ledger and was signed by an authorised key.
- Verify that the chain itself has not been tampered with.
- Reconstruct the sequence of decisions.

### 4.4 Recovery

After an outage of the primary processor, the ledger can be replayed to produce the last known good set of accepted plans. The prototype exports both a human-readable summary and a structured JSON artefact that can be used for further operational recovery or investigation.

---

## 5. Prototype Status (September 2026)

A working local prototype has been implemented and is publicly structured as an open repository. It demonstrates:

- Canonicalisation and deterministic hashing of flight plans
- Ed25519 key generation, signing and verification
- Append-only hash-chain ledger (file-backed for zero-dependency demos)
- Independent verification of individual plans and of the full chain
- Reconstruction of the last known good accepted set (“recovery” view)
- Command-line interface supporting record, verify, list, recover and a full end-to-end demo

Sample plans modelled on typical Qatar Airways, British Airways and easyJet operations are included. The entire demonstration runs on a single machine with only open-source libraries and requires no external services or cloud resources.

This prototype is intentionally minimal. Its purpose is to make the design concrete and to allow technical review before any larger investment of effort.

---

## 6. Relationship to Existing ATM Systems and Standards

The design is intended to complement, not compete with, current and emerging ATM data-exchange standards (SWIM, FIXM, FF-ICE). Integration points are:

- At the acceptance (or rejection) gate of the primary flight-processing system – an event can trigger a ledger write.
- Optionally at airline submission time – an airline may pre-record an “intent” hash for later correlation.
- In recovery mode – the reconstructed set can be offered back to a restored or degraded primary system.

Because the ledger is a sidecar, it does not require the same Design Assurance Level as the primary flight-data processor. This significantly lowers the certification and safety-case burden for an initial pilot.

---

## 7. Cost and Adoption Considerations

**Capital and operating cost of a first pilot**  
The prototype already runs with negligible cost. A multi-party pilot involving NATS, the CAA and a small number of airlines would primarily involve:

- Governance and key-management process definition
- Lightweight integration at the acceptance event
- Operational procedures for verification and recovery use

These are organisational rather than heavy engineering costs.

**Value proposition**  
Even a modest reduction in investigation time, dispute volume, or recovery duration after a future outage would repay the cost of a pilot many times over, given the scale of losses observed in September 2026 and previous incidents.

---

## 8. Proposed Next Steps

1. Technical review of the prototype and this note by interested parties inside NATS, the CAA, and airline operations/technology teams.
2. Refinement of the data model and canonicalisation rules against real flight-plan samples.
3. Definition of a minimal multi-party governance and key-management scheme.
4. A time-boxed pilot that records a subset of live (or shadow) acceptance decisions and exercises verification and recovery procedures.

No claim is made that the current prototype is production-ready for safety-critical use. It is offered as a concrete starting point for discussion of a low-cost resilience measure that addresses a demonstrated weakness.

---

## 9. Availability

The working prototype, source code, sample data and this technical note are maintained in a public repository structure. Interested parties are invited to examine the implementation, run the local demonstration, and provide feedback.

Contact for technical discussion can be arranged through normal professional channels.

---

*This document is an early exploratory technical note. It does not constitute a formal proposal, safety case, or commitment by any organisation.*
