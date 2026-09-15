/**
 * Pure decision rules for the bot (no Probot/octokit imports).
 * Covered by `npm test` (node:test) — keep framework glue in index.js.
 */

const BOT_MARKER = "<!-- fpl-bot -->";
const PR_MARKER = "<!-- fpl-pr-checklist -->";

/** GitHub author_association values that mean "first contribution". */
function isFirstTimer(association) {
  return association === "FIRST_TIMER" || association === "FIRST_TIME_CONTRIBUTOR";
}

/** Keyword rules mapping issue/PR text to labels. Maintainers can force the
 *  workflow labels by writing the phrases "good first" / "help wanted". */
const LABEL_RULES = [
  { label: "documentation", any: [/\bdocs?\b/, /readme/, /typo/, /guide/, /changelog/] },
  { label: "bug", any: [/\bbug\b/, /error/, /crash/, /broken/, /regression/, /fails?\b/] },
  { label: "question", any: [/\bquestion\b/, /how (do|to|can)/, /why does/] },
  { label: "demo", any: [/\bdemo\b/, /vercel/, /netlify/, /website/, /pages\b/, /frontend/] },
  { label: "good first issue", any: [/good first/] },
  { label: "help wanted", any: [/help wanted/] },
];

function labelsForText(title, body) {
  const text = `${title || ""}\n${body || ""}`.toLowerCase();
  const labels = [];
  for (const rule of LABEL_RULES) {
    if (rule.any.some((re) => re.test(text))) labels.push(rule.label);
  }
  return labels;
}

module.exports = { BOT_MARKER, PR_MARKER, isFirstTimer, labelsForText };
