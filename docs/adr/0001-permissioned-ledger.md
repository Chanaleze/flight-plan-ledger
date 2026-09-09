# ADR 0001: Permissioned Ledger (not public blockchain)

## Status

Accepted

## Context

We need an immutable, multi-party verifiable record of flight plans.  
Public blockchains (Ethereum, etc.) bring:

- Unnecessary token economics
- High and unpredictable transaction costs
- Public visibility of operational metadata
- Governance complexity that aviation stakeholders will reject

## Decision

We will use a **permissioned** ledger:

- Only authorised organisations can operate writing nodes or validate membership.
- No native cryptocurrency or public gas market.
- Identity is based on organisational certificates / DIDs issued under a governance framework.

## Consequences

**Positive**
- Dramatically lower and predictable operating cost
- Easier regulatory conversation
- Ability to keep certain metadata private to the consortium
- Simpler key management and revocation

**Negative**
- We must design and operate membership & governance ourselves
- Less “trustless” than a public chain (we accept this trade-off)

## Alternatives considered

- Public L1/L2 → rejected on cost, privacy and governance grounds
- Pure centralised database with audit logs → rejected because it does not give airlines an independent source of truth
- Fully decentralised permissionless network → operationally and politically unrealistic for ATM
