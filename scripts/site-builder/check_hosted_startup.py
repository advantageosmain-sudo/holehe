"""Check an ephemeral CI container without triggering any provider lookup."""
import json
import os
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:18765"
for attempt in range(30):
    try:
        with urlopen(BASE + "/healthz", timeout=2) as response:
            assert json.load(response) == {"status": "ok"}
        break
    except (URLError, TimeoutError):
        if attempt == 29:
            raise
        time.sleep(1)
try:
    urlopen(BASE + "/health", timeout=2)
    raise AssertionError("Authenticated health endpoint accepted a missing token")
except HTTPError as error:
    assert error.code == 401
request = Request(BASE + "/health", headers={"Authorization": "Bearer " + os.environ["LOOKUP_API_TOKEN"]})
with urlopen(request, timeout=2) as response:
    assert json.load(response) == {"status": "ok"}
print("PASS: container startup, readiness, and token authentication")
