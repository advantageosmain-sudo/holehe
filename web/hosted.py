"""Authenticated Railway API for the existing allowlisted Holehe scanner."""
import hmac
import json
import os
import threading
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from web.server import COOLDOWN_SECONDS, DEFAULT_MODULES, scan, valid_email

STATES = frozenset({"registered", "not_registered", "unknown", "error", "rate_limited"})


def create_app(*, token=None, allowed_email=None, scanner=scan, clock=time.monotonic):
    token = token if token is not None else os.environ.get("LOOKUP_API_TOKEN", "")
    allowed_email = allowed_email if allowed_email is not None else os.environ.get("HOLEHE_ALLOWED_EMAIL", "")
    if not isinstance(token, str) or len(token) < 32 or not token.isascii():
        raise ValueError("LOOKUP_API_TOKEN must contain at least 32 ASCII characters")
    if not valid_email(allowed_email):
        raise ValueError("HOLEHE_ALLOWED_EMAIL must contain one valid address")

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    lookup_lock = threading.Lock()
    last_lookup = float("-inf")

    def response(data, status=200, headers=None):
        return JSONResponse(data, status_code=status, headers={
            "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff", **(headers or {})
        })

    def authorized(request):
        provided = request.headers.get("authorization", "").encode("utf-8")
        expected = ("Bearer " + token).encode("ascii")
        return hmac.compare_digest(provided, expected)

    @app.get("/healthz")
    async def healthz():
        # Railway readiness check: no configuration or account information.
        return response({"status": "ok"})

    @app.get("/health")
    async def health(request: Request):
        if not authorized(request):
            return response({"error": "Unauthorized"}, 401, {"WWW-Authenticate": "Bearer"})
        return response({"status": "ok"})

    def run_lookup(email):
        nonlocal last_lookup
        if not lookup_lock.acquire(blocking=False):
            return response({"error": "A lookup is already running"}, 429, {"Retry-After": "30"})
        try:
            remaining = COOLDOWN_SECONDS - (clock() - last_lookup)
            if remaining > 0:
                return response({"error": "Wait between lookups"}, 429,
                                {"Retry-After": str(max(1, int(remaining + 1)))})
            last_lookup = clock()
            try:
                raw = scanner(email)
                if not isinstance(raw, list):
                    raise ValueError("Invalid scanner response")
                results = []
                for name in DEFAULT_MODULES:
                    item = next((x for x in raw if isinstance(x, dict) and x.get("service") == name), {})
                    state = item.get("status")
                    results.append({"service": name, "status": state if isinstance(state, str) and state in STATES else "unknown"})
            except Exception:
                # Provider errors must not expose addresses, credentials or provider bodies.
                return response({"error": "Lookup could not be completed"}, 502)
            return response({"results": results})
        finally:
            lookup_lock.release()

    @app.post("/api/lookup")
    async def lookup(request: Request):
        if not authorized(request):
            return response({"error": "Unauthorized"}, 401, {"WWW-Authenticate": "Bearer"})
        if request.headers.get("content-type", "").split(";")[0].strip() != "application/json":
            return response({"error": "Send JSON"}, 415)
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 1024:
                return response({"error": "Request too large"}, 413)
        try:
            data = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            return response({"error": "Invalid request"}, 400)
        email = data.get("email") if isinstance(data, dict) else None
        if not valid_email(email):
            return response({"error": "Enter a valid email address"}, 400)
        if not hmac.compare_digest(email.casefold(), allowed_email.casefold()):
            return response({"error": "This address is not enabled"}, 403)
        return await run_in_threadpool(run_lookup, email)

    return app
