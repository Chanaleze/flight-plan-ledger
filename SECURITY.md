# Security Policy

Scope honesty first: this is a **demonstration-grade prototype** — an
integrity sidecar for research and outreach. There are no production systems,
no real operational data, and no paid infrastructure in scope. Reports about
the prototype code, the hosted demo, and the docs are welcome; everything
else is almost certainly out of scope.

## Supported versions

| Version | Supported |
| ------- | --------- |
| v0.1.x (`main`) | Best effort |

## Reporting a vulnerability

Email **chanaleze@live.com** with:

- what is affected (file/endpoint/commit or demo URL),
- steps to reproduce using **sample data only** (`examples/sample-flight-plans/`),
- what you think the impact is.

Please do **not** include real operational flight data, credentials, private
keys, or other sensitive material — if you have those, you already have a
bigger problem than this repo. Do not test third-party hosting itself
(Vercel, GitHub); report platform issues to the platform.

Acknowledgement is best-effort, typically within a week. There is no bounty —
this is an unfunded research prototype, and the most useful reports are the
ones that make the demo or the recovery story more honest.

## Out of scope

- Social engineering, phishing, or physical attacks.
- Denial-of-service against the free-tier demo (rate limits are the host's job).
- Findings that require a production deployment to matter — none exists.
- Claims about ATC safety impact: the ledger never touches the real-time
  safety path by design (see `docs/PROJECT-PROFILE-AND-WAY-FORWARD.md` §6),
  so "compromising the demo affects flight safety" is not a valid impact
  statement. Saying so misunderstands the architecture; the report is still
  welcome for the integrity mechanics themselves.
