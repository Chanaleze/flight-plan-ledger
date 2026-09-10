# Contracts / Chaincode

This directory is reserved for smart contracts or chaincode **if** we decide to use a full permissioned DLT (e.g. Hyperledger Fabric).

For the first version we may implement a simple hash-chain without any on-chain code.  
In that case this directory will remain mostly empty or contain only interface definitions.

## Current content

- [`openapi-sketch.yaml`](openapi-sketch.yaml) — **draft, unimplemented** sketch of a future *optional* read-only HTTP façade over the CLI surface (`verify`, `verify-chain`, `recover`). No write endpoints by design; recording stays a privileged writer operation. Mirrors the proven CLI 1:1.
