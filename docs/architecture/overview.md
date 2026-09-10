# Architecture Overview

## Goal

Provide a **tamper-evident, independently verifiable record** of every flight plan that is accepted (or rejected/amended) by the ATM system, without becoming part of the real-time safety-critical path.

## Design principles

1. **Sidecar, not replacement**  
   The ledger never sits in the critical decision loop of controllers or the primary flight-processing system.

2. **Minimal on-ledger data**  
   Only cryptographic hash + essential metadata. Full flight-plan content remains in existing systems.

3. **Permissioned trust**  
   Only authorised organisations (ANSP, major airlines, regulator, selected airports) operate nodes or can write.

4. **Low operational cost**  
   Prefer simple, well-understood primitives (hash chains + digital signatures) over heavy consensus where possible. Full DLT (Hyperledger Fabric / Corda style) is an option, not a requirement for v1.

5. **Recoverability**  
   The ledger must be sufficient to reconstruct the last known good set of accepted flight plans after a primary system outage.

## Logical components

| Component        | Responsibility                                      | Criticality     |
|------------------|-----------------------------------------------------|-----------------|
| Ingestor         | Receive, normalise, validate incoming flight plans  | Medium          |
| Ledger Writer    | Hash → Sign → Append entry                          | High (integrity)|
| Permissioned Ledger | Store immutable ordered entries                  | High            |
| Verifier         | Allow any authorised party to check a plan's status | Medium          |
| Recovery Service | Replay ledger to rebuild state                      | High (post-outage) |
| Query API        | Read-only access for airlines, tools, auditors      | Low             |

## Data flow (happy path)

1. Airline submits flight plan (via existing channels or new API).
2. Ingestor normalises to a canonical form and computes content hash.
3. Ledger Writer creates a signed `LedgerEntry` and appends it.
4. Primary ATM system continues its normal processing (independent).
5. Any authorised party can later call Verifier with the original plan (or its hash) and receive cryptographic proof of what was recorded.

## Failure modes we care about

- Primary flight-processing system fails → ledger still holds the last accepted set.
- Malicious or accidental alteration of historical records → immediately detectable.
- Dispute between airline and ANSP about “what was submitted” → resolved by ledger.
- Need for rapid post-incident investigation → cryptographic timeline available in minutes instead of days.

## Technology options (still open)

**Option A – Hash chain + signatures (lowest cost)**  
Simple append-only log with Merkle tree or sequential hashes. Very cheap to run and audit.

**Option B – Permissioned DLT (Hyperledger Fabric / similar)**  
Stronger multi-party consensus and built-in membership services. Higher operational complexity.

**Recommendation for first pilot**: Start with Option A, design the data model so it can later be moved onto a full DLT without breaking clients.

## See also

- [NATS System Background](../research/nats-system-background.md) – why the FPRSA-R / NAS layer needs an independent integrity sidecar.
