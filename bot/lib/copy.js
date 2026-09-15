/**
 * Message builders for the bot (pure functions, no side effects).
 * Tone: quiet technical outreach — modest claims, no safety over-claims.
 */

const { BOT_MARKER, PR_MARKER } = require("./rules");

const DEMO_COMMAND = "PYTHONPATH=src python -m flight_plan_ledger.cli.main demo";
const TEST_COMMAND = "python -m pytest tests -q";

function welcomeIssue(username) {
  return (
    `${BOT_MARKER}\n` +
    `Thanks for opening your first issue, @${username} — welcome!\n\n` +
    `Context that helps us respond fast: what you ran (the end-to-end CLI demo is ` +
    `\`${DEMO_COMMAND}\`), what you expected, and what you saw instead.\n\n` +
    `Note: this is a demonstration-grade prototype (an integrity sidecar, not an ` +
    `ATC system), so reports about the demo, docs, and recovery tooling are the ` +
    `most actionable right now.`
  );
}

function prBody(username, firstTimer) {
  const greeting = firstTimer
    ? `Thanks for your first PR, @${username} — welcome aboard!\n\n`
    : `Thanks for the PR, @${username}!\n\n`;
  return (
    `${BOT_MARKER}\n${PR_MARKER}\n` +
    greeting +
    `**Try it locally** (what reviewers will run):\n` +
    `\`\`\`bash\n${DEMO_COMMAND}\n${TEST_COMMAND}\n\`\`\`\n\n` +
    `**Safety note:** this project is a demonstration-grade integrity sidecar — ` +
    `it observes and remembers, never decides. Please keep claims modest: no DAL ` +
    `compliance, separation assurance, capacity management, or production ` +
    `readiness (see \`docs/PROJECT-PROFILE-AND-WAY-FORWARD.md\` §6).\n\n` +
    `**Checklist** (tick before requesting review):\n` +
    `- [ ] Tests pass: \`${TEST_COMMAND}\`; coverage kept at 100% for touched code\n` +
    `- [ ] No secrets: no private keys (\`.pem\`/\`.key\`), \`data/\`, or recovery exports\n` +
    `- [ ] Docs updated alongside code (\`docs/\` + \`tests/test_docs.py\` guardrail where apt)\n` +
    `- [ ] ADRs added for architecture / trust / data-handling decisions\n` +
    `- [ ] One concern per change; no safety or operational over-claims`
  );
}

module.exports = { DEMO_COMMAND, TEST_COMMAND, welcomeIssue, prBody };
