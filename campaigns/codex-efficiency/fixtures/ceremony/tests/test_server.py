"""Tests for the notes service (server.py)."""
import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server


class NotesStoreTests(unittest.TestCase):
    def test_create_assigns_increasing_ids(self):
        store = server.NotesStore()
        a = store.create("first")
        b = store.create("second")
        self.assertEqual(a["id"], 1)
        self.assertEqual(b["id"], 2)

    def test_get_missing_returns_none(self):
        store = server.NotesStore()
        self.assertIsNone(store.get(999))

    def test_delete_returns_false_for_missing(self):
        store = server.NotesStore()
        self.assertFalse(store.delete(999))

    def test_delete_returns_true_and_removes(self):
        store = server.NotesStore()
        note = store.create("temp")
        self.assertTrue(store.delete(note["id"]))
        self.assertIsNone(store.get(note["id"]))

    def test_list_all_newest_first(self):
        store = server.NotesStore()
        store.create("first")
        store.create("second")
        ids = [n["id"] for n in store.list_all()]
        self.assertEqual(ids, sorted(ids, reverse=True))


class NotesHTTPTests(unittest.TestCase):
    """Integration tests against a real running server on a free port."""

    @classmethod
    def setUpClass(cls):
        cls.store = server.NotesStore()
        handler = server.make_handler(cls.store)
        cls.httpd = server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=5)

    def _url(self, path):
        return f"http://127.0.0.1:{self.port}{path}"

    def _request(self, method, path, body=None):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(self._url(path), data=data, method=method)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                parsed = json.loads(raw) if raw else None
                return resp.status, parsed
        except urllib.error.HTTPError as e:
            raw = e.read()
            e.close()
            parsed = json.loads(raw) if raw else None
            return e.code, parsed

    def test_create_then_list(self):
        status, note = self._request("POST", "/notes", {"text": "buy milk"})
        self.assertEqual(status, 201)
        self.assertEqual(note["text"], "buy milk")
        status, body = self._request("GET", "/notes")
        self.assertEqual(status, 200)
        self.assertIn(note["id"], [n["id"] for n in body["notes"]])

    def test_get_single_note(self):
        _, note = self._request("POST", "/notes", {"text": "single"})
        status, body = self._request("GET", f"/notes/{note['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(body["text"], "single")

    def test_get_missing_note_is_404(self):
        status, _ = self._request("GET", "/notes/999999")
        self.assertEqual(status, 404)

    def test_post_without_text_is_400(self):
        status, _ = self._request("POST", "/notes", {})
        self.assertEqual(status, 400)

    def test_delete_note(self):
        _, note = self._request("POST", "/notes", {"text": "temp"})
        status, _ = self._request("DELETE", f"/notes/{note['id']}")
        self.assertEqual(status, 204)
        status, _ = self._request("GET", f"/notes/{note['id']}")
        self.assertEqual(status, 404)

    def test_unknown_route_is_404(self):
        status, _ = self._request("GET", "/unknown")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
