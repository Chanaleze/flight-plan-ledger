# Operational Limitations — the product boundary

> This note is the boundary of the project, written for external readers.
> Treat it as an asset: it screens partners, scopes pilots, and keeps every
> conversation honest. Anything here that becomes untrue must be fixed in
> code/docs first, never in conversation. Operator detail lives in
> `../ops/LIMITATIONS.md`; the binding safety position in
> `PROJECT-PROFILE-AND-WAY-FORWARD.md` (§6–§9).

**One-line version:** an independent integrity sidecar that remembers what was
accepted and proves it afterwards. It decides nothing, controls nothing, and
replaces nothing.

## Limits we will not negotiate away

| Limit | What it means for you |
|-------|------------------------|
| No real-time role | The ledger trails the primary system by design. Never use it for live decisions. This is the core selling point (low assurance burden), not a gap to patch with claims. |
| Hashes, not full plans | Only hash + metadata is recorded (ADR 0003). Without the original plan, nothing can be verified — any pilot must say how the sponsor re-attaches plans off-ledger. |
| Single store, single writer (v0.1) | One JSONL file, local keys, no replication or consensus. Correct for demos; a pilot brings the sponsor's storage and key custody, not this laptop. |
| No enforced revocation | A retired key's old signatures still verify. Key lifecycle in a pilot is a sponsor-owned procedure with drill evidence — not a crypto feature we pretend to have. |
| Single-key CLI verify | Plans spanning a rotation need repeated per-key checks. Multi-key verify is backlog, only when a real rotation is in scope. |
| No software access control | "Permissioned" today is governance intent + file permissions. Never expose the ledger or writer on a public network; a pilot runs on private network / sponsor IAM. |

## How to read reactions to this note

- "Good — we understand the boundary" → serious technical contact. Proceed.
- "Can we still use it for live decisions?" → explain once, then walk away if they insist.
- "Ignore that for the pitch" → do not proceed.

Put this note (link or short appendix) in every serious conversation. It does
your screening for you. Log every pushback on limits in `../ops/TASK-LOG.md`
— who asked to stretch what.

## Phase B pilot preconditions — all six, in writing, before any pilot

Do not start a pilot until the sponsor agrees to own:

1. Threat and risk assessment.
2. Key custody and rotation (their keys, their procedure).
3. Replicated / backed-up store.
4. How original plans are re-attached for recovery.
5. A time-bounded recovery procedure they will actually run.
6. Explicit non-use for real-time decisions.

If they will not fund or own these, it is not a pilot — it is a demo with
risk on us. Until then: no replication, HSM, or membership builds "to look
ready." That burns time and blurs the safety story.

## Communication rule

- **Cold outreach:** gap + sidecar + demo link; limits available on request and in the profile.
- **Technical reply / call:** limits up front (this note), then demo and recovery value.
- **Anyone saying "buy / deploy / certify":** full note first — no commercial talk until they accept the boundary.

Never let conversation outrun the written limits.
