# SWOT — NATS Technology and Our Opening

One-page operational version. Deep evidence and timeline live in
`docs/research/nats-history-and-swot.md` (§2–§5); official findings in
`docs/research/nats-incident-reports.md`. This page is the version you
brief from. Updated by decision (see `docs/DECISIONS.md`), never silently.

## Strengths (internal)

- **S1** Normal-ops excellence: seconds of delay/flight, ~2.5m flights/yr.
- **S2** Layered fail-safe design: fail-safe worked as designed in Aug 2023.
- **S3** Funded investment machine: >£1bn/decade, NR23 £636m.
- **S4** Staged modernisation in ops: iTEC limited live, radar £120m renewal.
- **S5** PPP stability + supplier base (Frequentis/Indra).

## Weaknesses (internal — the gap lives here)

- **W1** 1970s NAS sustained, not replaced; legacy skills gone by ~2030.
- **W2** Common-mode software defeats primary/backup redundancy.
- **W3** Contingency cliff: 800 → ~60 plans/hour; 4 h store degrades.
- **W4** No independent accepted-set: forensics, not replay.
- **W5** Unmappable estate ("effectively impossible" — Panel: major finding).
- **W6** One major deployment/year caps change throughput.

## Opportunities (external)

- **O1** Funded replacement window: NAS→2031, iTEC V2 2029 / V3 2036+.
- **O2** Hardware refresh with headroom (radar, firewalls, NERC).
- **O3** Standards tailwind: SWIM, FF-ICE, Free Route, UKADS.
- **O4** Regulatory appetite for demonstrable resilience (34 CAA recs).
- **O5** Sidecar economics: £20–80k pilot vs ~£100m/incident.
  Pilot-grade gate (from `ops/LIMITATIONS.md`): sponsoring organisation,
  threat/risk assessment, enforced key lifecycle, replicated store,
  time-bounded recovery, human re-feed runbook, safety/security engagement.

## Threats (external)

- **T1** 2030 support cliff-edge. **T2** Growth widens the manual gap.
- **T3** Data pathology systemic (3,000+ duplicate waypoints).
- **T4** Political/regulatory tolerance running out. **T5** Part-IS/ED-205
  assurance burden. **T6** Programme collision under one-slot-per-year.

## Cross-strategies (what we do about it)

- **S1+S3+O4 →** offer a demonstrable, non-invasive resilience win now.
- **W4+O3 →** bind filed-hash to accepted-hash at the acceptance gate.
- **W2+O1 →** be the diverse independent memory the lanes can never be.
- **W3+T2 →** replace forensic reconstruction with one-command replay.
- **W5+T1 →** a self-describing chain independent of tribal knowledge.

**Bottom line:** strengths sit on fragile foundations; the ledger insures the
weaknesses without touching the strengths. Stays a sidecar (P1.1).

*End of SWOT. Challenge the ratings with evidence, not adjectives.*
