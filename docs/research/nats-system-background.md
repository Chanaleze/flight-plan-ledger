# NATS System Background — Why an Integrity Sidecar Helps

## What NATS Currently Uses

Flight plans do **not** go straight to controllers.

Typical flow:

1. Airline files a flight plan → Eurocontrol IFPS (Brussels)
2. Plan arrives in standard European format (ADEXP)
3. Enters the UK via AMS-UK (Aeronautical Messaging Switch)
4. Goes through **FPRSA-R** at Swanwick
   → This is the critical translation / processing layer that converts the European format into the format required by the UK systems
5. Then into the **National Airspace System (NAS)** Flight Data Processor
   → This is the main system that maintains the live database of flight plans and feeds controllers

NAS is a long-lived system (originally based on older FAA-style architecture).
NATS has already approved accelerating its replacement because of resilience concerns.

---

## Where the Fault Is

The September 2026 outage (and previous major incidents) hit the **flight-processing / translation layer** (FPRSA-R category of system) at Swanwick.

When this layer fails:

- Automatic processing of incoming flight plans stops
- Controllers fall back to **manual input**
- Manual input can only handle a tiny fraction of normal volume
- Capacity collapses → widespread delays, cancellations, and multi-day backlog

Key structural weaknesses that keep appearing:

- Primary and backup systems have shared software logic → one software fault can disable both
- System architecture is complex and hard to keep fully mapped
- Recovery depends heavily on internal logs and manual correlation across organisations
- There is no independent, cryptographically verifiable record of exactly which plans had been accepted up to the moment of failure

The Transport Secretary publicly stated the latest failure was avoidable.

---

## How We Bring Value to the Table

We do **not** try to replace FPRSA-R or NAS.

We add a **lightweight, independent integrity layer** that sits beside them:

| Current Pain | What Our Ledger Provides |
|--------------|---------------------------|
| No independent record of accepted plans | Cryptographically signed, hash-chained record of every acceptance/rejection |
| Slow, painful post-incident investigation | Instant, verifiable timeline that any authorised party can check |
| Difficult recovery of “last known good” state | One-command reconstruction of the accepted plan set |
| Disputes between airline and ANSP about “what was filed/accepted” | Single shared source of truth |
| High cost of repeated outages | Low-cost sidecar that reduces investigation and recovery time |

**Design principles that match the real constraints:**

- Hybrid / sidecar only — never in the real-time safety-critical path
- Minimal data on the ledger (hash + key metadata only)
- Permissioned (only NATS, CAA, major airlines, etc.)
- Starts extremely cheap (our current working prototype runs on a laptop)
- Data model designed so it can later move onto Hyperledger Fabric if a full consortium wants stronger multi-party consensus

In short:
We give the industry an independent, tamper-evident memory of flight-plan decisions that survives the next failure of the translation/processing layer.
