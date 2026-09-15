<!-- Pre-filled for every PR. The bot reposts the full version with the demo
command and safety note on first open — this template is the author's own
checklist. Delete what does not apply, keep it honest. -->

## What does this change do?

## Checklist

- [ ] Tests pass: `python -m pytest tests -q`; coverage kept at 100% for touched code
- [ ] No secrets: no private keys (`.pem`/`.key`), `data/`, or recovery exports
- [ ] Docs updated alongside code (`docs/` + `tests/test_docs.py` guardrail where apt)
- [ ] ADRs added for architecture / trust / data-handling decisions
- [ ] One concern per change; no safety or operational over-claims
- [ ] `ops/TASK-LOG.md` updated for ledger-affecting work

See CONTRIBUTING.md for the full rules.
