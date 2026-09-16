# flight-plan-ledger-bot

Probot app that makes the repo feel maintained: welcomes first-time
contributors, auto-labels issues/PRs, and posts a demo + safety checklist on
every PR. Stale handling lives in `.github/workflows/stale.yml` (Probot has
no scheduler — the workflow is the right tool for that job).

## What it does

| Event | Action |
|---|---|
| `issues.opened` | Applies keyword labels (`documentation`, `bug`, `question`, `demo`); welcomes first-time reporters |
| `pull_request.opened` | Applies keyword labels; posts one comment with the local demo command, the safety note, and the PR checklist (skipped if already posted) |

Labels `good first issue` / `help wanted` are applied when the issue text
contains those phrases — i.e. maintainers opt issues in by writing them.
Native issue/PR templates under `.github/` carry the same checklist and
labels, so contributors get guidance even before the bot is installed.

## Run locally

```bash
cd bot
npm install
cp .env.example .env   # fill in APP_ID / key / secret (see Register below)
npm start              # http://localhost:3000/probot
npm test               # pure-logic tests, no credentials needed
```

Webhook testing from localhost needs a public URL: create a channel at
[smee.io](https://smee.io), set
`WEBHOOK_PROXY_URL=<smee-url>` in `.env`, and use the smee URL as the app's
webhook URL. (ngrok works too — see `ops/NGROK-RUNBOOK.md`, Procedure A.)

## Register & install (one time, ~10 min)

Full preserved procedure: [`INSTALL.md`](INSTALL.md) — follow it when the
repo has real external traffic, not before. Short version:

1. GitHub → Settings → Developer settings → GitHub Apps → **New GitHub App**,
   or open `http://localhost:3000/probot/setup` while the bot runs.
2. Feed it `bot/app.yml` (manifest flow), replacing `hook_attributes.url`
   with the bot's public URL (smee URL for testing, real host URL for prod).
3. Download the private key into `bot/` (it is `*.pem`-ignored, never commit it),
   set `APP_ID`, `PRIVATE_KEY_PATH`, `WEBHOOK_SECRET`, restart.
4. On the app's page: **Install App** → select `Chanaleze/flight-plan-ledger`.

## Hosting

The bot needs an always-on HTTPS endpoint (it cannot run on GitHub Pages).
Free-tier options: Render, Railway, or Fly.io web service running
`npm start` with the three env vars above. Redeploy on `main` is enough —
the bot is stateless.

## Security hygiene

- The private key and webhook secret live **only** in `bot/.env` / host env —
  never in git (see `.opencode/skills/ops-security-hygiene/SKILL.md`).
- Requested permissions are minimal: read metadata, write issues + PRs
  (comments and labels only). The bot never touches code, secrets, or data.
