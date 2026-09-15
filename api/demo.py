"""Vercel adapter: demo API + static file serving (GET /, /demo/*, /examples/*).

Thin HTTP glue only: every API decision lives in
``flight_plan_ledger.demo_service`` (fully unit-tested). Stateless —
chain state stays in the visitor's browser.

Why this file also serves static assets: with ``[tool.vercel] entrypoint``
declared (required for ``vercel build`` to find the function), Vercel routes
*every* path to this handler, so ``/demo/index.html`` would otherwise return
API JSON. The static map below restores the intended layout: ``/demo/*`` and
``/examples/*`` are served as files (whitelist only — nothing else on disk is
reachable), ``/`` redirects to ``/demo/``, and only ``/api/demo`` speaks JSON.

Security notes:
- Request bodies are never logged.
- Error responses are generic; internal details never leak to the client.
- API responses carry ``no-store``; the demo holds no cookies and no sessions.
"""

import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from http.server import BaseHTTPRequestHandler  # noqa: E402

from flight_plan_ledger.demo_service import (  # noqa: E402
    INFO,
    MAX_BODY_BYTES,
    DemoError,
    handle_action,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

API_PATH = "/api/demo"

# URL prefix -> directory under the project root. Nothing else is servable.
STATIC_ROUTES = {
    "/demo/": "demo",
    "/examples/": "examples",
}
STATIC_INDEX = "index.html"
STATIC_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json",
}


def _request_path(raw: str) -> str:
    """Path portion of the request target, percent-decoded (query stripped)."""
    return urllib.parse.unquote(urllib.parse.urlsplit(raw).path)


def _find_static(path: str):
    """Return (status, content_type, body) for static paths, else None."""
    for prefix, folder in STATIC_ROUTES.items():
        exact = prefix.rstrip("/")
        if path != exact and not path.startswith(prefix):
            continue
        rel = path[len(prefix):] if path.startswith(prefix) else ""
        if not rel:
            rel = STATIC_INDEX
        safe = os.path.normpath(rel)
        if safe.startswith("..") or os.path.isabs(safe):
            return 403, "application/json", b'{"error": "forbidden"}'
        full = os.path.join(PROJECT_ROOT, folder, safe)
        if os.path.isdir(full):
            full = os.path.join(full, STATIC_INDEX)
        if not os.path.isfile(full):
            return 404, "application/json", b'{"error": "not found"}'
        ext = os.path.splitext(full)[1].lower()
        with open(full, "rb") as f:
            return 200, STATIC_TYPES.get(ext, "application/octet-stream"), f.read()
    return None


class handler(BaseHTTPRequestHandler):
    server_version = "FplDemo/0.1"

    # -- helpers ---------------------------------------------------------
    def _send(self, status: int, content_type: str, body: bytes,
              cacheable: bool = False, extra: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header(
            "Cache-Control", "public, max-age=3600" if cacheable else "no-store"
        )
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status: int, obj: dict) -> None:
        self._send(status, "application/json", json.dumps(obj).encode("utf-8"))

    def log_message(self, *args):  # never log request bodies
        pass

    # -- routes ----------------------------------------------------------
    def do_OPTIONS(self):
        self._send_json(204, {})

    def do_GET(self):
        path = _request_path(self.path)
        if path == "/" or path == "":
            self._send(302, "text/plain", b"Redirecting to /demo/",
                       extra={"Location": "/demo/"})
            return
        if path == API_PATH or path.startswith(API_PATH + "/"):
            self._send_json(200, dict(INFO))
            return
        static = _find_static(path)
        if static is not None:
            status, content_type, body = static
            self._send(status, content_type, body, cacheable=(status == 200))
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self):
        path = _request_path(self.path)
        if path != API_PATH and not path.startswith(API_PATH + "/"):
            self._send_json(404, {"error": "not found"})
            return
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
