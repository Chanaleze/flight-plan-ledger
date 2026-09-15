const test = require("node:test");
const assert = require("node:assert/strict");
const { DEMO_COMMAND, TEST_COMMAND, welcomeIssue, prBody } = require("../lib/copy");

test("welcome message stays modest and actionable", () => {
  const msg = welcomeIssue("octocat");
  assert.ok(msg.includes("@octocat"));
  assert.ok(msg.includes(DEMO_COMMAND));
  assert.ok(msg.includes("demonstration-grade prototype"));
  assert.ok(msg.includes("<!-- fpl-bot -->"));
});

test("PR body has demo command, safety note, and checklist", () => {
  const msg = prBody("octocat", false);
  assert.ok(msg.includes("@octocat"));
  assert.ok(!msg.includes("first PR"));
  assert.ok(msg.includes(DEMO_COMMAND));
  assert.ok(msg.includes(TEST_COMMAND));
  assert.ok(msg.includes("never decides"));
  assert.ok(msg.includes("no DAL"));
  assert.ok(msg.includes("<!-- fpl-pr-checklist -->"));
  for (const item of ["Tests pass", "No secrets", "Docs updated", "ADRs added", "One concern"]) {
    assert.ok(msg.includes(item), `missing checklist item: ${item}`);
  }
});

test("PR body welcomes first-timers", () => {
  const msg = prBody("newbie", true);
  assert.ok(msg.includes("first PR"));
  assert.ok(msg.includes("<!-- fpl-pr-checklist -->"));
});
