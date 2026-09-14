# Flight Plan Hashing & Canonicalisation

## Why this matters

Two parties must be able to independently compute the **exact same hash** for the same logical flight plan.  
If canonicalisation is ambiguous, the whole integrity guarantee collapses.

## Recommended approach (v0.1)

1. **Input formats accepted**
   - ICAO flight plan (classic)
   - FIXM 4.x / FF-ICE
   - Internal airline JSON (mapped to canonical form)

2. **Canonical form**
   - Convert to a strict, versioned JSON schema (`FlightPlanCanonicalV1`)
   - All keys sorted lexicographically
   - No insignificant whitespace
   - Numbers normalised (no trailing zeros, consistent decimal representation)
   - Timestamps in UTC ISO-8601 with millisecond precision
   - Enums use uppercase string values
   - Missing optional fields are omitted (not null)

3. **Hash**
   - SHA-256 over the UTF-8 bytes of the canonical JSON
   - Result encoded as `sha256:<hex>`

## Example (simplified)

```json
{
  "aircraft_id": "A7-BAA",
  "callsign": "QTR23",
  "dof": "2026-09-09",
  "destination": "EGLL",
  "origin": "OTHH",
  "route": "..."
}
```

→ canonical bytes → `sha256:3f8a9c2e...`

## Future-proofing

- Schema is versioned (`FlightPlanCanonicalV1`, `V2`...)
- Hash algorithm is recorded in the ledger entry (`plan_hash_alg`)
- We can support multiple concurrent algorithms during migration

## Implementation location

Canonicalisation and hashing logic lives in:

- `src/flight_plan_ledger/models` – schema + normalisation
- `src/flight_plan_ledger/crypto` – pure hash functions

(`packages/` is reserved for future multi-language ports; the interface
sketches under `services/` pin the behaviour contracts.)
