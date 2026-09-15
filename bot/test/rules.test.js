const test = require("node:test");
const assert = require("node:assert/strict");
const { BOT_MARKER, PR_MARKER, isFirstTimer, labelsForText } = require("../lib/rules");

test("first-timer associations", () => {
  assert.equal(isFirstTimer("FIRST_TIMER"), true);
  assert.equal(isFirstTimer("FIRST_TIME_CONTRIBUTOR"), true);
  assert.equal(isFirstTimer("CONTRIBUTOR"), false);
  assert.equal(isFirstTimer("MEMBER"), false);
  assert.equal(isFirstTimer(undefined), false);
});

test("labels documentation issues", () => {
  assert.deepEqual(labelsForText("Fix typo in README", "correct the guide"), ["documentation"]);
  assert.deepEqual(labelsForText("Add changelog entry", ""), ["documentation"]);
});

test("labels bugs and questions", () => {
  assert.ok(labelsForText("Crash on verify-chain", "").includes("bug"));
  assert.ok(labelsForText("How do I run the demo?", "").includes("question"));
});

test("labels demo topics", () => {
  assert.ok(labelsForText("Deploy demo to Vercel", "").includes("demo"));
});

test("workflow labels need explicit phrases", () => {
  assert.deepEqual(labelsForText("Small cleanup", "might suit a newcomer"), []);
  assert.ok(labelsForText("Small cleanup", "good first issue for newcomers").includes("good first issue"));
  assert.ok(labelsForText("Need help wanted here", "").includes("help wanted"));
});

test("no labels for unrelated text", () => {
  assert.deepEqual(labelsForText("Refactor writer internals", "no user-facing change"), []);
});

test("markers are stable HTML comments", () => {
  assert.match(BOT_MARKER, /^<!-- [\w-]+ -->$/);
  assert.match(PR_MARKER, /^<!-- [\w-]+ -->$/);
  assert.notEqual(BOT_MARKER, PR_MARKER);
});
