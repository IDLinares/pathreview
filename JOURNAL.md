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

## Week 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:**
I have implemented all of the backend functionality for the "Copy Link" button feature as documented in the [PLAN.md](PLAN.md) file. I updated the `Review` model to include new columns for the shareable link token and expiration date and well as performed the migration to add the new columns to the database. Also, two new async functions were created in `core/services/share_service.py` to handle the creation and retrieval of the shareable link. Lastly, two new routes were created: one in `api/routes/reviews.py` to handle the creation of the shareable link and another in `api/routes/public.py` to handle the retrieval of the public review summary along with schemas for the responses from the two new endpoints. Unit tests were also created and ran for this new service and all tests have passed.

**Next steps:**
The rest of the week will be spent working on the frontend functionality, testing, and preparing the PR.

**Blockers:**
Since this is a full-stack feature, some changes have caused linter errors and warnings in areas downstream in files unrelated to the feature I am working on. I have had to work around them by updating type declarations for functions in the same file that might be unrelated to my feature and silence the linter for files that were downstream of changes in my current file. These errors already existed in the codebase but are now being caught by the linter due to an import in a staged file, such as `main.py`.

---

### Check-in 2 (end of week)

**PR link:** [link to your submitted pull request]

**Branch:** [the branch name you worked on, e.g. `fix/123-short-description`]

**What you built:**
[1–3 sentences summarizing what your fix does and how it works]

**Tests added or updated:**
[Which test files did you touch? What do they cover?]

**Self-review confirmation:** [ ] make check passes [ ] make test-unit passes

**Draft PR feedback received from:** [name or Slack handle, or "none"]
