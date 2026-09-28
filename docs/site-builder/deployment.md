# Deployment

Run `python3 scripts/site-builder/build.py`; deploy the generated `dist/` directory to a static host. There are no environment variables, server process, database, API, or DNS assumptions. For local preview, run `python3 -m http.server 8000 --directory dist` and open `http://localhost:8000/`.

GitHub Pages deployment is deliberately not enabled by this PR. To publish through GitHub Pages, first approve public hosting, choose Pages as the deployment target in repository settings, and configure a workflow or host that uploads `dist/`. Use the resulting canonical URL for canonical tags and sitemap. Do not point the site at an unverified URL. Existing CodeQL workflow is untouched.

The local lookup requires Python and the package dependencies. `python3 web/server.py` serves it at `127.0.0.1:8765`; set `HOLEHE_ALLOWED_EMAIL` in the process environment first. Do not deploy this loopback server as a public service. Public lookup hosting would require a separate authentication, abuse-control, privacy, and deployment design and is not configured here. GitHub Pages serves only static files and cannot execute the lookup backend.
