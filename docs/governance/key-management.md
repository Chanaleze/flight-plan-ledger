# Key Management (Draft)

## Principles

- Organisational identity is separate from operational signing keys.
- All signing keys used for ledger entries must be rotatable and revocable.
- Private keys never leave the organisation’s security boundary.
- A simple, auditable process is preferred over exotic MPC in the first version.

## Key hierarchy (proposed)

1. **Root of Trust**  
   Controlled by the initial governance committee (ANSP + Regulator + 1–2 airlines).  
   Used only to issue / revoke organisational certificates.

2. **Organisational Certificate**  
   Long-lived, identifies the legal entity (e.g. “Qatar Airways”).

3. **Operational Signing Keys**  
   Short- to medium-lived keys used by the Ledger Writer service.  
   Bound to the organisational certificate.  
   Can be hardware-backed (HSM / cloud KMS) or software with strong access control.

## Rotation & revocation

- Planned rotation: every 90–180 days or on personnel change.
- Emergency revocation: governance committee can publish a revocation entry that nodes must honour.

## Future improvements

- Threshold signatures or multi-party computation for the highest-value keys.
- Integration with existing aviation PKI where possible.
