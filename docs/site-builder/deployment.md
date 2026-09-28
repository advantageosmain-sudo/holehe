# Deployment

Run `python3 scripts/site-builder/build.py`; deploy the generated `dist/` directory to a static host. There are no environment variables, server process, database, API, or DNS assumptions. For local preview, run `python3 -m http.server 8000 --directory dist` and open `http://localhost:8000/`.

GitHub Pages deployment is deliberately not enabled by this PR. To publish through GitHub Pages, first approve public hosting, choose Pages as the deployment target in repository settings, and configure a workflow or host that uploads `dist/`. Use the resulting canonical URL for canonical tags and sitemap. Do not point the site at an unverified URL. Existing CodeQL workflow is untouched.
