# Ledger Writer Service

Responsible for:

1. Receiving a normalised flight plan + decision status
2. Computing the content hash
3. Creating a `LedgerEntry`
4. Signing it with the organisation’s operational key
5. Appending it to the permissioned ledger

This is the most security-sensitive service in the system.  
It should run with minimal privileges and ideally use an HSM or cloud KMS for the private key.
