# ADR 0003: Minimal on-ledger data (hash + metadata only)

## Status

Accepted

## Context

Flight plans contain operationally sensitive routing and schedule data, and any
shared record across airlines, ANSPs and regulators raises privacy, commercial
and data-protection concerns. Storing full plans on the ledger would also bloat
it and raise the cost of every node.

## Decision

Each `LedgerEntry` carries **only**:

- the content hash of the canonical plan (`sha256:<hex>`),
- the minimal metadata needed to find and explain an entry (`callsign`,
  `origin`, `destination`, `aircraft_id`, `dof`, plus caller-supplied extras),
- chain linkage (`sequence`, `previous_entry_hash`), `status`, submitter and signature.

The full flight plan **stays off-ledger** in existing systems. Verification
requires presenting the original plan (or its hash); the ledger confirms *what
was recorded*, it does not disclose *what was filed* to parties that never had it.

## Consequences

**Positive**
- Tiny ledger, cheap nodes, laptop-runnable prototype.
- No passenger or commercial PII required on the ledger.
- Dispute resolution works without exposing full plans to all readers.

**Negative**
- A lost original plan cannot be reconstructed from the ledger alone — the
  ledger is a memory of *decisions*, not a backup of *data*.
- Verifiers must obtain the plan through existing channels first.

## Alternatives considered

- Full plans on-ledger → rejected on privacy, commercial-confidentiality and size grounds.
- Hash only, zero metadata → rejected: recovery summaries and investigations
  need human-readable keys without a second lookup system.
