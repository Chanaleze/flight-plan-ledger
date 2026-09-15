# ADR 0005 – Deferred Hosted Persistence

## Status

Accepted (September 2026).

## Context

The v0.1 ledger store is file-backed JSONL (`src/flight_plan_ledger/ledger/store.py`):
zero infrastructure, zero cost, trivially inspectable — correct for local
demos and recovery drills. Free tiers from Supabase / Railway / Render tempt
an early move to a hosted store (managed Postgres, persistent disks, always-on
services). That move has real costs even when the price is €0: more moving
parts, a larger security surface (credentials, network exposure, backups),
and operational attention — all before any external party has asked for them.

## Decision

Stay file-backed for the demonstration stage. A hosted ledger store is adopted
only when **both** conditions hold:

1. **Real external interest** — a named pilot partner or sponsor, not
   hypothetical scale.
2. **A clear reason the file store cannot meet** — e.g. concurrent writers,
   durability/availability guarantees, or query needs beyond replaying a
   local JSONL chain.

Until then, hosted platforms add cost, complexity, and security surface with
little gain. Known file-store limits (single node, no concurrent writers,
manual snapshots) are accepted and documented in `ops/LIMITATIONS.md`.

## Consequences

- Prototype stays runnable on a laptop with no accounts, no credentials, and
  no network — anyone can verify every claim by running the CLI demo.
- Recovery drills and key-rotation drills keep working unchanged against
  local files.
- If a pilot arrives, this ADR tells us exactly what changed our minds
  (the two triggers above) instead of relitigating from scratch.
- The data model stays store-agnostic: `LedgerStore` is a small interface
  (`append` / `get_all` / `get_by_*`), so a hosted backend later does not
  require touching writers, verifiers, or entry formats.

## Alternatives

- **Supabase (managed Postgres) now** — rejected for now: a database the demo
  does not need, plus credentials and Row-Level-Security to get right, for
  zero additional demonstrable value.
- **Railway / Render hosted service + disk now** — rejected for now:
  always-on hosting for a prototype nobody outside this machine queries;
  free-tier sleeping/limits would make demos *less* reliable, not more.
- **Hosted store for the public web demo** (`docs/demo.md`) — rejected:
  the demo API is stateless by design (ADR 0004); persistence would contradict
  its security model without adding anything visitors can see.
