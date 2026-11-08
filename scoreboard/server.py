import json
import logging
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

STATIC = Path(__file__).resolve().parent.parent / "static"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}

# Deliberately fictional: this data is not connected to PlayHQ.
DEMO_GAMES = [
    {
        "grade": "1st XI - A Grade",
        "fixture": "Round 4 vs Example CC at Home Oval",
        "teams": [
            {"name": "Golden Grove", "score": "8/191 (40)", "players": ["Player A 57 (56)", "Player B 32 (51)", "Player C 2/22 (4)"]},
            {"name": "Example CC", "score": "87 (24.3)", "players": ["Player D 32 (26)", "Player E 12 (11)", "Player F 3/12 (5)"]},
        ],
        "status": "Example result: won by 104 runs",
    },
    {
        "grade": "2nd XI - B Grade",
        "fixture": "Round 4 vs Example CC at Away Oval",
        "teams": [
            {"name": "Golden Grove", "score": "6/144 (35)", "players": ["Player A 45 (48)", "Player B 28 (32)", "Player C 1/19 (5)"]},
            {"name": "Example CC", "score": "4/145 (31)", "players": ["Player D 48 (42)", "Player E 26 (30)", "Player F 2/21 (5)"]},
        ],
        "status": "Example result: lost by 6 wickets",
    },
    {
        "grade": "3rd XI - C Grade",
        "fixture": "Round 4 vs Example CC at Home Oval",
        "teams": [
            {"name": "Golden Grove", "score": "3/105 (23)", "players": ["Player A 42 (38)", "Player B 21 (27)"]},
            {"name": "Example CC", "score": "Yet to bat", "players": []},
        ],
        "status": "Example: in play",
    },
    {
        "grade": "4th XI - D Grade",
        "fixture": "Round 4 vs Example CC at Away Oval",
        "teams": [
            {"name": "Golden Grove", "score": "Not started", "players": []},
            {"name": "Example CC", "score": "Not started", "players": []},
        ],
        "status": "Example: upcoming fixture",
    },
]


def create_handler(mode):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/api/scoreboard":
                if mode == "demo":
                    self.send_json(200, {"mode": "demo", "games": DEMO_GAMES})
                else:
                    self.send_json(503, {"mode": "unconfigured", "error": "PlayHQ integration is not configured or implemented."})
                return
            entry = STATIC_FILES.get(self.path)
            if entry is None:
                self.send_error(404)
                return
            filename, content_type = entry
            try:
                body = (STATIC / filename).read_bytes()
            except OSError:
                logging.exception("Cannot read static file %s", filename)
                self.send_error(500)
                return
            self.send_body(200, content_type, body)

        def send_json(self, status, value):
            self.send_body(status, "application/json; charset=utf-8", json.dumps(value).encode("utf-8"))

        def send_body(self, status, content_type, body):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

    return Handler


def main():
    logging.basicConfig(level=logging.INFO)
    mode = os.environ.get("SCOREBOARD_MODE", "demo")
    if mode not in ("demo", "unconfigured"):
        raise SystemExit("SCOREBOARD_MODE must be 'demo' or 'unconfigured'")
    try:
        port = int(os.environ.get("PORT", "8080"))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise SystemExit("PORT must be an integer from 1 to 65535")
    server = ThreadingHTTPServer(("0.0.0.0", port), create_handler(mode))
    logging.info("Starting scoreboard in %s mode on port %d", mode, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
