# R&D Agenda — Questions, Evidence, Next Experiments

The research programme behind the ledger. Answered questions cite evidence;
open questions name the experiment that would close them. Outreach claims
may only use the Answered column.

## Answered (with evidence)

| # | Question | Answer (one line) | Evidence |
|---|----------|-------------------|----------|
| RQ-01 | Where do flight plans flow and break? | IFPS → AMS-UK → FPRSA-R → NAS; translation layer is the choke point | `research/nats-system-background.md`; NATS Final §3 |
| RQ-02 | Root cause of 28 Aug 2023? | Valid plan, 6-attribute DVL duplicate → dual critical exception in ~20 s | `research/nats-incident-reports.md` §2; NATS Final §4.2 |
| RQ-03 | Why did recovery take hours? | 800→60/hr cliff + degrading 4 h store + pending/pending-queue confusion + 5 h vendor escalation | NATS Final Ma3–Ma5; CAP2993 Ch.2 |
| RQ-04 | Has this shape failed before? | Yes: 2002 birth trauma, Dec 2013 voice, Dec 2014 server, Jul 2024 radar — same collapse pattern | `research/nats-history-and-swot.md` §4 |
| RQ-05 | Will the replacement fix it soon? | No: iTEC slipped 2015→2030s; NAS sustained to 2031; one deployment/year | DfT prioritisation Dec 2025; `nats-history-and-swot.md` §2 |
| RQ-06 | What does the regulator demand? | 34 recommendations: contingency, assurance, diversity, comms, incentives, consumer | CAP2993 Ch.5; `nats-incident-reports.md` §2 |
| RQ-07 | Does hybrid ledger fit ATM? | Yes: permissioned-ledger-for-audit + federated-real-time is the researched pattern | Profile §5 |
| RQ-00 | v0.1 behaviour contracts pinned? | Yes: fail-closed writes, duplicates allowed (dedupe is reader's job), absence proves nothing, verifier reports breaks but never repairs, no write API ever | `services/ledger-writer/INTERFACE.md`, `services/verifier/INTERFACE.md`, `contracts/openapi-sketch.yaml` |

## Open (with closing experiment)

| # | Question | Why it matters | Experiment to close |
|---|----------|----------------|---------------------|
| RQ-08 | Canonicalisation vs real ADEXP samples? | Hash equality needs byte-exact rules on real data | Run canonicaliser over de-identified real samples with an airline partner (Phase B) |
| RQ-09 | Measured recovery-time delta? | Pilot success criterion | Time-boxed shadow pilot: ledger replay vs log forensics on a simulated outage |
| RQ-10 | Multi-writer governance that airlines accept? | Consortium is the endgame | Tabletop key ceremony + dispute exercise with 2+ orgs (Phase B) |
| RQ-11 | Fabric port cost? | De-risks the evolution story | Port current entry schema to a minimal Fabric network, measure effort (only if demand exists — DEC-001) |
| RQ-12 | Schema evolution: `replaces_entry_id`, REJECTED reason codes, Merkle inclusion proofs? | Append-only corrections + dispute detail need linking; proofs need scale | Design against entry model v0.1 (`data-model/ledger-entry.md`); prototype on copies only |
| RQ-13 | Enforced key lifecycle + multi-key verification? | v0.1 gaps: single-key CLI, procedural revocation, software keys on disk | HSM/KMS custody, revocation enforcement, per-plan multi-key verify (Phase B preconditions) |
| RQ-14 | Time-bounded (`--as-of`) recovery + human re-feed runbook? | Investigators need state-at-T; operators need a safe handoff | CLI flag + pilot-grade re-feed procedure with per-plan confirmation |

## Non-goals for research

No real-time coordination studies, no public-chain token work, no safety-case
research without a sponsoring organisation (P1.1, P3.2).

## Evidence log (retrieved artefacts)

NATS Preliminary (4 Sep 2023, 18 pp) · NATS Final (14 Nov 2024, 84 pp) ·
CAA CAP2993 Final (14 Nov 2024, 71 pp, 34 recs) · Transport Focus + Define
consumer studies · CAA progress update (Apr 2025: 18/34 complete). Links and
verified summaries in `research/nats-incident-reports.md`. PDFs live on
caa.co.uk, not in this repo.

*End of agenda. New question ⇒ new row; answered ⇒ evidence pointer or it
didn't happen.*
