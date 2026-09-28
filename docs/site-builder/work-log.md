# Work log

## 2026-09-28 10:10 America/Chicago

Task: Inspected the upstream-aligned fork, created a repository-local website builder workflow, and built a static Holehe project guide. Base: `master` at `14da70f588538936b20d238783c5e28a0772a2b3`.

Created: `site.config.json`, `site/` four routes and stylesheet, `scripts/site-builder/build.py`, `.github/agents/` (orchestrator plus twelve roles), `.github/skills/` (ten stages), `.github/prompts/build-site.md`, `docs/site-builder/` architecture, design, content, deployment and validation docs. Modified: `.gitignore`, `README.md`.

Validation: static route/link/asset/metadata build PASS for four pages; additional checks and PR evidence follow in the session continuation. Blocker: publication requires a deliberate GitHub Pages configuration and owner authorization. Next action: validate branch, open PR, then review deployment choice.

Session continuation: Added `repository-assessment.json` and `.github/workflows/site-check.yml`. Site is COMPLETE for repository-controlled work; public deployment is separately blocked pending hosting authorization. Static build and local-link checks PASS; Python syntax PASS; diff whitespace PASS; no frontend install, lint, or typecheck is required. Browser-based responsive and accessibility review remain limited to source inspection in this environment.

## 2026-09-28 10:20 America/Chicago

Task: Added a loopback-only allowlisted lookup form and backend after owner request. Created `web/server.py`, `site/lookup/`, `tests/test_web.py`, and `.env.example`; updated navigation, site manifest, CI, README, architecture, content, deployment and validation documentation. Validation: five-route static build and mocked local HTTP tests. No third-party live lookups, public backend, or deployment performed. Next action: merge the validated guide PR, then land this feature through its own reviewable PR.

## 2026-09-28 15:45 UTC — Railway preparation

Task: Prepared the selected Railway backend for the existing private Sites interface, preserving the local server and CLI. PRs #1 and #2 are merged; this work starts from `545837cd22e46b3a13f566daa4abcfc905550adc` on `feat/railway-backend`.

Created: `web/hosted.py`, `tests/test_hosted.py`, `requirements-hosted.lock`, `Dockerfile.railway`, `railway.json`, `.dockerignore`, `scripts/site-builder/check_hosted_startup.py`. Modified: shared scanner deadline in `web/server.py`, CI container checks, `.env.example`, README, site manifest, architecture, deployment and validation documentation.

Validation: 13 mocked backend tests PASS; five-route static build/link/asset checks PASS; Python syntax and diff whitespace PASS. Docker is unavailable in the editing environment; container build/startup is delegated to the repository CI gate. No live email lookup, production token, paid service, or hosted-backend deployment was performed. Blocker: Railway dashboard requires sign-in; the owner must choose the permitted address and supply/authorize deployment access. Next executable action: publish the branch, verify CI including container startup, merge when checks pass, then complete Railway account connection and private Sites runtime settings.

CI continuation: The image built successfully and all thirteen tests passed. The first readiness probe hit a connection reset before Uvicorn was ready; updated the bounded startup retry to include connection-reset/HTTP startup failures and retained container logs for diagnosis. Rerun required before merge.

## 2026-09-28 15:51 UTC — Railway validation and authorization boundary

PR #3 merged as `e246095c17fb0c1a8e195321f95164a6c614da18`. Final implementation head `30468c4cfcede12de15869f166ece5a6bdd8e550` passed GitHub Site check run `36446258329` (dependency install, thirteen tests, static build, Docker build and startup/authentication smoke checks) and CodeQL run `36446258449`. No unresolved review threads were returned. The startup retry repair passed.

Railway sign-in succeeded; its dashboard shows a trial workspace. Prepared GitHub app authorization with only `advantageosmain-sudo/holehe` selected, but did not click Install & Authorize. Browser confirmation is required to grant new repository access. No backend service, production credential, paid subscription or live lookup was created. Updated deployment documentation and the manifest with the exact remaining blocker. Next action: obtain the scoped GitHub app authorization, choose the owner-permitted address, configure the Railway service and matching private Sites runtime values, then verify live health and an intentional lookup.

## 2026-09-28 16:27 UTC — Railway project setup and config correction

Owner approved the Railway GitHub app for only `advantageosmain-sudo/holehe`. Clicking Install & Authorize led to GitHub sudo confirmation. The owner selected GitHub Mobile, but the verification request timed out; repository authorization did not complete. Do not treat the app as installed.

Created private Railway project `Holehe` (ID `79d59f56-a9fc-412b-b23f-d1628e6d330d`) and offline service `holehe-api` (ID `977bc658-8985-459a-9491-6413be3534f8`). Staged Dockerfile builder, `/Dockerfile.railway` path, and `/healthz` check; the service has no source, runtime variables or live deployment. One replica is shown. No paid upgrade, live lookup or production secret was used.

Railway now deprecates legacy Config as Code for new services. Removed the unused `railway.json` and corrected the README, deployment docs, architecture and manifest to reflect the actual dashboard configuration. Next action: choose another GitHub sudo method or retry GitHub Mobile when the owner is available; then connect this fork, configure the permitted address and matching secure token in Railway and Sites, deploy, verify health and perform an intentional lookup.

## 2026-09-28 16:37 UTC — GitHub Mobile retry and scoped Railway source

Task: Retried GitHub Mobile sudo verification at the owner's request. The new challenge succeeded. GitHub reset repository access to all repositories after the expired request; reselected only `advantageosmain-sudo/holehe` and completed the previously approved Railway App installation. Railway returned to the authenticated dashboard. No other repository was selected.

Railway: Selected the existing fork and `master` branch for the existing offline `holehe-api` service. The dashboard shows six staged settings: repo, branch, Dockerfile builder, `/Dockerfile.railway`, `/healthz`, and Wait for CI false. One replica remains selected. The Wait for CI feature reported automatic deployment unavailable and requested updated GitHub permissions when enabled, so it was returned to off. These changes have not been applied; the service has no runtime variables, public domain or live deployment. No token, email address, lookup, paid upgrade or public exposure was added.

Validation: GitHub installation redirected to Railway dashboard PASS; Railway source selector listed the single authorized fork PASS; staged changes review showed expected repository, branch, builder, path and health check PASS. Deployment and end-to-end health BLOCKED pending owner-selected permitted address and secure production token entry. Next executable action: set `HOLEHE_ALLOWED_EMAIL` and `LOOKUP_API_TOKEN` in Railway, apply staged changes, review the build and health result, configure a protected HTTPS domain and matching private Sites worker variables, then verify authenticated health and an intentional owner-authorized lookup.
