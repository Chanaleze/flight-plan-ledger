# Installing the bot — full procedure (run when needed, not before)

> Saved procedure. Follow it when the repo has real external traffic
> (outreach replies, outside contributors) — not before. Until then the
> scaffold, templates, and CI carry the load for free.

## When to install

- At least one outside person is opening issues/PRs (or about to), **and**
- GitHub account in good standing (Actions must run — the bot is useless
  without delivery logs to debug from), **and**
- You have ~30 minutes for register → host → verify below.

If any of these is false, stop here. Nothing rots by waiting.

## A. Register the GitHub App (~10 min)

1. On your machine: `cd bot && npm install` (once), then `npm start`.
   It boots into Probot setup mode — this is expected before registration.
2. Open `http://localhost:3000/probot/setup` → **Register GitHub App**.
   Use `bot/app.yml` as the manifest source (name, description, permissions
   `issues:write` + `pull_requests:write` + `metadata:read`, events `issues`
   + `pull_request` are pre-filled there).
3. For the webhook URL at registration time, use a temporary
   [smee.io](https://smee.io) channel URL (see step B) — you will replace it
   with the host URL in step C.
4. GitHub generates the app: download the **private key** (`.pem`) into
   `bot/` — it is git-ignored, verify with `git status` that it stays out —
   and note the **App ID**.
5. Fill `bot/.env` (copy from `.env.example`):
   `APP_ID`, `PRIVATE_KEY_PATH=./<your-file>.private-key.pem`,
   `WEBHOOK_SECRET` (the same secret you set on the app), `PORT=3000`.
6. Restart `npm start` — setup mode should be gone.

## B. Prove webhooks work locally (~5 min)

1. Still running locally, set `WEBHOOK_PROXY_URL=<your-smee-url>` in
   `bot/.env` and restart (Probot forwards smee → localhost).
2. Open a **test issue** titled e.g. `[question] install probe — will close`:
   expect the `question` label within seconds; if your test account is a
   first-timer, expect the welcome comment too.
3. Open a **test PR** from a scratch branch: expect keyword labels (if any
   match) plus exactly **one** checklist comment. Push another commit:
   expect **no** second comment (once-only marker).
4. Close/delete the probes. If anything misbehaves, the bot log + the smee
   inspector show every delivery — fix forward, never by hand-editing on GitHub.

## C. Host it always-on (~10 min)

The bot needs a persistent HTTPS endpoint. Any free tier that runs
`npm start` with the four env vars works — Render, Railway, or Fly.io:

1. Create a **Web Service** from the repo (root is fine; set start command
   `npm --prefix bot start`, or set the service root to `bot/` and use
   `npm start`). Node 20+.
2. Add environment variables on the host (same four as `.env`): `APP_ID`,
   `PRIVATE_KEY` (paste the **contents** of the `.pem` — most hosts prefer
   this over a file; if yours takes files, upload it as a secret file and
   keep `PRIVATE_KEY_PATH`), `WEBHOOK_SECRET`, `PORT` (host-assigned).
3. Deploy, note the public URL, e.g. `https://fpl-bot.onrender.com`.
4. Back on the GitHub App settings page, replace the smee webhook URL with
   `<host-url>/api/github/webhooks`. Keep the secret identical.
5. Honest free-tier caveat: free services sleep when idle, so the first
   event after a quiet spell can be slow or time out — GitHub shows the
   delivery status; re-trigger the event if needed. Acceptable for a
   welcome/labels bot; revisit only if it ever misses something that mattered.

## D. Install on the repo (~2 min)

GitHub App page → **Install App** → select `Chanaleze/flight-plan-ledger`
(this repo only — never "All repositories") → confirm permissions
(read metadata; read/write issues + pull requests).

## E. Verify in production (~5 min)

1. Repeat the B probes (test issue + test PR) against the live install.
2. Confirm in the host logs that deliveries arrive without smee.
3. Confirm the stale workflow is separate and running (Actions tab).
4. Close/delete probes, log the install in `ops/TASK-LOG.md` (date, host URL,
   app ID).

## F. If it ever misbehaves

1. Check host logs first, GitHub App "Deliveries" tab second.
2. Silence quickly without uninstalling: App settings → suspend, or remove
   the webhook URL; native issue/PR templates keep guiding contributors.
3. Uninstall path: App page → Uninstall from the repo. No repo changes needed
   — the bot never touches code, only comments and labels, all marked
   `<!-- fpl-bot -->` and deletable.
