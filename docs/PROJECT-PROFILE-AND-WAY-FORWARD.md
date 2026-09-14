# Flight Plan Integrity Ledger  

## Project Profile, Business Model & Way Forward



**Version:** 0.1  

**Date:** September 2026  

**Status:** Demonstration-grade prototype – ready for technical outreach, not operational use



---



## 1. One-Sentence Summary



We are building a low-cost, permissioned integrity and recovery layer for flight-plan processing that records what was accepted, survives the next processing outage, and makes investigation and recovery dramatically cheaper — without touching the real-time safety path.



---



## 2. The Problem



### What happened (September 2026 and previous incidents)



On 8 September 2026 the UK’s air traffic control provider (NATS) suffered a technical failure in its flight-processing system at Swanwick. Automated processing of flight plans stopped. Controllers fell back to slow manual input. More than 2,000 flights were cancelled or failed to operate across two days. Airlines incurred multi-million-pound losses. The Transport Secretary stated the failure was avoidable. It was the third major technical incident in three years.



### Root structural issues



- Flight plans flow through a translation/processing layer (FPRSA-R category) into the National Airspace System (NAS) Flight Data Processor.

- When that layer fails, there is no independent, readily queryable, cryptographically verifiable record of exactly which plans had been accepted.

- Primary and backup systems have historically shared software logic, allowing a single software fault to disable both.

- Post-incident investigation and state recovery remain slow and expensive.

- Political and regulatory pressure rises after every major outage.



The industry already has primary operational systems. What it lacks is a cheap, independent **integrity and recovery memory** that survives when those systems fail.



---



## 3. What We Are Building



### Core product



A **hybrid integrity sidecar** (not a replacement for NATS systems):



- Every accepted / rejected / amended flight plan produces a signed, hash-chained ledger entry.

- Only a cryptographic hash + essential metadata is stored on the ledger (full plan stays off-ledger).

- Any authorised party can independently verify a plan and the integrity of the chain.

- After an outage, the last known good set of accepted plans can be reconstructed from the ledger.



### Design principles (non-negotiable)



1. **Sidecar, not replacement** — never sits in the real-time controller decision loop.

2. **Minimal on-ledger data** — hash + key metadata only.

3. **Permissioned** — only authorised organisations (ANSP, regulator, major airlines, selected airports).

4. **Low operational cost** — start with a simple signed hash-chain; design the data model so it can later move to a full permissioned ledger if required.

5. **Recoverability** — the ledger must be sufficient to rebuild the last known good accepted set.



### Current technical status (September 2026)



| Capability | Status |

|------------|--------|

| Canonical flight-plan model + deterministic hashing | Working |

| Ed25519 key generation, signing, verification | Working |

| Append-only hash-chain ledger | Working |

| Independent verification | Working |

| Recovery of last-known-good set + JSON export | Working |

| CLI demo + sample plans | Working |

| Test suite | 77 tests, 100% coverage on current suite |

| Multi-party / Hyperledger-style network | Not started (future) |

| Live integration with NATS or airline systems | Not started |



The prototype runs locally with zero external infrastructure cost.



---



## 4. Business Model



### Customer segments (priority order)



1. **Major airlines** that lose money and reputation in every major outage (BA, easyJet, Ryanair, Qatar Airways, Emirates, etc.).

2. **NATS** (under political and investigative pressure to improve resilience).

3. **UK CAA / Department for Transport** (accountability and independent review).

4. **Major airports** (operational disruption).

5. Later: Eurocontrol and other ANSPs.



### Value proposition by segment



| Segment | Core value |

|---------|------------|

| Airlines | Faster recovery, clearer evidence in disputes, lower investigation cost |

| NATS | Demonstrable resilience measure that is low-risk and non-invasive |

| Regulator | Independent audit trail that supports investigation and oversight |

| Airports | Reduced knock-on disruption through faster network recovery |



### Revenue path (realistic and staged)



**Stage 0 – Now (pre-revenue)**  

Credibility assets only: working prototype, technical note, public repository.



**Stage 1 – Validation / Pilot (target 6–18 months)**  

- Paid or sponsored technical pilot with 1–2 airlines or NATS innovation budget  

- Typical early range: £20k–£80k  

- Goal: prove recovery speed and investigation value under controlled conditions



**Stage 2 – Limited production (if pilot succeeds)**  

- Annual support / licence fee per organisation  

- Professional services (integration support, key management, recovery runbooks)  

- Possible hosted verification & recovery service for airlines



**Stage 3 – Consortium (longer term)**  

- Shared permissioned network  

- Membership / node participation fees + support



Early money is almost certainly **pilot funding + services**, not large SaaS ARR. Aviation infrastructure sales cycles are long; the model must tolerate that.



### Cost structure (kept deliberately tiny)



- Current development and demonstration cost: essentially zero beyond time.

- Infrastructure for the prototype: laptop only.

- Only when a real pilot starts do meaningful costs (integration, limited hosting, legal) appear.

- The model collapses if we try to become a full ATC system. We stay a sidecar.



### Positioning sentence for outreach



> “An independent, permissioned integrity ledger that records what was accepted, survives the next processing outage, and makes investigation and recovery dramatically cheaper — without touching the real-time safety path.”



---



## 5. Architecture Stance (including permissioned blockchains)



### Current choice



Simple **signed hash-chain** (Ed25519 + sequential hashes).  

Reasons: extreme clarity, near-zero cost, easy to explain, easy to demonstrate, low certification burden while we remain a sidecar.



### Future evolution path



The data model is deliberately designed so the same ledger entries can later be written to a multi-party permissioned ledger (for example Hyperledger Fabric) if a consortium requires stronger shared consensus and membership services.



### Explicit non-choices



- Public blockchains — unsuitable for operational flight-plan data.

- Putting decision logic or real-time coordination on-chain — increases latency, complexity and certification burden.

- Replacing FPRSA-R or NAS — out of scope and unrealistic.



### Research alignment



Recent work on permissioned ledgers for Uncrewed Traffic Management concludes that pure blockchain struggles with aeronautical real-time requirements and recommends **hybrid models**: distributed ledger for auditability + federated systems for real-time coordination. Our design follows that recommendation.



---



## 6. Safety & Security Position



### Critical design decision



Because the system is a **sidecar / integrity layer** and does **not** sit in the real-time control path:



- Failure of our ledger does not cause loss of separation.

- Primary ATC continues to operate exactly as it does today if the ledger is unavailable.

- We therefore do not require the same Design Assurance Level (DAL) as the primary flight-data processor.



### Relevant standards we respect (without claiming compliance yet)



| Domain | Key references |

|--------|----------------|

| Software assurance | DO-178C / ED-12C (DAL concept) |

| Airworthiness security | DO-326B / ED-202A, DO-356A |

| ATM/ANS ground security | ED-205 |

| Information security affecting aviation safety (EU) | Part-IS (Regulations 2022/1645 & 2023/203) |

| Safety management | ICAO Annex 19, SMS |

| ATM security oversight | EUROCONTROL guidelines, national NSAs |



### How we keep the system safe in practice



1. Architectural isolation from the real-time path.

2. Fail-safe behaviour (ledger down ≠ ATC down).

3. Minimal data on the ledger (no passenger or commercial PII required).

4. Cryptographic integrity and key rotation.

5. Strict non-claims: we do not provide separation assurance, capacity management, or real-time traffic control.

6. Clear logging of all administrative actions.



Any move toward operational use would require a formal threat & risk assessment and engagement with the sponsoring organisation’s safety and security processes. That work has not started and is not claimed.



---



## 7. Current Assets



- Public / transferable Git repository with working prototype

- Technical note (`docs/technical-note/flight-plan-integrity-ledger.md`)

- End-to-end CLI demo (record → verify → recover)

- Sample flight plans (Qatar Airways, British Airways, easyJet style)

- Business model and this project profile

- Test suite with high coverage on the current code



---



## 8. Way Forward (practical roadmap)



### Phase A – Credibility & quiet outreach (now → ~3 months)



**Objectives**

- Keep the prototype stable and well-documented

- Obtain technical feedback from people who understand ATM systems

- Avoid over-claiming



**Actions**

1. Freeze current code as demonstration-grade v0.1.

2. Maintain the technical note and this project profile as the two core documents.

3. Begin quiet conversations with former/current NATS/CAA technical people, airline ops-tech contacts, and aviation resilience researchers.

4. Ask for feedback, not money or formal pilots yet.

5. Log every significant conversation and decision.



**Success criteria**

- Several informed technical people have reviewed the approach

- Feedback has been incorporated or explicitly declined with reasons

- No safety or operational claims have been made that we cannot defend



### Phase B – First pilot opportunity (target 6–18 months)



**Objectives**

- Run a controlled pilot that proves recovery and investigation value

- Generate a credible case study



**Actions**

1. Only after Phase A feedback, pursue a small paid or sponsored pilot.

2. Scope tightly: integrity recording + recovery demonstration under controlled conditions.

3. Keep the system out of any live safety-critical path.

4. Document results honestly (including limitations).



**Success criteria**

- At least one external organisation has funded or formally sponsored a pilot

- Measurable improvement in recovery or investigation speed is shown

- Written case study exists



### Phase C – Limited production / consortium exploration (only if Phase B succeeds)



**Objectives**

- Move from prototype to supported service for a small number of organisations

- Explore multi-party permissioned network only if demand and governance exist



**Actions**

1. Define support model and commercial terms.

2. Strengthen key management and operational runbooks.

3. Revisit permissioned ledger technology only if multi-party consensus is required.

4. Begin the formal safety/security engagement required by the sponsoring organisations.



**Success criteria**

- Recurring or repeatable revenue appears

- At least two independent organisations are actively using the integrity layer

- Safety and security position remains consistent with the sidecar design



---



## 9. Explicit Non-Goals



- We will not claim to replace NATS, FPRSA-R, or NAS.

- We will not put real-time traffic management decisions on a blockchain.

- We will not pursue public-chain token models.

- We will not seek operational deployment without a sponsoring organisation and an appropriate assurance process.

- We will not inflate the technology story beyond what the prototype and design actually deliver.



---



## 10. Immediate Next Actions



1. Keep the repository and documentation clean and consistent with this profile.

2. Prepare a short outreach message that links the technical note + this profile + the working demo.

3. Identify 5–10 realistic technical contacts.

4. Run one more clean demo and recovery drill; record it in the ops task log.

5. Do not expand scope into multi-party blockchain implementation until external interest justifies the cost.



---



## Document Control



- This document is the single high-level profile of the project.

- Binding rules live in `PRINCIPLES.md`; decisions in `DECISIONS.md`;
  one-page SWOT in `SWOT.md`; research programme in `RD-AGENDA.md`.
  Agent sync rule: `.opencode/instructions/knowledge-base.md`.

- Detailed technical design lives in `docs/architecture/` and `docs/technical-note/`.

- Operational procedures and task history live under `ops/`.

- All claims in external conversations should remain consistent with the readiness and safety positions stated above.



---



*End of Project Profile & Way Forward*

