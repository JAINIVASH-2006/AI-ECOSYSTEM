# EcoRestore — run and deploy

## Local web app

Install Node.js 22.12+ or a supported later LTS release.

```sh
cd frontend
npm ci
cp .env.example .env.local
# Fill in the new project's URL and publishable key.
npm run dev
```

Without environment variables, public exploration still works and account access clearly reports that setup is pending. `npm test` runs scoring/planning tests; `npm run build` emits `frontend/dist`. To inspect a build: `python -m http.server 5173 --directory frontend/dist` from the repository root.

The original research application remains available with `pip install -r requirements.txt` and `streamlit run app.py`. It is a separate local research app; it does not gain Supabase authentication from the browser implementation and must not be published as a protected backend without additional server-side work.

## Supabase

1. Create a new project in the organization confirmed by the owner. Do not use the unrelated inactive project.
2. Run `supabase/schema.sql` in its SQL editor. It creates `eco_plans`, owner-scoped CRUD policies, explicit grants and RLS. Keep this file in version control; after live validation, capture a migration with the Supabase CLI rather than inventing a migration history.
3. Enable the email provider. Retain email confirmation. Configure Site URL and the exact redirect URL to the deployed Pages URL including its repository path and trailing slash. Also allow the localhost URL used for development. Use the same browser to complete PKCE email links.
4. Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY`. These are public frontend configuration. Never put secret or service-role keys in frontend variables or GitHub Pages.
5. Configure production email delivery in Supabase before inviting users; confirm signup and recovery delivery and rate limits on the chosen plan.
6. Run the live acceptance checks below. Client route guards are navigation controls; RLS is the data security boundary. The public synthetic dataset intentionally requires no account.

## GitHub Pages

Create or provide an empty target repository. Upload source while respecting `.gitignore`; do not upload `node_modules`, SQLite, private data, `.env` files, model binaries or generated local outputs. Set the default branch to `main`.

Repository Settings → Secrets and variables → Actions → Variables:

- `VITE_SUPABASE_URL`: the project API URL
- `VITE_SUPABASE_PUBLISHABLE_KEY`: its publishable key

Settings → Pages → Source → GitHub Actions. Push to `main` or run the included `Deploy EcoRestore to GitHub Pages` workflow. It tests and builds the app, then publishes only `frontend/dist`.

Pages hosts static HTML/CSS/JavaScript. It does not execute Python or Streamlit. This release runs the baseline score in-browser and uses Supabase for accounts/private plans. Python model inference needs a separate authenticated service if added later.

## Required live acceptance checks

- Signup requires confirmation; confirm link opens the exact deployed subpath.
- Sign in, reload protected routes and sign out. Signed-out `#workspace` and `#plans` redirect to `#auth` without displaying private data.
- Password reset delivers a link; recovery opens the new-password form; the new password works.
- User A saves a plan. User B cannot SELECT, UPDATE or DELETE it via direct REST calls using B's token, and cannot INSERT a row with A's owner ID.
- An unauthenticated request cannot read/write `eco_plans`.
- Failed/expired sessions do not grant workspace access; errors remain visible.
- Save, reload, status update and deletion work with a real user.
- Inspect Supabase security advisors after schema application.
- Open the deployed Pages URL and reload hash routes. Confirm no missing assets or console errors.

## Automated verification

- 35 original + regression Python tests passed (`python -m pytest tests -q`).
- 4 browser engine unit tests passed (`cd frontend && npm test`).
- Production builds succeeded both without auth configuration and with a placeholder test configuration. No placeholder configuration is committed or included in the distribution build.
- Live Supabase and GitHub deployment are pending the account/project choices described above.
