"""Loopback-only, allowlisted web interface for the existing Holehe modules."""
import hmac
import importlib
import json
import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\Z")
DEFAULT_MODULES = ("github", "gravatar", "wordpress")
MODULE_PATHS = {
    "github": "programing.github",
    "gravatar": "cms.gravatar",
    "wordpress": "cms.wordpress",
}
COOLDOWN_SECONDS = 300


def scan(email, modules=DEFAULT_MODULES):
    """Run selected existing modules without invoking the CLI auto-updater."""
    import httpx
    import trio

    async def run():
        output = []
        async with httpx.AsyncClient(timeout=10) as client:
            async def one(name):
                module = importlib.import_module("holehe.modules." + MODULE_PATHS[name])
                try:
                    await getattr(module, name)(email, client, output)
                except Exception:
                    output.append({"name": name, "error": True})
            async with trio.open_nursery() as nursery:
                for name in modules:
                    nursery.start_soon(one, name)
        by_name = {item.get("name"): item for item in output if isinstance(item, dict)}
        return [{
            "service": name,
            "status": ("rate_limited" if item.get("rateLimit") else
                       "error" if item.get("error") else
                       "registered" if item.get("exists") is True else
                       "not_registered" if item.get("exists") is False else "unknown")
        } for name in modules for item in [by_name.get(name, {})]]

    return trio.run(run)


class LookupServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, allowed_email, scanner=scan, clock=time.monotonic):
        if not EMAIL.fullmatch(allowed_email):
            raise ValueError("Set HOLEHE_ALLOWED_EMAIL to one valid email address")
        super().__init__(address, Handler)
        self.allowed_email = allowed_email
        self.scanner = scanner
        self.clock = clock
        self.lock = threading.Lock()
        self.last_lookup = float("-inf")


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, format, *args):
        pass  # Never write submitted addresses to access logs.

    def send_json(self, status, data):
        payload = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def headers_valid(self):
        host = self.headers.get("Host", "")
        allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        origin = self.headers.get("Origin")
        return host in allowed and (not origin or origin in {"http://" + h for h in allowed})

    def do_POST(self):
        if self.path != "/api/lookup":
            return self.send_json(404, {"error": "Not found"})
        if not self.headers_valid():
            return self.send_json(403, {"error": "Request origin rejected"})
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            return self.send_json(415, {"error": "Send JSON"})
        try:
            length = int(self.headers.get("Content-Length", ""))
            if not 0 < length <= 1024:
                raise ValueError
            data = json.loads(self.rfile.read(length))
            email = data.get("email") if isinstance(data, dict) else None
        except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
            return self.send_json(400, {"error": "Invalid request"})
        if not isinstance(email, str) or not EMAIL.fullmatch(email):
            return self.send_json(400, {"error": "Enter a valid email address"})
        if not hmac.compare_digest(email.casefold(), self.server.allowed_email.casefold()):
            return self.send_json(403, {"error": "This address is not enabled for this local server"})
        if not self.server.lock.acquire(blocking=False):
            return self.send_json(429, {"error": "A lookup is already running"})
        try:
            now = self.server.clock()
            if now - self.server.last_lookup < COOLDOWN_SECONDS:
                return self.send_json(429, {"error": "Wait five minutes between lookups"})
            self.server.last_lookup = now
            try:
                results = self.server.scanner(email)
            except Exception:
                return self.send_json(502, {"error": "Lookup failed; check local dependencies and service availability"})
            return self.send_json(200, {"results": results})
        finally:
            self.server.lock.release()

    def do_GET(self):
        if not self.headers_valid():
            return self.send_json(403, {"error": "Request host rejected"})
        route = self.path.split("?", 1)[0]
        files = {"/": "index.html", "/style.css": "style.css", "/lookup/app.js": "lookup/app.js"}
        for name in ("install", "usage", "privacy", "lookup"):
            files[f"/{name}/"] = f"{name}/index.html"
        relative = files.get(route)
        if relative is None:
            return self.send_json(404, {"error": "Not found"})
        content = (SITE / relative).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/javascript; charset=utf-8" if relative.endswith(".js") else "text/css; charset=utf-8" if relative.endswith(".css") else "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; form-action 'self'; base-uri 'none'")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main():
    allowed = os.environ.get("HOLEHE_ALLOWED_EMAIL", "")
    server = LookupServer(("127.0.0.1", 8765), allowed)
    print("Local lookup ready at http://127.0.0.1:8765/lookup/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
