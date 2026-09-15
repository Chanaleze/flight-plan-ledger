/**
 * flight-plan-ledger-bot — Probot app.
 *
 * Event-driven automations (welcome, labels, PR checklist). Stale handling is
 * intentionally NOT here — Probot has no scheduler — see
 * .github/workflows/stale.yml instead.
 */
const { PR_MARKER, isFirstTimer, labelsForText } = require("./lib/rules");
const { welcomeIssue, prBody } = require("./lib/copy");

async function alreadyCommented(context, number, marker) {
  const { data: comments } = await context.octokit.rest.issues.listComments({
    ...context.repo(),
    issue_number: number,
  });
  return comments.some((c) => (c.body || "").includes(marker));
}

module.exports = (app) => {
  app.log.info("flight-plan-ledger-bot loaded");

  app.on("issues.opened", async (context) => {
    if (context.isBot) return;
    const issue = context.payload.issue;

    const labels = labelsForText(issue.title, issue.body);
    if (labels.length) {
      await context.octokit.rest.issues.addLabels({
        ...context.repo(),
        issue_number: issue.number,
        labels,
      });
      app.log.info(`labeled #${issue.number}: ${labels.join(", ")}`);
    }

    if (isFirstTimer(issue.author_association)) {
      await context.octokit.rest.issues.createComment({
        ...context.repo(),
        issue_number: issue.number,
        body: welcomeIssue(issue.user.login),
      });
      app.log.info(`welcomed first-time reporter on #${issue.number}`);
    }
  });

  app.on("pull_request.opened", async (context) => {
    if (context.isBot) return;
    const pr = context.payload.pull_request;

    const labels = labelsForText(pr.title, pr.body);
    if (labels.length) {
      await context.octokit.rest.issues.addLabels({
        ...context.repo(),
        issue_number: pr.number,
        labels,
      });
      app.log.info(`labeled PR #${pr.number}: ${labels.join(", ")}`);
    }

    // One comment per PR: welcome (first-timers) + checklist + demo/safety note.
    if (await alreadyCommented(context, pr.number, PR_MARKER)) return;
    await context.octokit.rest.issues.createComment({
      ...context.repo(),
      issue_number: pr.number,
      body: prBody(pr.user.login, isFirstTimer(pr.author_association)),
    });
    app.log.info(`posted PR checklist on #${pr.number}`);
  });
};
