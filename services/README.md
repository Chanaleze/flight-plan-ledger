# Service Map — FUTURE deployment view

How the v0.1 prototype modules would map to deployable services **if** a pilot
ever needs them. Nothing here runs yet; the working equivalents are the Python
prototype (`src/flight_plan_ledger/`) and the CLI (`fpl ...`).

```
Airline / Operator
        │
        ▼
[ingestor]  receive → normalise → validate
        │   (≡ normalize_flight_plan)
        ▼
[ledger-writer]  hash → sign → append          ★ interface sketched
        │   (≡ LedgerWriter.record)
        ▼
 ledger store (append-only hash chain)
        │
        ├──► [verifier]  check plan / chain     ★ interface sketched
        │   (≡ Verifier.verify_plan / verify_chain)
        └──► [recovery]  last-known-good set
            (≡ RecoveryService + fpl recover)
                           │
                           ▼
                        [api]  optional read-only HTTP (see contracts/openapi-sketch.yaml)
```

| Service dir | Working equivalent today | Interface sketch |
|-------------|--------------------------|------------------|
| `ingestor/` | `models/canonical.py` | — (pure function, see data-model docs) |
| `ledger-writer/` | `ledger/writer.py` + `fpl record` | `INTERFACE.md` |
| `verifier/` | `ledger/verifier.py` + `fpl verify` | `INTERFACE.md` |
| `recovery/` | `ledger/recovery.py` + `fpl recover` | — (see `INTERFACE.md` of writer/verifier + recovery code) |
| `api/` | CLI read commands | `contracts/openapi-sketch.yaml` |

Rules for any future service split (from the sidecar design):

1. Services are **stateless** except the single append-only store.
2. No service sits in the real-time ATC path — the whole map is a sidecar.
3. `verifier` and `recovery` are **read-only**; only `ledger-writer` appends.
4. Every write path must be followed by `verify-chain` (see `ops` rules).
5. Tap-in points and pilot scope live in `docs/architecture/nats-integration-fit.md`;
   behaviour contracts in each service's `INTERFACE.md` mirror the prototype exactly.
