## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/101

**Issue title:** Add a "Copy link" button to share a public review summary (101)

**Tier:** [ ] Tier 1 [x] Tier 2 [ ] Tier 3

I have experience with React and TypeScript, and I am familiar with the basics of web development, as well as have worked in shared codebases before, so I believe I am experienced enough for a tier 2 issue.

I also recognize I will have to create a new route (API endpoint) in `reviews.py` to handle the link generation, connect it to a service that actually creates the link, and then add a physical button to the UI on the `ReviewPage` that calls that service.

**Problem summary:**
The issue is requesting a button be added to the UI that allows the user to create a link they can share with others of their review summary. The link should be to a read-only version of their review summary that does not require authentication and expires after 30 days. The button should say "Copy Link" and be placed on the review summary page of the app.

**Branch name:** feat/101-add-copy-link-button

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/IDLinares/pathreview/commit/c6fcdba8ec3f64edd09c970569163cd309517543

**Reproduction summary:**
First, I manually tested the "Share" button that is currently available on the review page and saw it simply copied the URL of the current page, so it is not performing the intended functionality of creating a public link to the review page that expires after 30 days.

As such, I created two new test files to test the functionality and implementation of this feature for when it is completed: a file for the eventual share service in the backend that creates the share link, and a file for the frontend that calls the share service and copies the link to the clipboard.

**PLAN.md link:** [PLAN.md](PLAN.md)

**Walkthrough video (recommended):** No link

**Blockers or open questions:**
No blockers or open questions.
