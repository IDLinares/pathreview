## Solution plan

**Issue:** Add a "Copy link" button to share a public review summary (101) - https://github.com/ascherj/pathreview/issues/101

### Understand

The current "Share" button on the review page calls the `handleShare` function in `ReviewPage.tsx` which simply grabs the current URL and writes that URL to the clipboard ( `window.location.href -> navigator.clipboard.writeText(url)` ) without any concern for authentication, access control, or expiration.

The expected behavior: Clicking a "Copy Link" (would replace the share button) button should call a backend service that creates a shareable link (does not require authentication) to a read-only view of the review sumamry and that link should be copied to the clipboard.

**Root cause:** There is no backend service that handles creation of a public-view endpoint for review summaries to share with others.

### Map

Files I expect to touch:

- `frontend/src/pages/ReviewPage.tsx` - `handle_share()` function (~ line 32): Will replace the current url creation and instead all the API service to either create a new shareable link or fetch an existing link and copy the link to the clipboard.
- `frontend/src/services/api.ts` - File where I will be adding the method that calls the API to create the shareable link and the method that retrieves the public review summary without the authorization header.
- `frontend/src/types/index.ts` - File where I will be adding a new type for the shareable link response since a link needs to have a token and expiration date associated with it.
- `frontend/src/App.tsx` - File where I will be adding a new route to the app that will be the public review summary page (without the ProtectedRoute wrapper).
- `api/routes/reviews.py` - File where endpoints dealing with reviews are implemented. I will be adding a new endpoint to this file that will create the shareable link since this is an owner-only, auth-protected operation on a review summary similar to other endpoints in this file.
- `api/schemas/review.py` - File where I will be adding the schema for the shareable link response since a link needs to have a token and expiration date associated with it.
- `api/main.py` - File where I will be adding the new public router for the public review summary page.
- `core/models/review.py` - File where I need to add a new column to the existing Review model to store the shareable link token and expiration date.
- `frontend/src/pages/__tests__/` - Directory where I will be creating unit tests for the frontend functionality of the "Copy Link" button feature.
- `tests/unit` - Directory where I will be creating unit tests for the backend functionality of the "Copy Link" button feature.

Files I expect to create:

- `public.py` file in `api/routes/` directory: This file will contain the unauthenticated endpoint to the read-only public review summary separate from the other endpoints in the `reviews.py` file.
- `shared_service.py` file in `core/services/` directory: This file will contain functions to create and retrieve the shareable link (what the tests files for the feature will be tested against).
- `PublicReviewPage.tsx` file in `frontend/src/pages/` directory: This file will contain the public, read-only version of the review page that will be accessible without authentication (no share/export/edit buttons).

### Plan

**Backend:**

1. Update the `Review` model to include new columns for the shareable link token and expiration date of the token, as well as run a migration to add the new columns to the database.
2. Create a new file in `core/services/` (potentially `shared_service.py`) with 2 new functions: one to create the shareable link (with the token and expiration date) and the other to actually retrieve the page of the public review summary.
3. Create a new route in `api/routes/reviews.py` to handle the creation of the shareable link. Specifically, an authenticated POST endpoint that should call the service that creates the link and returns the token and expiration date.
4. Add two new schema classes in `api/schemas/review.py` to handle the response of the shareable link creation endpoint and the endpoint for the public review summary page.
5. Create a new file in `api/routes/` (potentially `public.py`) with an unauthenticated endpoint to the public review summary page. It should call the service to retrieve the public review summary.
6. Add the new `public` route to the `api/main.py` file.

**Frontend:**

1. Replace the current "Share" button on the `frontend/src/pages/ReviewPage.tsx` file with a "Copy Link" button that calls the new API endpoint to create the shareable link and copies the public URL link to the clipboard.
2. Create a new route in `frontend/src/App.tsx` to access the public review summary page without authentication.
3. Create a new page in `frontend/src/pages` (potentially `PublicReviewPage.tsx`) that reads the token from the URL parameters and calls the service to retrieve the public review summary. This should render a read-only version of the review page that does not require authentication and does not have the share or exportbuttons.
4. Add a new type in `frontend/src/types/index.ts` to handle the response of the shareable link creation endpoint (should include the token and expiration date).

**Testing:**

1. Create and run backend tests for the two new functions in `core/services/shared_service.py` to ensure they work as expected.
2. Create and run frontend tests for the "Copy Link" button feature in `frontend/src/pages/__tests__/ReviewPage.test.tsx` to ensure the button works as expected and the page is rendered correctly.
3. Run `make test-unit` to ensure all other tests pass and the new feature did not brea anything unexpectedly.
4. Run `make check-lint` to ensure all linting rules, formatting rules, and type checking rules are satisfied.

### Inputs & outputs

What does your fix take as input? What should it produce or change?

### Risks & unknowns

What could go wrong? What are you still unsure about?

### Edge cases

What inputs or states should your fix handle gracefully?
