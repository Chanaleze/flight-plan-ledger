# @flight-plan-ledger/crypto

Cryptographic primitives used across the project.

## Scope (v0.1)

- SHA-256 (and future hash algorithms)
- Ed25519 signing & verification (primary)
- Optional: ECDSA P-256 for broader compatibility
- Hash chaining helpers
- Simple Merkle tree (later)

No blockchain-specific cryptography in this package – keep it pure and reusable.
