from __future__ import annotations

import json
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from metro_app.data import DATA_SOURCE, GRAPH, STATIONS
from metro_app.service import (
    available_algorithms,
    available_lines,
    find_nearest_station,
    find_routes,
    summarize_segments,
)


ROOT_DIR = Path(__file__).resolve().parent
WEB_DIR = ROOT_DIR / "web"


def _station_payload() -> list[dict[str, float | str]]:
    return [
        {
            "name": station.name,
            "lat": station.lat,
            "lon": station.lon,
        }
        for station in sorted(STATIONS.values(), key=lambda item: item.name)
    ]


def _edge_payload() -> list[dict[str, float | str]]:
    edges: list[dict[str, float | str]] = []
    seen: set[tuple[str, str, str]] = set()
    for source, neighbors in GRAPH.items():
        for edge in neighbors:
            key = tuple(sorted((source, edge.target)) + [edge.line])
            if key in seen:
                continue
            seen.add(key)
            edges.append(
                {
                    "source": source,
                    "target": edge.target,
                    "line": edge.line,
                    "distance_km": edge.distance_km,
                    "travel_time": edge.travel_time,
                }
            )
    return edges


def _route_payload(
    start: str,
    goal: str,
    blocked_lines: set[str] | None = None,
    blocked_segments: set[tuple[str, str]] | None = None,
    algorithm: str | None = None,
) -> dict[str, object]:
    results = find_routes(start, goal, blocked_lines, blocked_segments, algorithm)
    return {
        "start": start,
        "goal": goal,
        "blocked_lines": sorted(blocked_lines or set()),
        "blocked_segments": [
            {"source": segment[0], "target": segment[1]}
            for segment in sorted(blocked_segments or set())
        ],
        "algorithm": algorithm.lower() if algorithm else None,
        "results": [
            {
                "algorithm": result.algorithm,
                "path": result.path,
                "total_cost": result.total_cost,
                "explored_nodes": result.explored_nodes,
                "line_sequence": result.line_sequence,
                "total_distance_km": result.total_distance_km,
                "segments": summarize_segments(result.path, result.line_sequence),
            }
            for result in results
        ],
    }


def _nearest_station_payload(lat: float, lon: float) -> dict[str, object]:
    station_name, distance_km = find_nearest_station(lat, lon)
    station = STATIONS[station_name]
    return {
        "query_point": {"lat": lat, "lon": lon},
        "station": {
            "name": station.name,
            "lat": station.lat,
            "lon": station.lon,
            "distance_km": distance_km,
        },
    }


def _route_by_points_payload(
    start_lat: float,
    start_lon: float,
    goal_lat: float,
    goal_lon: float,
    blocked_lines: set[str] | None = None,
    blocked_segments: set[tuple[str, str]] | None = None,
    algorithm: str | None = None,
) -> dict[str, object]:
    start_station_name, start_walk_km = find_nearest_station(start_lat, start_lon)
    goal_station_name, goal_walk_km = find_nearest_station(goal_lat, goal_lon)
    payload = _route_payload(start_station_name, goal_station_name, blocked_lines, blocked_segments, algorithm)
    payload["point_selection"] = {
        "start_point": {"lat": start_lat, "lon": start_lon},
        "goal_point": {"lat": goal_lat, "lon": goal_lon},
        "start_station": {
            "name": start_station_name,
            "lat": STATIONS[start_station_name].lat,
            "lon": STATIONS[start_station_name].lon,
            "distance_km": start_walk_km,
        },
        "goal_station": {
            "name": goal_station_name,
            "lat": STATIONS[goal_station_name].lat,
            "lon": STATIONS[goal_station_name].lon,
            "distance_km": goal_walk_km,
        },
    }
    return payload


class MetroRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str | None = None, **kwargs) -> None:
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/network":
            self._send_json(
                {
                    "data_source": DATA_SOURCE,
                    "stations": _station_payload(),
                    "edges": _edge_payload(),
                    "lines": available_lines(),
                    "algorithms": available_algorithms(),
                }
            )
            return

        if parsed.path == "/api/nearest-station":
            query = parse_qs(parsed.query)
            try:
                lat = float(query.get("lat", [""])[0])
                lon = float(query.get("lon", [""])[0])
            except ValueError:
                self._send_json({"error": "lat và lon phải là số hợp lệ."}, status=HTTPStatus.BAD_REQUEST)
                return

            self._send_json(_nearest_station_payload(lat, lon))
            return

        if parsed.path == "/api/routes":
            query = parse_qs(parsed.query)
            start = query.get("start", [""])[0]
            goal = query.get("goal", [""])[0]
            blocked_lines = self._parse_blocked_lines(query)
            blocked_segments = self._parse_blocked_segments(query)
            algorithm = query.get("algorithm", [""])[0] or None
            try:
                payload = _route_payload(start, goal, blocked_lines, blocked_segments, algorithm)
            except ValueError as error:
                self._send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        if parsed.path == "/api/routes-by-points":
            query = parse_qs(parsed.query)
            blocked_lines = self._parse_blocked_lines(query)
            blocked_segments = self._parse_blocked_segments(query)
            algorithm = query.get("algorithm", [""])[0] or None
            try:
                start_lat = float(query.get("start_lat", [""])[0])
                start_lon = float(query.get("start_lon", [""])[0])
                goal_lat = float(query.get("goal_lat", [""])[0])
                goal_lon = float(query.get("goal_lon", [""])[0])
                payload = _route_by_points_payload(
                    start_lat,
                    start_lon,
                    goal_lat,
                    goal_lon,
                    blocked_lines,
                    blocked_segments,
                    algorithm,
                )
            except ValueError as error:
                self._send_json({"error": str(error)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json(payload)
            return

        if parsed.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def _send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @staticmethod
    def _parse_blocked_lines(query: dict[str, list[str]]) -> set[str]:
        blocked_values = query.get("blocked_lines", [])
        blocked_lines: set[str] = set()
        for value in blocked_values:
            for item in value.split(","):
                normalized = item.strip()
                if normalized:
                    blocked_lines.add(normalized)
        return blocked_lines

    @staticmethod
    def _parse_blocked_segments(query: dict[str, list[str]]) -> set[tuple[str, str]]:
        blocked_values = query.get("blocked_segments", [])
        blocked_segments: set[tuple[str, str]] = set()
        for value in blocked_values:
            if "|||" not in value:
                continue
            source, target = value.split("|||", 1)
            source_name = source.strip()
            target_name = target.strip()
            if source_name and target_name:
                blocked_segments.add(tuple(sorted((source_name, target_name))))
        return blocked_segments


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    handler = partial(MetroRequestHandler, directory=str(WEB_DIR))
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Shanghai Metro web app running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
