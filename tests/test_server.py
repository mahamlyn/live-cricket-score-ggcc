import json
import os
import subprocess
import sys
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from scoreboard.server import create_handler


class ServerTests(unittest.TestCase):
    def request(self, mode, path):
        server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(mode))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            connection.request("GET", path)
            response = connection.getresponse()
            result = response.status, dict(response.getheaders()), response.read()
            connection.close()
            return result
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

    def test_demo_has_four_explicitly_fictional_games(self):
        status, headers, body = self.request("demo", "/api/scoreboard")
        data = json.loads(body)
        self.assertEqual(status, 200)
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(data["mode"], "demo")
        self.assertEqual(len(data["games"]), 4)
        self.assertTrue(all(len(game["teams"]) == 2 for game in data["games"]))
        self.assertTrue(all("Example" in game["status"] for game in data["games"]))

    def test_unconfigured_never_returns_example_scores(self):
        status, _, body = self.request("unconfigured", "/api/scoreboard")
        data = json.loads(body)
        self.assertEqual(status, 503)
        self.assertEqual(data["mode"], "unconfigured")
        self.assertNotIn("games", data)

    def test_static_files_and_unknown_paths(self):
        status, headers, body = self.request("demo", "/")
        self.assertEqual(status, 200)
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn(b"Golden Grove", body)
        self.assertEqual(self.request("demo", "/../scoreboard/server.py")[0], 404)

    def test_invalid_configuration_fails_at_startup(self):
        for setting, value in (("SCOREBOARD_MODE", "live"), ("PORT", "invalid")):
            with self.subTest(setting=setting):
                environment = dict(os.environ, SCOREBOARD_MODE="demo", PORT="8080")
                environment[setting] = value
                result = subprocess.run(
                    [sys.executable, "-m", "scoreboard"],
                    env=environment,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(setting, result.stderr)


if __name__ == "__main__":
    unittest.main()
