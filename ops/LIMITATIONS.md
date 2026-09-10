# Operational Limitations — what this prototype does NOT do

> Read this before trusting the ledger for anything beyond demonstration and
> technical outreach. Honesty about limits is part of the safety position
> (project profile, section 6). Anything here that becomes untrue must be
> fixed in code/docs first, never in conversation.

## Hard limits (by design)

1. **No real-time role.** The ledger is eventually consistent with the primary
   system. A plan accepted 10 seconds ago may not be recorded yet. Never use
   it for live decisions.
2. **Lost plans stay lost.** The ledger stores hashes, not plans (ADR 0003).
   Without the original plan you can verify nothing.
3. **Single store, single writer key model in v0.1.** The prototype is one
   JSONL file + local PEM keys. No replication, no consensus, no HSM. Disk
   loss without a snapshot = ledger loss.
4. **No enforced revocation.** A retired key's old signatures still verify.
   Key compromise is handled procedurally (see `ops/KEY-ROTATION-DRILL.md`),
   not cryptographically.
5. **Single-key verification in the CLI.** Plans spanning a rotation need
   repeated per-key checks (see the rotation drill record).
6. **No access control in software.** "Permissioned" is currently governance
   intent + file permissions, not an enforced membership service. Do not
   expose the ledger file or the CLI to untrusted parties.

## When NOT to trust it

- Chain verification fails → only pre-break entries are individually usable,
  and only with care (see `ops/RECOVERY-RUNBOOK.md` step 3).
- You cannot produce the original plan → the hash alone proves nothing to you.
- Anyone had unsupervised write access to `data/` → the file is just a file;
  re-generate from snapshots or start over.
- Someone promises you DAL compliance, separation assurance, or capacity
  management on the basis of this prototype → walk away; those claims are
  explicitly excluded (see `CONTRIBUTING.md`).

## What would have to change for pilot grade (Phase B, not this repo state)

Sponsoring organisation, threat/risk assessment, enforced key lifecycle,
replicated store, time-bounded recovery in the CLI, re-feed runbook, and a
safety/security engagement — per the project profile roadmap.
