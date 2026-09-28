# Architecture

Repository assessment: `megadose/holehe` fork, default branch `master`, base commit `14da70f588538936b20d238783c5e28a0772a2b3`. The project is a Python 3 command-line package (setup.py, holehe/core.py and service modules), not a web app. No existing site or frontend dependencies were found. Existing CodeQL workflow and package remain intact.

The new site is a static four-route project guide in `site/`; `scripts/site-builder/build.py` checks pages and local links then copies to ignored `dist/`. No framework, runtime API, form, cookie, analytics, or new dependency. Python CLI remains separate. Pages: overview `/`, installation `/install/`, usage `/usage/`, privacy `/privacy/`. GitHub Pages can publish `dist/` after explicit deployment setup, but no public URL is assumed.

Public sources: README, setup.py, LICENSE. CLI modules and operational implementation are not copied into the site. This is a documentation interface, not an email lookup service.
