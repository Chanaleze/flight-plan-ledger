# NATS 28 Aug 2023 Failure — Official Reports (Retrieval Note)

**Retrieved:** September 2026. All three core reports below were downloaded
from the UK CAA official publication pages and text-extracted to verify
contents. PDFs are not committed to this repo (size + hygiene) — use the
canonical CAA links.

Related: [NATS History and SWOT](nats-history-and-swot.md),
[NATS System Background](nats-system-background.md).

---

## 1. Reports that exist (yes — full public record)

| # | Report | Publisher / date | Size | Canonical source |
|---|--------|------------------|------|------------------|
| 1 | NATS Major Incident **Preliminary Report** — FPRSA-R sub-system incident 28 Aug 2023 | NATS, issued 4 Sep 2023 | 18 pp | `https://www.caa.co.uk/publication/download/20648` |
| 2 | NATS Major Incident Investigation **Final Report** — FPRSA-R incident 28 Aug 2023 (SAF 013, CEO-commissioned, Lead Investigator intro) | NATS, published alongside CAA review 14 Nov 2024 | 84 pp | CAA page `https://www.caa.co.uk/CAP2993C`, file `https://www.caa.co.uk/publication/download/23340` (1.2 MB PDF) |
| 3 | **Independent Review** of NATS (En Route) Plc's Flight Planning System Failure on 28 Aug 2023 — **Final Report (CAP2993)** | Independent Panel chaired by Jeff Halliwell, final report dated 31 May 2024, first published 14 Nov 2024 (v1, updated 25 Nov 2024 to add Prospect union to Appendix E) | 71 pp (801 kB PDF) | CAA page `https://www.caa.co.uk/data-and-publications/publications/documents/content/cap2993/`, file `https://www.caa.co.uk/publication/download/23337` |
| 4a | Transport Focus — passenger experience during the outage | Transport Focus via CAA | — | CAA page `https://www.caa.co.uk/CAP2993A` |
| 4b | Define — qualitative consumer-feedback research | Define via CAA | — | CAA page `https://www.caa.co.uk/CAP2993B` |
| 5 | CAA **progress update** on the 34 recommendations (as at end Apr 2025) | CAA, 2025 | — | `https://www.caa.co.uk/publication/download/25369` — headline: **18 of 34 complete**, NATS considers its 11+2 submitted for validation |

NATS's own short public summary is at
`https://www.nats.aero/news/nats-report-into-air-traffic-control-incident-details-root-cause-and-solution-implemented/`
(6 Sep 2023): duplicate-waypoint critical exception, fail-safe to maintenance
mode, fix to prevent recurrence.

---

## 2. What the reports establish (verified from extracted text)

**Cause (all three agree):** valid LA → Paris Orly plan; FPRSA-R entry APSOV
found, IFPS-added SITET then ETRAT correctly rejected as exits (not in filed
plan), then 3-letter **DVL** accepted — filed-plan DVL = Devil's Lake ND,
supplement DVL = Deauville FR. Exit precedes entry → critical exception →
primary then hot-standby into maintenance mode in ~20 s (08:32). Six jointly
necessary attributes (see history-and-swot §5); any one absent → normal
processing. >15m plans processed Sep 2018 – Aug 2023 with no prior dual
failure.

**Blast radius:** auto 800/hr → manual ~60/hr (7 Swanwick terminals; Prestwick
minor-edits only); rates cut to ~30/hr 13:00; 4 h NAS store degrading from
08:32, exhausted ~12:32; AMS-UK pause queue created but poison message sat in
*pending* queue and re-crashed FPRSA-R on each reconnect; auto restored
14:27–14:32, regulations stepped down 15:24–18:03. 700,000+ passengers
(300k cancelled incl. ~1,600 flights, 95k 3 h+ delays, 300k shorter), sector
cost up to ~£100m (CAA review).

**NATS Final — 5 Major findings:** Ma1 extreme rarity (6-attribute combo);
Ma2 requirements→code gap (NATS Route Translation guide depicted the DVL
condition; manufacturer derived requirements from it but inadvertently omitted
that branch in code); Ma3 joint decision-making invocation model; Ma4 pending
vs pause queue residue; Ma5 escalation timing (vendor SME ~5 h in).
5 Minor: Mi1 resilience understanding, **Mi2 system-architecture complexity
("effectively impossible" to keep an up-to-date overall map — Panel upgrades
to major)**, Mi3 password-login delay, Mi4 resolution-focus delayed
escalation, Mi5 manual-process methodology capped throughput. Plus
observations, 10 opportunities for improvement, positive outputs (§5.1–5.3).

**Independent Review CAP2993 — 34 recommendations in 8 TOR groups**
(TOR order; see Ch.5 pp.49–52 for verbatim list):

- TOR#1 Cause/prevention R1 contingency for max capacity without restrictions;
  R2 engineering onsite cover matched to demand; R3 software assurance review;
  R4 software-diversity policy with evidenced per-system account.
- TOR#2 Communication R5 earlier airline/airport notification + pre-arranged
  cadence; R6 stakeholder comms incl. ATICCC; R7 regular cross-sector major-
  incident rehearsals (CAA facilitated); R8 senior leadership resilience forum.
- TOR#3 Resources/resilience R9–R10 change-notification review (cyber controls,
  internal coordination first); R11–R13 CAA oversight resources, sampling of
  new/changed systems, weighting contingency-mode capacity impact in audits.
- TOR#4 Investment R14 strategic oversight of change programme; R15 consumer
  interests in investment/incentive framework.
- TOR#5 Performance/incentives R16 cancellations/knock-on measurement; R17
  comparative ANSP ambition; R18 stronger resilience incentives; R19 business-
  plan guidance on resilience/consumer outcomes; R20 NERL strategic resilience
  approach like other safety-critical sectors.
- TOR#6 Consumer R21–R24 legislation/CAA powers (information, enforcement
  without courts, resources, statutory consumer body); R25 vulnerable-pax
  arrangements.
- TOR#7 System response R26 airport support; R27 airport consumer-resilience
  plans; R28 airline staffed representation at airports; R29 vouchers; R30
  multi-channel comms suite (CAA-coordinated); R31 standardised UK261 rights
  communication; R32 claims pace/courtesy; R33 mandatory ADR membership.
- TOR#8 Financial risk R34 do not dilute UK261 consumer protections.

---

## 3. How to use them for this project

- Cite **cause + blast-radius numbers** from §2 (all sourced above) instead of
  the Sep-2026 motivator when talking to technical reviewers; keep the
  Sep-2026 event labelled as this repo's project narrative per the profile.
- Map ledger value to **R1 (contingency capacity), R3/R4 (assurance/diversity
  via independent memory), R5–R8 (shared verifiable timeline), R14/R20
  (strategic resilience)** — sidecar only, no safety-path claims.
- Next retrieval step (not yet done): pull 4a/4b consumer reports + Apr-2025
  progress file when consumer-impact or implementation-status evidence is
  needed for outreach.

*End of retrieval note. Fix by new commit; canonical PDFs live on caa.co.uk,
not in this repo.*
