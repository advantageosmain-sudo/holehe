# Architecture

Repository assessment: `megadose/holehe` fork, default branch `master`, base commit `14da70f588538936b20d238783c5e28a0772a2b3`. The project is a Python 3 command-line package (setup.py, holehe/core.py and service modules), not a web app. No existing site or frontend dependencies were found. Existing CodeQL workflow and package remain intact.

The new site is a static four-route project guide in `site/`; `scripts/site-builder/build.py` checks pages and local links then copies to ignored `dist/`. The static build itself has no runtime API, cookie, analytics, or frontend dependency. An optional local backend is described below. Python CLI remains separate. Pages: overview `/`, installation `/install/`, usage `/usage/`, privacy `/privacy/`. GitHub Pages can publish `dist/` after explicit deployment setup, but no public URL is assumed.

Public sources: README, setup.py, LICENSE. CLI modules and operational implementation are not copied into the site. This is a documentation interface, not an email lookup service.

## Local lookup extension

`web/server.py` serves the static pages and a same-origin JSON POST endpoint on loopback only. An exact address from `HOLEHE_ALLOWED_EMAIL` is required; a process lock and five-minute cooldown bound use. The scanner imports three existing service modules directly and omits the CLI's update/install behavior. It returns only service and status, not masked recovery details or raw provider responses. No lookup history is stored. The static output `dist/` alone cannot run the endpoint.
