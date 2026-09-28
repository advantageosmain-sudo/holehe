# Validation

`python3 scripts/site-builder/build.py` checks that configured routes exist, each has a title, description, and H1, images have alt text, and local href/src and fragment targets exist. It copies site files to `dist/` only after these checks pass. It does not emulate a browser or perform a full WCAG audit. Review mobile at 375px and desktop at 1280px before public release. No JavaScript or third-party frontend dependencies exist; lint and typecheck are N/A. Python package runtime behavior is outside this documentation-site build.
