import threading
import unittest
from fastapi.testclient import TestClient
from web.hosted import create_app

TOKEN = "test-token-for-unit-tests-only-00000000"
AUTH = {"Authorization": "Bearer " + TOKEN}


class HostedTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.now = 1000
        def scanner(email):
            self.calls.append(email)
            return [{"service": "github", "status": "registered", "recovery": "private"}]
        self.app = create_app(token=TOKEN, allowed_email="owner@example.com", scanner=scanner, clock=lambda: self.now)
        self.client = TestClient(self.app)

    def test_health_auth_and_no_secret_exposure(self):
        self.assertEqual(self.client.get("/healthz").json(), {"status": "ok"})
        self.assertEqual(self.client.get("/health").status_code, 401)
        self.assertEqual(self.client.get("/health", headers=AUTH).json(), {"status": "ok"})
        self.assertEqual(self.client.post("/api/lookup", json={"email": "owner@example.com"}).status_code, 401)
        self.assertEqual(self.calls, [])

    def test_allowlist_and_size_limit(self):
        self.assertEqual(self.client.post("/api/lookup", headers=AUTH, json={"email": "other@example.com"}).status_code, 403)
        self.assertEqual(self.client.post("/api/lookup", headers={**AUTH, "Content-Type": "application/json"}, content=" " * 1100).status_code, 413)
        self.assertEqual(self.calls, [])

    def test_sanitizes_results_and_enforces_cooldown(self):
        r = self.client.post("/api/lookup", headers=AUTH, json={"email": "owner@example.com"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"results": [
            {"service": "github", "status": "registered"},
            {"service": "gravatar", "status": "unknown"},
            {"service": "wordpress", "status": "unknown"}]})
        self.assertNotIn("private", r.text)
        self.assertEqual(r.headers["cache-control"], "no-store")
        self.assertEqual(self.client.post("/api/lookup", headers=AUTH, json={"email": "owner@example.com"}).status_code, 429)
        self.now += 301
        self.assertEqual(self.client.post("/api/lookup", headers=AUTH, json={"email": "owner@example.com"}).status_code, 200)

    def test_concurrent_lookup_rejected(self):
        entered, release = threading.Event(), threading.Event()
        def scanner(email):
            entered.set()
            release.wait(5)
            return []
        client = TestClient(create_app(token=TOKEN, allowed_email="owner@example.com", scanner=scanner))
        thread = threading.Thread(target=lambda: client.post("/api/lookup", headers=AUTH, json={"email": "owner@example.com"}))
        thread.start()
        self.assertTrue(entered.wait(2))
        try:
            self.assertEqual(client.post("/api/lookup", headers=AUTH, json={"email": "owner@example.com"}).status_code, 429)
        finally:
            release.set(); thread.join(5)

    def test_fails_closed_with_missing_settings(self):
        for kwargs in ({"token": "", "allowed_email": "owner@example.com"}, {"token": TOKEN, "allowed_email": ""}):
            with self.assertRaises(ValueError): create_app(**kwargs)

    def test_provider_exception_does_not_leak_data(self):
        def fail(email): raise RuntimeError("sensitive provider details")
        client = TestClient(create_app(token=TOKEN, allowed_email="owner@example.com", scanner=fail))
        r = client.post("/api/lookup", headers=AUTH, json={"email": "owner@example.com"})
        self.assertEqual(r.status_code, 502)
        self.assertNotIn("sensitive", r.text)


if __name__ == "__main__": unittest.main()
