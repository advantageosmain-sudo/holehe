# Deployment

## Current deployment model

The fork keeps its static guide and optional loopback server. The private ChatGPT Sites interface runs separately as `holehe-project-guide`; it proxies requests from its server to this repository's authenticated Railway API. The browser never receives the API token. Railway is the selected backend host. Railway sign-in is complete. GitHub app authorization, project connection, runtime values and a verified HTTPS domain are still required; no hosted backend URL is assumed.

## Railway backend

Connect this GitHub repository's `master` branch in Railway, using the repository root. `railway.json` selects `Dockerfile.railway`, one US East replica, and the `/healthz` readiness path. The image installs `requirements-hosted.lock`, runs as a non-root user, and starts one Uvicorn worker on Railway's `PORT`. Keep one replica and one worker: the concurrency lock and five-minute cooldown are in process memory and reset at restart. There is no database or lookup history.

Set these Railway runtime variables outside Git:

- `LOOKUP_API_TOKEN`: a randomly generated secret with at least 32 ASCII characters. Use a password manager or secure secret generator; never use the synthetic CI test token.
- `HOLEHE_ALLOWED_EMAIL`: the single address the owner has chosen and is authorized to check.

The process fails closed when either setting is absent or invalid. `.env.example` lists variable names only and is not loaded automatically. Do not add real values to source, build arguments, screenshots or logs. Select only this repository if Railway requests GitHub app access. Any paid plan or account terms require the owner's action.

After deployment, generate Railway's HTTPS domain and verify `/healthz` returns `{"status":"ok"}`. Verify `/health` returns HTTP 401 without a bearer token and HTTP 200 with the configured token. These checks do not contact lookup providers. The lookup endpoint is `POST /api/lookup` with JSON `{"email":"the permitted address"}` and an `Authorization: Bearer ...` header. Provider results are limited to GitHub, Gravatar and WordPress status fields. Requests have a 1 KiB limit, concurrent checks are rejected, and each provider has a 20-second deadline. No recovery details are returned. The application disables access logs; Railway's own telemetry is controlled by Railway.

## Connect the existing Sites interface

Keep the Site private. Set its server runtime values:

- `LOOKUP_API_URL`: the verified Railway HTTPS base URL, without a trailing slash.
- `LOOKUP_API_TOKEN`: the same secret as Railway.
- `HOLEHE_ALLOWED_EMAIL`: the same permitted address as Railway.

Redeploy the Site after updating runtime values. Its connection indicator checks the authenticated `/health` endpoint. The Sites worker checks same-origin requests, consent and the permitted address before forwarding to Railway. Do not place the token in browser JavaScript. End-to-end lookup validation needs the owner's selected address and an intentional submission; mocked tests do not prove that third-party services currently return accurate results.

## Development and validation

Use Python 3.12 and `python3 -m pip install -r requirements-hosted.lock`, then run `python3 -m unittest discover -s tests`. With variables supplied in the process environment, start the hosted adapter locally using `python3 -m uvicorn web.hosted:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log`.

CI builds the Railway image and smoke-tests startup and token authentication with synthetic settings. It never runs live provider lookups. Rebuild the image when updating dependency pins. Review changes with the test suite before deployment. Roll back by redeploying a known-good GitHub commit in Railway; rotate both services' token together if it is exposed.

## Static guide and loopback alternative

Run `python3 scripts/site-builder/build.py` to build the five-page guide into `dist/`. Preview with `python3 -m http.server 8000 --directory dist`. Static hosting cannot run `/api/lookup`. Canonical metadata and a sitemap require a confirmed public guide URL; the private Sites interface is not a public SEO destination.

For the original local form, set `HOLEHE_ALLOWED_EMAIL` and run `python3 web/server.py`, then visit `http://127.0.0.1:8765/lookup/`. This loopback server is separate from the Railway adapter and must remain loopback-only.
