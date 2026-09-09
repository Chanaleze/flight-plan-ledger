# Participants & Roles (Draft)

## Core writing / validating organisations (suggested initial set)

| Organisation type      | Example                  | Role                              |
|------------------------|--------------------------|-----------------------------------|
| ANSP                   | NATS                     | Primary writer, node operator     |
| National regulator     | UK CAA                   | Auditor, node operator, governance|
| Major airline hub      | British Airways, easyJet, Ryanair, Qatar Airways, Emirates | Writer (own plans) + verifier |
| Selected airports      | Heathrow, Gatwick        | Verifier + limited writer         |
| Network manager        | Eurocontrol (observer)   | Read / verify                     |

## Roles

- **Writer**: can append new LedgerEntries (subject to policy)
- **Validator / Node operator**: maintains a full copy of the ledger and participates in any consensus
- **Verifier**: can query and cryptographically verify entries (read-only)
- **Auditor**: full read access + ability to request key ceremony records

## Membership lifecycle

1. Organisation applies / is invited
2. Root of trust (initially a small governance committee) issues organisational certificate
3. Organisation generates its own operational keys and registers them
4. Keys can be rotated and revoked under documented procedures

Detailed key management is described in `key-management.md`.
