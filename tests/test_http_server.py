import json
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from functools import partial
from http.server import ThreadingHTTPServer

from server import MetroRequestHandler, WEB_DIR


class HTTPEndpointsTests(unittest.TestCase):
    """Integration tests for Metro HTTP server endpoints."""

    @classmethod
    def setUpClass(cls):
        """Start HTTP server on ephemeral port before all tests."""
        handler = partial(MetroRequestHandler, directory=str(WEB_DIR))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        """Shutdown server after all tests."""
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path):
        """Helper to GET path and return (status_code, json_body)."""
        url = f"http://127.0.0.1:{self.port}{path}"
        try:
            with urllib.request.urlopen(url) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_network_endpoint_returns_stations_and_lines(self):
        """GET /api/network → 200, contains stations, edges, lines, algorithms."""
        status, body = self._get("/api/network")

        self.assertEqual(status, 200)
        self.assertIn("stations", body)
        self.assertIn("edges", body)
        self.assertIn("lines", body)
        self.assertIn("algorithms", body)
        self.assertGreater(len(body["stations"]), 0)

    def test_routes_endpoint_valid_request(self):
        """GET /api/routes?start=Hongqiao Railway Station&goal=Century Avenue&algorithm=astar → 200, path correct."""
        start = "Hongqiao Railway Station"
        goal = "Century Avenue"
        params = urllib.parse.urlencode({"start": start, "goal": goal, "algorithm": "astar"})
        status, body = self._get(f"/api/routes?{params}")

        self.assertEqual(status, 200)
        self.assertIn("results", body)
        self.assertGreater(len(body["results"]), 0)
        path = body["results"][0]["path"]
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], goal)

    def test_routes_endpoint_missing_start_param(self):
        """GET /api/routes?goal=X (no start) → 400, error JSON."""
        params = urllib.parse.urlencode({"goal": "Century Avenue"})
        status, body = self._get(f"/api/routes?{params}")

        self.assertEqual(status, 400)
        self.assertIn("error", body)

    def test_routes_endpoint_unknown_station(self):
        """GET /api/routes?start=NONEXISTENT&goal=Century Avenue → 400, error message."""
        params = urllib.parse.urlencode({"start": "NONEXISTENT_STATION_XYZ", "goal": "Century Avenue"})
        status, body = self._get(f"/api/routes?{params}")

        self.assertIn(status, [400, 404])
        self.assertIn("error", body)

    def test_routes_endpoint_invalid_algorithm(self):
        """GET /api/routes?...&algorithm=bogus → 400, error."""
        params = urllib.parse.urlencode({
            "start": "Hongqiao Railway Station",
            "goal": "Century Avenue",
            "algorithm": "bogus_algorithm_xyz"
        })
        status, body = self._get(f"/api/routes?{params}")

        self.assertEqual(status, 400)
        self.assertIn("error", body)

    def test_nearest_station_returns_closest(self):
        """GET /api/nearest-station?lat=31.23&lon=121.47 → 200, distance_km >= 0."""
        status, body = self._get("/api/nearest-station?lat=31.23&lon=121.47")

        self.assertEqual(status, 200)
        self.assertIn("station", body)
        self.assertIn("distance_km", body["station"])
        self.assertGreaterEqual(body["station"]["distance_km"], 0)

    def test_nearest_station_rejects_non_float_coords(self):
        """GET /api/nearest-station?lat=abc&lon=def → 400, error."""
        status, body = self._get("/api/nearest-station?lat=abc&lon=def")

        self.assertEqual(status, 400)
        self.assertIn("error", body)

    def test_routes_by_points_valid(self):
        """GET /api/routes-by-points?start_lat=31.1949&start_lon=121.3270&goal_lat=31.2319&goal_lon=121.4783&algorithm=astar → 200, point_selection present."""
        params = urllib.parse.urlencode({
            "start_lat": "31.1949",
            "start_lon": "121.3270",
            "goal_lat": "31.2319",
            "goal_lon": "121.4783",
            "algorithm": "astar"
        })
        status, body = self._get(f"/api/routes-by-points?{params}")

        self.assertEqual(status, 200)
        self.assertIn("point_selection", body)
        self.assertIn("start_station", body["point_selection"])

    def test_unknown_endpoint_returns_404(self):
        """GET /api/does-not-exist → 404."""
        url = f"http://127.0.0.1:{self.port}/api/does-not-exist"
        try:
            with urllib.request.urlopen(url) as resp:
                self.fail("Expected 404, but request succeeded")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_root_serves_html(self):
        """GET / → 200, Content-Type is text/html."""
        url = f"http://127.0.0.1:{self.port}/"
        try:
            with urllib.request.urlopen(url) as resp:
                self.assertEqual(resp.status, 200)
                content_type = resp.headers.get("Content-Type", "")
                self.assertTrue(content_type.startswith("text/html"),
                               f"Expected text/html, got {content_type}")
        except urllib.error.HTTPError as e:
            self.fail(f"Root endpoint should return 200, got {e.code}")


if __name__ == "__main__":
    unittest.main()
