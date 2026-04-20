import unittest

from metro_app.data import DATA_SOURCE, STATIONS
from metro_app.service import available_algorithms, available_lines, find_nearest_station, find_routes
from server import _route_by_points_payload, _route_payload, _station_payload


class RouteSearchTests(unittest.TestCase):
    def test_station_dataset_is_available(self) -> None:
        self.assertGreater(len(STATIONS), 2)
        self.assertIn(DATA_SOURCE, {"sample", "osm_overpass_shanghai"})

    def test_route_results_cover_three_algorithms(self) -> None:
        results = find_routes("Hongqiao Railway Station", "Century Avenue")

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].algorithm, "UCS")
        self.assertEqual(results[1].algorithm, "Greedy Best-First Search")
        self.assertEqual(results[2].algorithm, "A*")

    def test_ucs_returns_a_valid_path(self) -> None:
        results = find_routes("Hongqiao Railway Station", "Century Avenue")
        ucs_result = results[0]

        self.assertGreater(ucs_result.total_cost, 0)
        self.assertGreater(ucs_result.total_distance_km, 0)
        self.assertEqual(ucs_result.path[0], "Hongqiao Railway Station")
        self.assertEqual(ucs_result.path[-1], "Century Avenue")

    def test_route_payload_matches_web_api_shape(self) -> None:
        payload = _route_payload("Hongqiao Railway Station", "Century Avenue")

        self.assertEqual(payload["start"], "Hongqiao Railway Station")
        self.assertEqual(payload["goal"], "Century Avenue")
        self.assertEqual(len(payload["results"]), 3)
        self.assertGreater(len(_station_payload()), 2)
        self.assertIsNone(payload["algorithm"])

    def test_find_nearest_station_returns_station_and_distance(self) -> None:
        station_name, distance_km = find_nearest_station(31.1949, 121.3270)

        self.assertIn(station_name, STATIONS)
        self.assertGreaterEqual(distance_km, 0)

    def test_route_by_points_payload_contains_nearest_station_mapping(self) -> None:
        payload = _route_by_points_payload(31.1949, 121.3270, 31.2303, 121.5190)

        self.assertIn("point_selection", payload)
        self.assertIn("start_station", payload["point_selection"])
        self.assertIn("goal_station", payload["point_selection"])
        self.assertEqual(len(payload["results"]), 3)

    def test_find_routes_respects_blocked_lines(self) -> None:
        results = find_routes("Hongqiao Railway Station", "Century Avenue", blocked_lines={"2"})

        self.assertEqual(len(results), 3)
        self.assertNotIn("2", results[0].line_sequence)

    def test_route_payload_exposes_blocked_lines(self) -> None:
        payload = _route_payload("Hongqiao Railway Station", "Century Avenue", blocked_lines={"2"})

        self.assertEqual(payload["blocked_lines"], ["2"])
        self.assertNotIn("2", payload["results"][0]["line_sequence"])

    def test_blocking_all_lines_makes_route_invalid(self) -> None:
        with self.assertRaisesRegex(ValueError, "Không tìm được lộ trình hợp lệ"):
            find_routes("Hongqiao Railway Station", "Century Avenue", blocked_lines=set(available_lines()))

    def test_single_algorithm_mode_returns_one_result(self) -> None:
        results = find_routes("Hongqiao Railway Station", "Century Avenue", algorithm="astar")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].algorithm, "A*")

    def test_route_payload_accepts_algorithm_filter(self) -> None:
        payload = _route_payload("Hongqiao Railway Station", "Century Avenue", algorithm="greedy")

        self.assertEqual(payload["algorithm"], "greedy")
        self.assertEqual(len(payload["results"]), 1)
        self.assertEqual(payload["results"][0]["algorithm"], "Greedy Best-First Search")

    def test_available_algorithms_are_exposed(self) -> None:
        self.assertEqual(available_algorithms(), ["ucs", "greedy", "astar"])

    def test_find_routes_respects_blocked_segments(self) -> None:
        results = find_routes(
            "Hongqiao Railway Station",
            "Century Avenue",
            blocked_segments={("East Nanjing Road", "Lujiazui")},
            algorithm="astar",
        )

        self.assertEqual(len(results), 1)
        path_pairs = list(zip(results[0].path, results[0].path[1:]))
        self.assertNotIn(("East Nanjing Road", "Lujiazui"), path_pairs)
        self.assertNotIn(("Lujiazui", "East Nanjing Road"), path_pairs)

    def test_route_payload_exposes_blocked_segments(self) -> None:
        payload = _route_payload(
            "Hongqiao Railway Station",
            "Century Avenue",
            blocked_segments={("East Nanjing Road", "Lujiazui")},
            algorithm="astar",
        )

        self.assertEqual(len(payload["blocked_segments"]), 1)
        self.assertEqual(payload["blocked_segments"][0]["source"], "East Nanjing Road")
        self.assertEqual(payload["blocked_segments"][0]["target"], "Lujiazui")


if __name__ == "__main__":
    unittest.main()
