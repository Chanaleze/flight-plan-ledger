# Public Interactive Demo

**Live demo:** TBD — paste the Vercel URL here after the first deploy
(then link it from `docs/index.md` and the root `README.md`).

A 30-second, no-signup browser demo of the ledger: load a sample flight plan,
see its canonical form + hash, record it with an ephemeral demo key, verify it,
tamper with it, then simulate an outage and recover. It reuses the **real**
prototype logic — not a mock.

## Architecture

```
browser (demo/, static, no build step)
  │  hash.js  — byte-exact mirror of canonicalization (tested, see below)
  │  app.js   — UI; the session chain lives only in page memory
  ▼  POST /api/demo  {action, ...}   (same origin; overridable via ?api=…)
serverless function (api/demo.py → src/flight_plan_ledger/demo_service.py)
  │  hash         canonical form + plan hash (no keys involved)
  │  sign         ONE demo entry with a fresh ephemeral keypair
  │  verify       plan vs entry + signature (read-only)
  │  verify_chain hash-link walk + signature checks (read-only)
  │  recover      last-known-good accepted set (read-only)
```

This is **not** the product API — that remains an unimplemented sketch
(`contracts/openapi-sketch.yaml`). The demo endpoint is deliberately separate
(`/api/demo`) and demo-only.

## Security model (non-negotiable — see ADR 0004)

1. **Ephemeral keys only.** Each `sign` call generates a fresh Ed25519 keypair
   in memory; the private key is never returned, logged, or stored.
   No real writer key exists on, or is ever sent to, the hosted demo.
2. **Demo entries are unmistakable.** The service forces
   `submitter_id="org:demo"` and `metadata.demo=true`, and key IDs carry a
   `demo-ephemeral-` prefix. A demo entry can never be mistaken for an
   operational record.
3. **No persistence.** Chain state lives in the visitor's browser; every call
   is a pure function of its JSON input. No database, no sessions, no cookies.
4. **Bounded abuse surface.** Plans ≤ 8 KB, entries ≤ 16 KB, chains ≤ 64
   entries, bodies ≤ 256 KB. Request bodies are never logged; error responses
   are generic (`no-store` everywhere).
5. **Nothing secret ships.** `.vercelignore` (plus `.gitignore`) keeps keys,
   `data/`, recovery exports, and local ledgers out of deployments.
   Before any share, run the checks in
   `.opencode/skills/ops-security-hygiene/SKILL.md`.

## Browser hash mirror

`demo/hash.js` reimplements canonicalization in dependency-free JavaScript so
visitors see the hash computed locally. It is pinned by a byte-exact parity
check against the Python implementation (all sample plans + edge cases:
offsets, microseconds, unicode, rejections). Re-run after any
canonicalization change:

```bash
# 1. Dump parity vectors from the real Python implementation
.\.venv\Scripts\python.exe -c "
import sys, json; sys.path.insert(0, 'src')
from flight_plan_ledger.models.canonical import normalize_flight_plan
cases = {}
for f in ['examples/sample-flight-plans/qtr23_doha_lhr.json','examples/sample-flight-plans/baw12_lhr_jfk.json','examples/sample-flight-plans/ezy8567_lgw_pmi.json']:
    cases[f] = json.load(open(f, encoding='utf-8'))
base = {'callsign':'T1','aircraft_id':'G-1','dof':'2026-09-09','origin':'EGLL','destination':'KJFK'}
for name, extra in [
  ('lower', {'callsign':' qtr23 ','aircraft_id':'a7-baa','dof':'2026-09-09','origin':'othh','destination':'egll','departure_time_utc':'2026-09-09T07:30:00+00:00','route':'X','junk':'dropped'}),
  ('offset', dict(base, departure_time_utc='2026-09-09T10:15:00+02:00')),
  ('micro', dict(base, departure_time_utc='2026-09-09T10:15:30.123456+00:00')),
  ('frac1', dict(base, departure_time_utc='2026-09-09T10:15:00.1Z')),
  ('nosecs', dict(base, departure_time_utc='2026-09-09T10:15')),
  ('minimal', dict(base)),
  ('unicode', dict(base, route='Zürich–Genève ✓')),
  ('explicit-null-route', dict(base, route=None, departure_time_utc=None)),
]:
    cases[name] = extra
rejects = [
  ('null-schema', dict(base, schema_version=None)),
  ('short-dof', dict(base, dof='2026-9-9')),
  ('bad-dt', dict(base, departure_time_utc='tomorrow')),
  ('missing-id', {'aircraft_id':'G-1','dof':'2026-09-09','origin':'EGLL','destination':'KJFK'}),
  ('int-id', dict(base, callsign=42)),
]
out = {}
for name, raw in cases.items():
    p = normalize_flight_plan(raw)
    out[name] = {'raw': raw, 'canonical': p.canonical_bytes().decode('utf-8'), 'hash': p.content_hash()}
for name, raw in rejects:
    try:
        normalize_flight_plan(raw); raise SystemExit('server accepted ' + name)
    except SystemExit: raise
    except Exception: out['must-reject:'+name] = {'raw': raw}
json.dump(out, open('parity.json','w', encoding='utf-8'), ensure_ascii=False)
print(len(out), 'cases written')
"

# 2. Compare in Node (must print "16 passed, 0 failed")
node -e "
const fs = require('fs');
const fpl = require('./demo/hash.js');
const cases = JSON.parse(fs.readFileSync('./parity.json', 'utf8'));
(async () => {
  let pass = 0, fail = 0;
  for (const [name, c] of Object.entries(cases)) {
    if (name.startsWith('must-reject:')) {
      try { fpl.canonicalJson(c.raw); console.log('REJECT-FAIL(js accepted):', name); fail++; }
      catch (e) { pass++; }
      continue;
    }
    try {
      const canon = fpl.canonicalJson(c.raw);
      const hex = await fpl.sha256Hex(canon);
      if (canon === c.canonical && ('sha256:' + hex) === c.hash) pass++;
      else { fail++; console.log('MISMATCH:', name, '\n  js :', canon, '\n  py :', c.canonical); }
    } catch (e) { fail++; console.log('THREW:', name, e.message); }
  }
  console.log(pass + ' passed, ' + fail + ' failed');
  process.exit(fail ? 1 : 0);
})();
"
```

The server hash is always authoritative; if the two ever disagree the UI says so.

## Deploy (Vercel, free tier)

No environment variables, no database, no build step.

```bash
npm i -g vercel
vercel          # preview deployment, follow the prompts
vercel --prod   # production deployment
```

Then open `https://<your-app>.vercel.app/demo/` and paste the URL at the top
of this page. A custom domain can be added later in the Vercel dashboard
(free TLS included).

Alternative hosts: any static host serves `demo/` for the hash step, but the
sign/verify/recover steps need a Python host for `/api/demo`. Netlify has no
native Python functions, which is why Vercel is the default (ADR 0004).

## Local preview

```bash
# full stack (static + function)
vercel dev        # then open http://localhost:3000/demo/

# static only (hash step works, API steps show the unreachable note)
npx serve .       # then open /demo/ and pass ?api=<deployed-url>/api/demo
```

## Non-goals

- The demo proves **integrity mechanics** (hash → sign → verify → recover),
  not operational readiness, performance, or multi-party consensus.
- It must never accept real operational plans, real keys, or PII — sample
  data only, enforced by design (ephemeral keys, forced `org:demo`).
- No feature may require server-side state, accounts, or secrets.
