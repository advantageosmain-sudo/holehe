# Validation

Run `python3 scripts/site-builder/build.py` for static route, metadata, local-link, fragment and asset checks. It copies the five pages to `dist/` only when these checks pass. Source review covers semantic headings, form labels, focus states and responsive CSS; it is not a browser-based WCAG audit. Full keyboard, screen-reader and device testing remains a manual release check.

Install `requirements-hosted.lock` with Python 3.12 and run `python3 -m unittest discover -s tests`. The thirteen local/hosted backend tests use fake scanners, including authentication, allowlisting, size limits, concurrent requests, cooldowns, result filtering and failures. They do not send emails to third-party providers. Run `python3 -m compileall -q web tests scripts/site-builder` and `git diff --check` for syntax and whitespace checks. No separate typecheck or lint tool is configured.

GitHub Actions builds `Dockerfile.railway` and runs `scripts/site-builder/check_hosted_startup.py` against an ephemeral container, verifying readiness and authenticated health. Synthetic test configuration is disposable and never used in production. The image has no real secrets. The dependency lock is checked with `python3 -m pip check`.

The separate Sites interface has its own build and worker tests for unconfigured state, origin/address restrictions, sanitized results and health checks. A successful Site build does not prove Railway connectivity. Deployment validation requires a live Railway URL and runtime settings, authenticated health, then an intentional owner-approved lookup. Third-party provider behavior can change; `unknown`, `rate_limited` and `error` are valid outcomes, not proof of absence.
