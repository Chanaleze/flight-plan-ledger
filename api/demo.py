"""Vercel serverless adapter for the public demo API (POST /api/demo).

Thin HTTP glue only: every decision lives in
``flight_plan_ledger.demo_service`` (fully unit-tested). Stateless —
chain state stays in the visitor's browser.

Security notes:
- Request bodies are never logged.
- Error responses are generic; internal details never leak to the client.
- Responses carry ``no-store``; the demo holds no cookies and no sessions.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from http.server import BaseHTTPRequestHandler  # noqa: E402

from flight_plan_ledger.demo_service import (  # noqa: E402
    INFO,
    MAX_BODY_BYTES,
    DemoError,
    handle_action,
)


class handler(BaseHTTPRequestHandler):
    server_version = "FplDemo/0.1"

    # -- helpers ---------------------------------------------------------
    def _send_json(self, status: int, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # never log request bodies
        pass

    # -- routes ----------------------------------------------------------
    def do_OPTIONS(self):
        self._send_json(204, {})

    def do_GET(self):
        self._send_json(200, dict(INFO))

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except (TypeError, ValueError):
            self._send_json(400, {"error": "invalid Content-Length"})
            return
        if length <= 0:
            self._send_json(400, {"error": "empty request body"})
            return
        if length > MAX_BODY_BYTES:
            self._send_json(413, {"error": "request body too large"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            self._send_json(400, {"error": "request body must be valid JSON"})
            return
        try:
            status, body = handle_action(
                payload.get("action") if isinstance(payload, dict) else None,
                payload,
            )
        except DemoError as e:
            self._send_json(e.status, {"error": e.message})
            return
        except Exception:
            self._send_json(500, {"error": "internal error"})
            return
        self._send_json(status, body)
