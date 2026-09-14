# NATS Technology History and SWOT — From Creation to the Integrity Gap

**Status:** Research note (demonstration-grade prototype context).
**Scope:** How NATS tech came to be, why the flight-processing layer keeps failing
the same way, and what that implies for a sidecar integrity ledger.
**Non-claims:** This note does not assess separation assurance, DAL compliance,
or production readiness. Safety position lives in
`docs/PROJECT-PROFILE-AND-WAY-FORWARD.md` (section 6).

Sources used: NATS Preliminary (4 Sep 2023) and Final Major Incident reports,
CAA Independent Review Interim + Final (CAP2993, Nov 2024) and April 2025
progress update, NATS annual reports / Service and Investment Plan,
DfT/CAA prioritisation letter (Dec 2025), IBM 9020 / NAS rehost history,
NATS blog 25-year PPP retrospectives (Mar/Jul 2026), contemporary BBC /
Computer Weekly / incident.io reporting. Specific report section numbers are
given where the claim comes directly from those reports.

Related: [NATS System Background](nats-system-background.md) (short operational
flow IFPS → AMS-UK → FPRSA-R → NAS), [Architecture Overview](../architecture/overview.md),
[Project Profile](../PROJECT-PROFILE-AND-WAY-FORWARD.md).

---

## 1. Executive summary of findings

1. **NATS tech is 60+ years of layered accretion, not one system.** Civil/military
   control unified as NATCS (1962) → CAA sponsorship (1972) → US FAA-derived
   NAS on IBM 9020D (1974) → rehost to IBM 4381 (1990) → SPRINT replacement of
   peripherals (1997) → Swanwick centre (2002, 6 years late) → FPRSA automation
   (2004) → two-centre consolidation with Prestwick (2010) → FPRSA-R replacement
   by Frequentis/Comsoft (Sep 2018). Each layer kept the one below alive.
2. **The replacement that was supposed to arrive in 2015 still has not arrived.**
   iTEC (UK/Spain/Germany, Indra platform) was first an interim FDP for the
   centre consolidation, then the Single European Sky FDP, then Deployment Point
   En Route / SkyNex. Target slipped 2015 → 2021 → 2030 → now V2 Scottish Upper
   2029, V3 London Upper from 2036, with NAS sustainment/replacement as
   Priority 1 to 2031. NATS itself told the CAA review that maintaining an
   up-to-date overall system map is "effectively impossible" — the Independent
   Panel upgraded that from a minor to a major finding.
3. **Failures repeat the same structural pattern, not the same bug.**
   Jul 2013 (software), Dec 2013 (Frequentis voice/touchscreen — sectors could
   not be split for daytime), Dec 2014 (Swanwick server failure), Aug 2023
   (FPRSA-R DVL duplicate-waypoint critical exception), Jul 2024 (radar/technical
   restriction), plus the September 2026 event used as this project's motivator
   in `docs/PROJECT-PROFILE-AND-WAY-FORWARD.md`. Different subsystems, same
   consequences: capacity collapses because a central function has no
   independent, queryable memory of what was already accepted.
4. **28 Aug 2023 is the best-documented instance and the template.**
   A valid Los Angeles → Paris (Orly) plan with six individually harmless
   attributes (duplicate 3-letter DVL = Devil's Lake ND + Deauville FR, both
   outside UK airspace on opposite sides, one near the UK exit, first in filed
   plan / second only in IFPS-supplemented ADEXP, true exit absent from filed
   plan) caused primary then hot-standby FPRSA-R to raise a critical exception
   and enter maintenance mode within ~20 seconds (08:32). 800 plans/hour
   automatic → ~60/hour manual (7 terminals at Swanwick; Prestwick terminals
   minor-edits only). 4-hour NAS rolling store bought time but degraded from
   the moment input stopped (exhausted ~12:32). AMS-UK pause/pending queue
   confusion kept re-presenting the poison message on every reconnect.
   Restoration 14:27–14:32, regulations lifted 15:24–18:03. Impact: 700,000+
   passengers, ~1,600 cancellations (300k cancelled, 95k 3h+ delays, 300k
   shorter delays per CAA), sector cost up to ~£100m. 34 Independent Review
   recommendations (11 for NATS alone); 18/34 complete by Apr 2025.
5. **SWOT conclusion:** Strengths are operational excellence on top of fragile
   foundations (seconds of delay per flight in normal ops, 2.5m+ flights/year,
   >£1bn tech investment in a decade). Weaknesses are architectural
   (common-mode software in primary/backup, 800→60 cliff, 4-hour degrading
   buffer, unmappable estate, vanishing legacy skills by ~2030). Opportunities
   are the funded replacement window (NAS sustainment to 2031, iTEC V2/V3,
   £120m radar renewal to 2045, UK Airspace Design Service, SWIM/FF-ICE).
   Threats are the 2030 support cliff-edge, traffic/complexity growth, and
   regulatory/political tolerance running out. A permissioned hash + metadata
   sidecar directly addresses W2–W5 and T1/T5 without touching the safety path —
   which is why this project stays a sidecar (ADR 0002).

---

## 2. From creation to today — timeline

| Period | Institutional / site milestone | Technology milestone | Why it matters for the problem |
|--------|-------------------------------|----------------------|-------------------------------|
| 1958–1962 | US Federal Aviation Act (1958) creates FAA system model. UK unifies military + civil control as **NATCS (1962)** | — | UK inherits the idea of a single national flight-data processor |
| 1966 | London ATC Centre opens at **RAF West Drayton** | Procedural + early radar control | Concentrates London control in one site for 40 years |
| 1972 | NATCS → **National Air Traffic Services (NATS)** under newly formed **CAA** | Contracts move to CAA/MoD; NATS has no separate legal existence yet | Regulator/operator split begins; distant ancestor of today's NERL/NATS Services split |
| 1974–1990 | CAA/NATS runs UK NAS | **NAS ported from US FAA, runs on IBM 9020D triplex** (3× S/360-65 + 3× S/360-50, 2+2 operational) at West Drayton. CE runs flight-data processing (route → fixes → times/levels → sector ownership); IOCE handles radar I/O | Core design — route processing into sectorised fixes — is still recognisable in today's NAS. ADEXP (European standard) comes *decades later*, forcing a permanent translation layer |
| 1978 | Scottish control from **Atlantic House, Prestwick**; Oceanic (Shanwick) procedural | — | Two-geography operation that persists to Swanwick + Prestwick today |
| 1990 | — | **NAS rehosted to IBM 4381 (System/370) + 3380/3480**, config changes from multiprocessor to main/standby with heartbeat + startover rebuild. 9020 PAMs (IBM 7289) retained until **SPRINT replaces them 27 Nov 1997** | First "keep the software, change the iron" sustainment — the pattern for the next 35 years |
| 1992–1996 | Government decides NATS should be at arm's length from CAA regulator. **1 Apr 1996: NATS Ltd, wholly owned CAA subsidiary**; military officers leave management | — | Sets up PPP; ends direct military management |
| 1996–2000 | PPP proposed (1996/1998), enshrined in **Transport Act 2000** | **£1bn 10-year investment programme** launched; ITEC design phase joined (£4m UK share; €16m EC funding). Plan: interim FDP for centre consolidation, then joint UK/Spain/Germany FDP for Single European Sky | Replacement clock starts. Original iTEC live target discussed as mid-2000s → 2015 |
| 26 Jul 2001 | **PPP completed:** Airline Group 46%, staff 5%, Government 49% + golden share. First major European ANSP in private sector | Private finance frees investment from public borrowing rules | Explains both the investment capacity (£500m of £1bn earmarked for FDP) and the airline/regulator governance tension in every later outage |
| 2001–2003 | 9/11 collapses traffic/revenue 7 weeks after PPP | **Financial restructuring Mar 2003:** £130m (£65m Gov + £65m BAA; BAA takes 4%, AG 42%), £600m bond | PPP survives its first stress test; BAA/LHR Airports Ltd holding persists |
| Jan 2002 | **Swanwick London Area Control opens** — £623m, **6 years late** (planned 1996) due to software problems. Described by NATS in 2008 as a "difficult birth" | West Drayton stays for Terminal Control until 2007/08 | "Big-bang centre + big-bang software" trauma shapes NATS's later insistence on staged migration — and its tolerance for sustaining NAS |
| 2004 | — | **FPRS → FPRSA:** largely automated translation of *some* flight-plan content, remainder manual | Direct ancestor of FPRSA-R; Route Translation logic already the complex part, documentation "not specific enough" (Final Report §3.1) |
| 2006–2011 | — | Shanwick Oceanic system (2006), LTCC + Military to Swanwick (2007/08), West Drayton closes (2008), arrival managers (2009), **Prestwick Centre opens Jan 2010** (Scottish + Manchester + Military + Oceanic), iFACTS at Swanwick (2011), EFD at Prestwick (2011) | **Two-centre strategy complete (2010):** Swanwick (London Area + Terminal) + Prestwick (Scottish + Oceanic). Saves ~£4.5m/yr (Prestwick) + ~£11m/yr (Terminal move); delays fall from 41s/flight (2004) to 7.1s (2011). But NAS + translation layer now serve both centres |
| Dec 2016 – Sep 2018 | NATS agrees FPRSA replacement Dec 2016; **Comsoft (Frequentis since 2016) selected Jul 2017**; Design Acceptance May 2018; test campaign Aug 2018 | **FPRSA-R live 19 Sep 2018** (Swanwick). ADEXP (Eurocontrol IFPS) → NAS-compatible route. Agile delivery; Route Translation guide detailed but "numerous specific steps … not fully formalised as requirements in their own right" | Sets up Aug 2023: NATS's logical approach *depicted* the DVL condition; manufacturer used the guide to derive requirements but "inadvertently missed" that condition in code (Final Report Major Ma2) |
| 2018–2023 | — | FPRSA-R processes **>15m plans, zero delay-causing failures until 28 Aug 2023** | The "extremely rare, unpredictable" defence is quantitatively true — and irrelevant to blast radius |
| 2023–2026 | CAA CAP2993 review (Interim 2024, Final Nov 2024, progress Apr 2025). NR23 settlement: **£636m regulated infra, £120m/yr run-rate**. DfT/CAA Dec 2025 prioritisation: **P1 NAS sustainment/replacement to 2031; P2 iTEC V2 Scottish Upper 2029, V3 London Upper from 2036**; one major deployment per calendar year max | iTEC limited ops at Prestwick (first controlled flight Jet2 STN–EDI, upper Scotland only, rollout over 5 years originally); **2024/25 NAS FDP resilience update**; NERC update; firewall refresh; **£120m radar renewal** (10 replace + 2 decommission of 12, life to 2045, 30–50% less energy); intelligent approach at Heathrow/Gatwick; Swanwick solar; OpenAir drone-access proposal; UKADS function awarded to NERL | Replacement horizon is now 2030s, not 2015. Panel: legacy sustainment expertise "in effect unavailable by 2030" through retirement. Press (Sep 2026) frames NAS as potentially "unsupported" from 2030 — NATS disputes "unfixable" but confirms staged sustainment plan |

Ownership today (unchanged in substance since 2003): Government 49% + golden
share, Airline Group 42%, staff 5%, LHR Airports Ltd 4%. Operator split:
**NERL** (NATS En Route plc, price-regulated en-route + Oceanic) vs
**NATS Services** (airports/towers/commercial). Swanwick = London Area +
Terminal; Prestwick = Scottish + Oceanic + (since 2010) ex-Manchester.

---

## 3. The tech stack that fails — what each piece does

**End-to-end flow (see short version in nats-system-background.md):**
Airline → Eurocontrol IFPS (Brussels, sole European source, ADEXP format) →
AMS-UK (UK message switch, has *pending* auto-forward vs *pause* manual-release
queues) → **FPRSA-R** (Swanwick, extracts UK portion, finds entry/exit) →
**NAS FDP** (holds rolling 4 hours, feeds controller working positions at
Swanwick + Prestwick) → manual-input fallback (Swanwick full plans, Prestwick
minor edits only).

| Component | Vintage / supplier | Function | Documented fragility |
|-----------|-------------------|----------|----------------------|
| NAS FDP | 1970s FAA logic; 9020D → 4381 → sustainment updates (incl. 2024/25 resilience/integration patch) | Route → fixes → times/levels/sectors; 4-hour rolling store | 50-year-old assumptions; ADEXP post-dates it so translation is permanent; store *degrades* from the moment input stops (dynamic re-routes, levels, speeds); "effectively impossible" to map end-to-end (NATS) |
| FPRSA-R | Comsoft/Frequentis, live Sep 2018; primary + hot-standby on separate HW/power/data, dedicated + central C&M | ADEXP → NAS route via entry/exit search; fail-safe to maintenance mode on critical exception to avoid showing controllers corrupt data | Primary and backup share *software logic* → common-mode failure; C&M log notes maintenance mode + timestamp but not which message caused it; no quarantine-and-continue (by safety design: all data must be understood) |
| AMS-UK | NATS message switch | IFPS → FPRSA-R queuing | Pause queue created on 28 Aug 2023 but poison message sat in *pending* queue outside it; every reconnect re-presented it and re-crashed FPRSA-R. Finding Ma4 |
| Manual input | 7 terminals Swanwick; Prestwick not qualified for full plans | Contingency FDP entry | 800/hr → ~60/hr by design ("not intended as substitute for automatic processing"); requires L1→L2→L3→vendor escalation (L2 had to travel on-site; L3→Comsoft took ~5h) |
| iTEC / SkyNex (Indra) | SESAR programme; limited Prestwick upper-airspace ops | Future FDP + trajectory/free-route enabler | Was interim → became the future; DP En Route red-rated 2024, recovery plan; one deployment/year constraint; Free Route / PBN / SWIM milestones all gated on it |

---

## 4. Incident pattern — same shape, different trigger

| Date | Trigger (subsystem) | Capacity effect | Duration / impact | Lesson codified |
|------|--------------------|-----------------|-------------------|-----------------|
| Jul 2013 | Software glitch (southern England) | Delays | Hours | "Difficult birth" era not over |
| 7 Dec 2013 | Frequentis voice/touchscreen config failure — night→day sector split impossible | Could not open day positions; <90%+ of busy schedule delivered after 14h fix | Thousands delayed; inquiry called | Contingency ≠ capacity; 11-year-old subsystem failed first time at shift change |
| 12 Dec 2014 | Swanwick system/server failure | Airspace closed/restricted ~1h, knock-on all day | Hundreds cancelled | Single-point server + manual recovery |
| 28 Aug 2023 (bank holiday Mon) | FPRSA-R DVL bug (see §5) | 800→60/hr; flow rates cut to ~30/hr at 13:00 (~4% normal) | Auto-processing down 08:32–14:27; regs to 18:03; days of backlog. 700k pax, ~1,600 cancel, ~£100m | 5 major + 5 minor NATS findings; 34 CAA recommendations; filters + software fix + Traffic Volume Manager role |
| 30 Jul 2024 | Swanwick radar/technical restriction (non-FPRSA-R) | Flow restrictions, Gatwick/Heathrow delays | Hours | Demonstrates diversity of single points, not just FPRSA-R |
| 8 Sep 2026 (project motivator) | Flight-processing failure at Swanwick per `docs/PROJECT-PROFILE-AND-WAY-FORWARD.md`: auto-processing stops, manual fallback, 2,000+ flights cancelled over 2 days, Transport Secretary "avoidable", 3rd major incident in 3 years | Manual-only collapse + multi-day backlog | Multi-million £ airline losses; independent investigation | Used in this repo as the *requirements driver* for the ledger, not as an independently sourced historical claim — do not cite it externally without the profile's caveats |

Pattern: **central automatic function stops → no independent accepted-set →
manual rate is 1–2 orders of magnitude below demand → 4-hour buffer masks then
magnifies → recovery is forensic (logs + cross-org correlation), not replay.**

---

## 5. Why 28 Aug 2023 is the reference case (detail)

Flight: Los Angeles → Paris Orly, valid IFPS plan, supplemented by IFPS
(extra waypoints, ADEXP conversion), sent via AMS-UK to Swanwick FPRSA-R at
08:32. FPRSA-R found entry APSOV, rejected IFPS-added SITET then ETRAT as exit
candidates (correctly — not in filed plan), then accepted 3-letter **DVL**.
Filed-plan DVL = Devil's Lake ND (pre-UK); supplemented-plan DVL = Deauville
FR (near UK exit). Exit thus precedes entry → not credible → critical
exception → primary disconnects to maintenance mode. Hot standby takes over,
ingests same queued message, same exception, same mode — **<20 seconds,
both lanes down.** No prior dual failure in 5 years / 15m messages; this exact
filed+supplemented combination had never been seen.

Six necessary attributes (NATS Final Report; CAA CAP2993 §2.12):

1. Route includes ≥2 same-abbreviation waypoints (globally 3,000+ duplicates;
   mostly 5-letter, minority 3-letter like DVL).
2. Both outside UK airspace, on opposite sides of it.
3. One duplicate near the UK FIR exit (eligible for search logic).
4. First duplicate in the ICAO4444 filed segment.
5. Second duplicate *absent* from filed segment, present only in IFPS supplement.
6. True UK exit absent from filed segment (no requirement to file one — software
   must then hunt beyond the exit).

Remove any one → normal processing.

**Timeline (all 28 Aug, UTC+1):** 08:32 dual failure, auto-processing ends,
4h buffer starts; 09:23 L1 notifies controller, major-incident SMS; 10:12
L1 options exhausted (L2 travel required — L1 unauthorised for full restart);
12:32 buffer exhausted, fully manual; 12:51–12:58 vendor (Comsoft) + L3 +
AMS-UK operator find *pending* (not *pause*) queue, re-queue to isolate poison
message; 13:00 rates to 30/hr; 13:26 test plans pass (after separate DB
startup issue); 14:27 full auto-processing restored (NATS reports 14:32);
15:24–18:03 regulations stepped down. Days of airline/passenger recovery
(bank-holiday demand).

**Why recovery was slow — five compounding causes (Ma1/Ma2/Ma4 + Panel):**
rare combination (unpredictable, untested) + missing coded branch (requirements
→ code gap, not requirements gap) + queue semantics + undiagnostic logs +
on-call/skill depth (Level 3 SME had never seen the log string; vendor SME 5h
in). Panel adds: CAA never audited FPRSA-R changes (no significant functional
change / low safety-impact assessment); risk system (Riskonnect) well-run but
change-portfolio oversight and resource-risk prioritisation weak [R14/R15].

---

## 6. SWOT of NATS technology

### Strengths (internal, evidence-backed)

- **S1 — Safety and delay performance in normal ops.** Delays attributable to
  NATS ~1.4s/flight (2012/13), 7.1s (2011) vs ~10× European average; early-2000s
  >100s/flight → single digits today while handling ~2.5–2.6m flights / 260–300m
  pax per year across 11% of European airspace / 25% of traffic, including the
  world's busiest single/dual runways. No serious safety incident attributed to
  Swanwick since 2002 per NATS (2008).
- **S2 — Two-centre + layered resilience that *does* prevent unsafe states.**
  Separate HW/power/data lanes, dedicated + central C&M, 4h NAS store, manual
  fallback, remote contingency + Heathrow virtual contingency tower. FPRSA-R
  correctly refused to show corrupt data — fail-safe worked as designed.
- **S3 — Funded investment machine.** >£1bn tech spend in last decade; NR23
  £636m regulated infra (£118–120m/yr); 24/7 L1/L2 + vendor L3; radar, firewall,
  NERC, EFD, iFACTS, arrival managers all delivered into live ops without
  safety events.
- **S4 — Staged modernisation actually in ops.** iTEC live (limited) at
  Prestwick, intelligent approach at Heathrow/Gatwick, OSEP small airspace wins
  (East Mids continuous climb, Lakes/Rathlin deconfliction), SWIM/OpenAir
  groundwork, UKADS coordination role awarded.
- **S5 — Institutional memory + supplier base.** Frequentis/Indra relationships,
  24-year PPP stability (2001–2026), airline-staff-government ownership aligns
  safety with service (even if it complicates blame).

### Weaknesses (internal — the integrity gap lives here)

- **W1 — NAS is a 1970s architecture sustained, not replaced.** FAA → 9020D →
  4381 → SPRINT → patches. Every ADEXP plan pays a translation tax. Panel:
  sustaining skills "in effect unavailable by 2030".
- **W2 — Common-mode software defeats redundancy.** Primary + backup FPRSA-R
  share logic → one valid message kills both in 20s. Diversity policy only
  written *after* the CAA demanded it [R4].
- **W3 — Contingency cliff: 800 → 60 (→ 30) plans/hour.** Manual terminals
  (7, Swanwick-only for full plans) are an error-correction UI, not a backup
  processor. Four-hour store degrades immediately (dynamic re-plans) and then
  expires.
- **W4 — No independent accepted-set; forensics, not replay.** Investigation
  relied on vendor-interpreted logs + AMS queue archaeology across orgs.
  Nothing cryptographically binds "airline filed X" to "ANSP accepted Y at T"
  in a place that survives the processor's own failure.
- **W5 — Unmappable, under-assured estate.** NATS: overall map "effectively
  impossible"; Panel: major finding. CAA did not audit FPRSA-R upgrades (low
  assessed safety impact). Agile Route Translation requirements left critical
  steps as guidance, not formal requirements. Queue semantics (pending vs
  pause) surprised even operators.
- **W6 — Change throughput capped.** One major tech/airspace deployment per
  year; DP En Route red in 2024 with recovery plan; Free Route/PBN/SWIM all
  gated on it. Portfolio risk feeds stability risk (delayed platform → more
  sustainment churn on fragile base).

### Opportunities (external, exploitable)

- **O1 — Funded replacement window 2025–2036.** P1 NAS sustainment/interim
  replacement to 2031 (potentially enduring fallback); P2 iTEC V2 (Scottish
  Upper 2029) / V3 (London Upper 2036+); Manchester TMA 2030, London TMA +
  Heathrow R3 2032–35.
- **O2 — Hardware refresh with headroom.** £120m radar renewal (10+2 of 12,
  to 2045, −30–50% energy); firewalls; NERC; Swanwick solar; Prestwick support
  building — all reduce obsolescence load on the FDP programme.
- **O3 — Standards tailwind.** SWIM, FIXM/FF-ICE, trajectory-based ops, Free
  Route, PBN, OpenAir (drones/AAM), UKADS single design — all assume a trusted
  exchange + audit layer. A hash+metadata record plugs into acceptance events
  without redefining them.
- **O4 — Regulatory appetite for resilience evidence.** 34 CAA recommendations
  (contingency [R1], engineering cover [R2], software assurance [R3], diversity
  [R4], change notifications [R10], strategic oversight [R14], incentives
  [R15], consumer/rehearsal forums). A low-cost, non-invasive demonstrator
  directly answers "what have you done since 2023?".
- **O5 — Sidecar economics.** Prototype runs on a laptop; pilot cost is
  governance + acceptance-event integration + runbooks, not a new ATC system.
  Even a small cut in investigation/recovery/dispute cost repays a £20–80k
  pilot (profile §4) many times over at £100m/incident scale.

### Threats (external, must survive)

- **T1 — 2030 support cliff-edge.** Press framing ("unsupported", "unfixable")
  overstates, but the underlying risk is real and acknowledged: legacy skills
  retire, vendors move on, sustainment cost rises while iTEC is still staged.
  Any FDP fault in 2030–36 has maximum blast radius.
- **T2 — Growth + complexity outrun manual fallback.** Traffic recovery,
  Heathrow expansion, new entrants (drones/AAM/space), dynamic re-routing —
  all widen the 800 vs 60 gap and shorten the useful life of a 4h buffer.
- **T3 — Data pathology is systemic.** 3,000+ duplicate abbreviations
  globally; IFPS supplementation *increases* waypoint count considerably.
  Filters added for DVL do not remove the class (any duplicate-near-exit with
  absent true exit). Next trigger will also be "extremely rare" and valid.
- **T4 — Assurance + political tolerance.** "Avoidable" (Transport Secretary),
  golden-share politics, airline compensation, CAA incentive reform, consumer
  duty (vulnerable pax, information standards). Another multi-day backlog
  invites price-control and governance intervention.
- **T5 — Cyber / information-security regulation.** Neither NATS nor Panel
  found cyber cause in 2023, but Part-IS (EU 2022/1645, 2023/203), ED-205,
  DO-326/356 now gate any operational addition. Minimal-data + permissioned +
  isolated sidecar is the only posture that keeps the assurance bill small.
- **T6 — Programme collision.** One-deployment-per-year + 12-airport London
  coordination + runway politics means any slip cascades (DP En Route →
  Free Route → TMA → R3). A sidecar that needs no deployment slot is a hedge.

**SWOT cross (SO/WO/ST/WT in one line each):**
S1+S3+O4 → offer regulators a demonstrable, non-invasive resilience win before
the next incident. W4+O3 → bind IFPS-filed hash to NAS-accepted hash at the
acceptance gate using existing SWIM/FF-ICE events. W2+O1 → run the ledger as
the diverse, independent memory that primary/backup logic can never be.
W3+T2 → replace "forensic reconstruction" with "one-command last-known-good
replay" to flatten the manual cliff. W5+T1 → a self-describing, verifiable
chain that does not depend on 1970s tribal knowledge or vendor log reading.

---

## 7. What this means for the Flight Plan Integrity Ledger

| NATS weakness/threat | Ledger answer (sidecar only) | Explicitly not claimed |
|----------------------|------------------------------|------------------------|
| W4/T5 No independent accepted-set | Signed hash-chain of ACCEPTED/REJECTED/AMENDED/CANCELLED at acceptance gate; hash + metadata only (ADR 0003); any authorised party verifies without NATS internals | Not a second FDP; does not decide, separate, or add capacity |
| W2 Common-mode dual failure | Independent trust domain (different code, keys, store); survives FPRSA-R/NAS loss; replay gives last-known-good set | Not diverse redundancy for real-time control; ledger down ≠ ATC down |
| W3 800→60 cliff | Pre-computed accepted set + JSON export shortens manual re-entry and dispute triage; Traffic Volume Manager gets a verifiable input | No real-time coordination on-chain; no throughput claim |
| W5 Unmappable estate | Minimal, versioned canonical plan + entry schema; self-validating chain reduces dependence on cross-org log correlation | No compliance claim (DO-178C/ED-12C, DO-326/ED-202A, ED-205, Part-IS); pilot needs sponsor safety/security process |
| T1 2030 cliff / T4 politics | Laptop-cheap pilot (£20–80k class), no deployment slot, permissioned (NATS/airlines/CAA/airports), evolvable to Fabric if consortium wants consensus | No public chain, no tokens, no FPRSA-R/NAS replacement |

Design lock (from profile §5 + ADRs): hash-chain + Ed25519 first (clarity,
cost, explainability); same entries portable to Hyperledger Fabric later;
hybrid per UTM-ledger research (ledger for auditability, federated systems
for real-time).

---

## Appendix A — One-page chronology (for outreach)

1962 NATCS → 1966 West Drayton → 1972 NATS/CAA → 1974 NAS (IBM 9020D, FAA
lineage) → 1978 Prestwick Atlantic House → 1990 NAS→IBM 4381 → 1996 NATS Ltd →
2000 Transport Act → 2001 PPP (AG 46/staff 5/Gov 49+golden) → 2002 Swanwick
(£623m, 6y late) → 2003 refinancing (BAA 4%) → 2004 FPRSA → 2007/08 Terminal→
Swanwick → 2010 Prestwick Centre (two-centre done) → 2016–18 FPRSA-R
(Comsoft/Frequentis) → 2023 DVL dual failure (700k pax, £100m, 34 recs) →
2024 DP En Route red / NAS patch / radar £120m → 2025 CAA progress (18/34
done) + DfT prioritisation (NAS→2031, iTEC V2 2029/V3 2036+) → 2026 PPP-25 +
Sep-2026 motivator (profile) → **pilot window now.**

## Appendix B — Glossary

NATCS/NATS/NERL, CAA, IFPS, ADEXP, AMS-UK (pending vs pause), FPRS/FPRSA/
FPRSA-R, NAS FDP, C&M, iTEC/SkyNex, DP En Route, SWIM/FIXM/FF-ICE, UKADS,
NR23, Shanwick, FIR.

## Appendix C — Key sources (retrieve by title)

- NATS Major Incident Preliminary Report (4 Sep 2023) + Final Report (with CEO
  initiation, SAF 013, Appendices A/B).
- CAA CAP2993 Independent Review: Interim + Final (Nov 2024, Jeff Halliwell
  chair, 34 recommendations) + Apr 2025 progress (18 complete, NATS 11+2
  submitted for validation).
- NATS En Route Annual Report YE Mar 2025 (David Snaith) — £120m in-year,
  £636m NR23, radar/NAS-firewall/NERC/OpenAir/UKADS.
- DfT→NATS prioritisation letter 15 Dec 2025 (redacted) — NAS→2031 P1, iTEC
  V2 2029 / V3 2036+, one deployment/year, Manchester→2030 over Scottish if
  clash, London TMA+R3 2032–35.
- IBM 9020 / UK 9020D→4381→SPRINT history (9020D triplex, PAM/7289 off
  27 Nov 1997).
- NATS PPP retrospectives (nats.aero/blog Mar + Jul 2026, Martin Rolfe) +
  House of Commons Library SN1309 + NATS 10-years-private-company review.
- BBC (Swanwick £623m, Dec 2013 voice failure), The Register (Frequentis
  touchscreen), Computer Weekly (DVL root cause), incident.io (FPRSA-R primer),
  AeroTime (NAS conversion chain).

*End of history + SWOT note. Corrections welcome — append-only thinking
applies to docs too: fix by new commit, never by rewriting history.*
