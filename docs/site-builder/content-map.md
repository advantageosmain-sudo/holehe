# Content map

| Route | Public content source | Purpose |
| --- | --- | --- |
| `/` | README, setup.py | Describe the CLI and direct readers to install and upstream source |
| `/install/` | README, setup.py | Python/pip, PyPI, source, Docker reference |
| `/usage/` | README | Example command, module fields, limitations |
| `/privacy/` | Repository architecture | State that this static site does not collect emails; explain limits |

Keep secrets, service-response data, private email addresses, logs, and internal operational records out of the static site. Do not assert a currently working service integration from old module code. Review upstream instructions before major version changes.
