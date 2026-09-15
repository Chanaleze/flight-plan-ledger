# ngrok Runbook — temporary exposure only (prototype, demo-grade)

> ngrok is a screwdriver, not infrastructure. It exists for two jobs in this
> project and nothing else. Anything that must outlive your work session
> belongs on Vercel (`docs/demo.md`) or GitHub Pages (`docs/_config.yml`).

## When to use this runbook

1. **Testing Probot webhooks locally** — GitHub must reach your laptop's
   `bot/` (`npm start` on `:3000`).
2. **Showing a local demo to one specific reviewer** — a time-boxed screen-share
   companion, not a published link.

## When NOT to use ngrok

- **Public demos.** ngrok free-tier URLs are random and ephemeral; they rot,
  cannot be linked from docs, and vanish when your laptop sleeps. Ship public
  things properly instead.
- **Anything persistent, scheduled, or load-bearing.** If a second person
  depends on the URL tomorrow, it is not an ngrok job.
- **Anything holding secrets.** The tunnel exposes a port on your machine to
  the internet — only ever point it at the demo/bot ports below.

## Preconditions

- A free ngrok account (one tunnel at a time, random URL, session limits —
  enough for an hour-long review, useless as a public link).
- The agent installed and authenticated **via environment, never via repo files**:
  `winget install ngrok.ngrok` (Windows) / `brew install ngrok` (macOS) /
  `snap install ngrok` (Ubuntu/WSL), then
  `ngrok config add-authtoken $env:NGROK_AUTHTOKEN`
  with the token exported in your shell, not pasted anywhere committable
  (`.env` files and tokens are git-ignored — see
  `.opencode/skills/ops-security-hygiene/SKILL.md`).
- A scribe: log the session (URL, purpose, start/stop) in `ops/TASK-LOG.md`.

## Procedure A — Probot webhooks

```powershell
cd bot
npm start                  # confirm "Running Probot" in setup or normal mode
ngrok http 3000            # note the https forwarding URL, e.g. https://abcd-1-2-3-4.ngrok-free.app
```

1. GitHub App settings (or `bot/.env` for local): set the webhook URL to
   `<ngrok-url>/api/github/webhooks` with your `WEBHOOK_SECRET`.
   (smee.io works instead and needs no install — see `bot/README.md`.)
2. Trigger a test event (open a draft issue/PR), watch deliveries land in the
   ngrok inspector (`http://127.0.0.1:4040`) and the bot log.
3. **When done: `Ctrl-C` the tunnel first**, then stop the bot. A forgotten
   tunnel is an open door.

## Procedure B — reviewer demo share

Prefer the full local stack so the reviewer gets hash → sign → verify → recover:

```powershell
vercel dev                 # serves demo/ + /api/demo on :3000 (see docs/demo.md)
ngrok http 3000            # share the https URL + a stop time ("live until 15:00")
```

Static-only fallback (hash step in-browser; API steps need a backend):

```powershell
npx serve .                # share http://localhost:3000/demo/?api=<deployed>/api/demo
```

Tell the reviewer explicitly: sample data only, ephemeral demo keys, nothing
persists, the link dies when you close the tunnel.

## Security rules (non-negotiable)

1. Authtoken in environment only. If a token ever lands in a file, rotate it
   at the ngrok dashboard, delete the file, log it in `ops/TASK-LOG.md`.
2. Expose the single smallest port that does the job (`3000` above) — never
   a file share, database, or anything under `data/`.
3. Assume the URL will be shared beyond your reviewer. There must be nothing
   behind it you would not post publicly.
4. Close the tunnel when the session ends and log stop time in `ops/TASK-LOG.md`.
