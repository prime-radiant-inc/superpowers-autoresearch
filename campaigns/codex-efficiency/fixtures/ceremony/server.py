#!/usr/bin/env python3
"""notes: a tiny stdlib-only HTTP JSON service for storing short text notes.

Endpoints:
  GET    /notes        -> list all notes, newest first
  POST   /notes         -> create a note; body {"text": "..."}
  GET    /notes/<id>    -> fetch one note
  DELETE /notes/<id>    -> delete one note

Storage is an in-memory dict, held for the life of the process -- there is
no persistence. Run directly (python3 server.py [--port N]) or import
NotesStore / make_handler to embed the service elsewhere.
"""
import argparse
import itertools
import json
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

NOTE_ID_RE = re.compile(r"^/notes/(\d+)$")


class NotesStore:
    """Thread-safe in-memory note storage."""

    def __init__(self):
        self._lock = threading.Lock()
        self._notes = {}
        self._ids = itertools.count(1)

    def create(self, text):
        with self._lock:
            note_id = next(self._ids)
            note = {"id": note_id, "text": text}
            self._notes[note_id] = note
            return note

    def get(self, note_id):
        with self._lock:
            return self._notes.get(note_id)

    def delete(self, note_id):
        with self._lock:
            return self._notes.pop(note_id, None) is not None

    def list_all(self):
        with self._lock:
            return sorted(self._notes.values(), key=lambda n: n["id"], reverse=True)


class NotesHandler(BaseHTTPRequestHandler):
    """Routes requests to a NotesStore bound as the class attribute `store`
    (see make_handler -- a handler class is bound to one store per server,
    matching BaseHTTPRequestHandler's own class-based construction)."""

    store = None  # set by make_handler before the server is constructed

    def _write_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/notes":
            notes = self.store.list_all()
            sys.stderr.write(f"GET {self.path} -> 200\n")
            self._write_json(200, {"notes": notes})
            return
        m = NOTE_ID_RE.match(self.path)
        if m:
            note = self.store.get(int(m.group(1)))
            if note is None:
                sys.stderr.write(f"GET {self.path} -> 404\n")
                self._write_json(404, {"error": "not found"})
                return
            sys.stderr.write(f"GET {self.path} -> 200\n")
            self._write_json(200, note)
            return
        sys.stderr.write(f"GET {self.path} -> 404\n")
        self._write_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/notes":
            sys.stderr.write(f"POST {self.path} -> 404\n")
            self._write_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            data = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            sys.stderr.write(f"POST {self.path} -> 400\n")
            self._write_json(400, {"error": "invalid JSON"})
            return
        text = data.get("text")
        if not isinstance(text, str) or not text.strip():
            sys.stderr.write(f"POST {self.path} -> 400\n")
            self._write_json(400, {"error": "text is required"})
            return
        note = self.store.create(text)
        sys.stderr.write(f"POST {self.path} -> 201\n")
        self._write_json(201, note)

    def do_DELETE(self):
        m = NOTE_ID_RE.match(self.path)
        if not m:
            sys.stderr.write(f"DELETE {self.path} -> 404\n")
            self._write_json(404, {"error": "not found"})
            return
        deleted = self.store.delete(int(m.group(1)))
        if deleted:
            sys.stderr.write(f"DELETE {self.path} -> 204\n")
            self.send_response(204)
            self.end_headers()
        else:
            sys.stderr.write(f"DELETE {self.path} -> 404\n")
            self._write_json(404, {"error": "not found"})

    def log_message(self, format, *args):
        # Silence BaseHTTPRequestHandler's own default per-request stderr
        # logging; the explicit sys.stderr.write calls above are this
        # service's actual request-log lines.
        pass


def make_handler(store):
    """Bind a NotesHandler subclass to `store`, suitable for passing to
    ThreadingHTTPServer (which instantiates the handler class itself, so
    binding via a class attribute is how per-server state gets in)."""
    return type("BoundNotesHandler", (NotesHandler,), {"store": store})


def serve(port):
    store = NotesStore()
    handler = make_handler(store)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    sys.stderr.write(f"notes service listening on 127.0.0.1:{port}\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="server.py", description="notes: a tiny JSON notes service")
    parser.add_argument("--port", type=int, default=8080, help="TCP port to listen on (default: 8080)")
    args = parser.parse_args(argv)
    serve(args.port)


if __name__ == "__main__":
    main()
