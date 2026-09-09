# @flight-plan-ledger/models

Shared data models and canonicalisation logic.

## Responsibilities

- `FlightPlanCanonicalV1` schema
- Normalisation rules (sorting, encoding, timestamp format)
- `LedgerEntry` schema
- Validation helpers

This package must remain dependency-light and language-agnostic in spirit (JSON Schema + clear rules) so it can be implemented in multiple languages later.
