# ADR 0004 – Public Demo Architecture

## Status

Accepted (September 2026).

## Context

For technical outreach we need a “try it in 30 seconds” demo: upload a sample
plan, see hash + signature, verify, run a recovery view. It must run on free
hosting, reuse the real prototype logic (not a mock), and — critically — never
put a real writer private key, operational data, or persistent state on a
free host.

## Decision

- **Static dependency-free frontend** (`demo/`: `index.html` + `styles.css` +
  `hash.js` + `app.js`, no build step) served from the same deployment.
- **One stateless Python serverless function** (`api/demo.py`, Vercel) that
  adapts `src/flight_plan_ledger/demo_service.py` — a pure-function façade
  over the real modules (canonicalization, Ed25519, chain walk, recovery).
- **Ephemeral keys**: a fresh keypair per `sign` call, private half discarded
  immediately; demo-only markers forced server-side (`org:demo`,
  `metadata.demo=true`, `demo-ephemeral-` key IDs).
- **No persistence**: the session chain lives in the visitor’s browser and is
  sent with each request; strict size/count limits bound free-tier abuse.
- **Browser hash mirror** (`demo/hash.js`) pinned by a byte-exact parity check
  against the Python canonicalization; the server hash stays authoritative.
- **Vercel** as the default host (native Python functions on the free tier);
  the demo endpoint (`/api/demo`) is explicitly separate from the product API,
  which remains an unimplemented sketch.

## Consequences

- The demo is cheap, portable, and honest: everything a visitor sees is
  produced by the real ledger code paths with throwaway keys.
- Demo entries are self-evidently non-operational; they cannot leak into any
  real trust domain (there is none — the prototype is local-only).
- The JS mirror is demo-only surface: any canonicalization change must update
  it **and** re-run the parity check (see `docs/demo.md`).
- Free-tier limits (cold starts, execution caps) are acceptable for a
  click-through demo and are documented as non-goals.

## Alternatives

- **Full JS port (hash + Ed25519 in browser, e.g. tweetnacl)** — rejected:
  signing in the browser normalizes key handling downwards and a second
  implementation of signature logic can silently diverge from the Python
  prototype it is supposed to demonstrate.
- **Persistent backend (DB + accounts)** — rejected: cost, abuse surface, and
  statefulness contradict the sidecar’s low-ops stance for a demo.
- **Netlify-only hosting** — rejected as default: no native Python functions,
  which would force the full-JS-port alternative above.
- **GitHub Pages only** — rejected: serves the docs site well but provides no
  compute for the real Python logic.
