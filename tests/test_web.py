import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from web.server import LookupServer


class WebTests(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.server = LookupServer(('127.0.0.1', 0), 'owner@example.com', scanner=self.fake_scan)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def fake_scan(self, email):
        self.calls.append(email)
        return [{'service': 'github', 'status': 'unknown'}]

    def request(self, email, origin=None):
        body = json.dumps({'email': email}).encode()
        headers = {'Content-Type': 'application/json'}
        if origin: headers['Origin'] = origin
        req = Request(self.base + '/api/lookup', body, headers, method='POST')
        try:
            with urlopen(req) as response:
                return response.status, json.load(response)
        except HTTPError as error:
            return error.code, json.load(error)

    def test_allowed_address_then_cooldown(self):
        code, body = self.request('owner@example.com', self.base)
        self.assertEqual((code, body['results'][0]['status']), (200, 'unknown'))
        self.assertEqual(self.request('owner@example.com')[0], 429)
        self.assertEqual(self.calls, ['owner@example.com'])

    def test_other_email_rejected_without_scan(self):
        self.assertEqual(self.request('other@example.com')[0], 403)
        self.assertEqual(self.calls, [])

    def test_cross_origin_rejected(self):
        self.assertEqual(self.request('owner@example.com', 'https://untrusted.example')[0], 403)
        self.assertEqual(self.calls, [])

    def test_form_served_and_no_traversal(self):
        with urlopen(self.base + '/lookup/') as response:
            self.assertIn(b'lookup-form', response.read())
        with self.assertRaises(HTTPError):
            urlopen(self.base + '/lookup/../../README.md')

    def test_server_requires_allowlist(self):
        with self.assertRaises(ValueError):
            LookupServer(('127.0.0.1', 0), '')


if __name__ == '__main__':
    unittest.main()
