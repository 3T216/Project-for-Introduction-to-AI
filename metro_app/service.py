from __future__ import annotations

from metro_app.algorithms import (
    SearchResult,
    a_star_search,
    greedy_best_first_search,
    uniform_cost_search,
)
from metro_app.data import DATA_SOURCE, Edge, GRAPH, STATIONS
from metro_app.geo import haversine_km

MAX_NEAREST_DISTANCE_KM = 50.0


def find_nearest_station(lat: float, lon: float) -> tuple[str, float]:
    nearest_name = ""
    nearest_distance = float("inf")

    for station in STATIONS.values():
        distance = haversine_km(lat, lon, station.lat, station.lon)
        if distance < nearest_distance:
            nearest_name = station.name
            nearest_distance = distance

    if not nearest_name:
        raise ValueError("Không tìm thấy ga nào trong bộ dữ liệu hiện tại.")

    if nearest_distance > MAX_NEAREST_DISTANCE_KM:
        raise ValueError(
            f"Điểm bạn chọn nằm ngoài vùng Thượng Hải "
            f"(cách ga gần nhất {nearest_distance:.1f} km)."
        )

    return nearest_name, round(nearest_distance, 3)


def available_lines() -> list[str]:
    return sorted({edge.line for edges in GRAPH.values() for edge in edges})


def normalize_segment(station_a: str, station_b: str) -> tuple[str, str]:
    return tuple(sorted((station_a, station_b)))


def available_segments() -> set[tuple[str, str]]:
    segments: set[tuple[str, str]] = set()
    for source, edges in GRAPH.items():
        for edge in edges:
            segments.add(normalize_segment(source, edge.target))
    return segments


def build_filtered_graph(
    blocked_lines: set[str] | None = None,
    blocked_segments: set[tuple[str, str]] | None = None,
) -> dict[str, list[Edge]]:
    blocked = blocked_lines or set()
    blocked_pairs = blocked_segments or set()
    return {
        station_name: [
            edge
            for edge in edges
            if edge.line not in blocked and normalize_segment(station_name, edge.target) not in blocked_pairs
        ]
        for station_name, edges in GRAPH.items()
    }


def available_algorithms() -> list[str]:
    return ["ucs", "greedy", "astar"]


def run_algorithm(
    algorithm: str,
    graph: dict[str, list[Edge]],
    start: str,
    goal: str,
) -> SearchResult:
    normalized = algorithm.lower()
    if normalized == "ucs":
        return uniform_cost_search(graph, start, goal)
    if normalized == "greedy":
        return greedy_best_first_search(graph, STATIONS, start, goal)
    if normalized == "astar":
        return a_star_search(graph, STATIONS, start, goal)
    raise ValueError(f"Thuật toán không hợp lệ: {algorithm}.")


def find_routes(
    start: str,
    goal: str,
    blocked_lines: set[str] | None = None,
    blocked_segments: set[tuple[str, str]] | None = None,
    algorithm: str | None = None,
) -> list[SearchResult]:
    if start == goal:
        raise ValueError("Ga đi và ga đến phải khác nhau.")
    if start not in STATIONS or goal not in STATIONS:
        raise ValueError("Tên ga không tồn tại trong bộ dữ liệu hiện tại.")
    if blocked_lines:
        invalid_lines = blocked_lines - set(available_lines())
        if invalid_lines:
            raise ValueError(f"Tuyến bị cấm không hợp lệ: {', '.join(sorted(invalid_lines))}.")
    if blocked_segments:
        invalid_stations = {
            station_name
            for segment in blocked_segments
            for station_name in segment
            if station_name not in STATIONS
        }
        if invalid_stations:
            raise ValueError(f"Ga trong đoạn bị cấm không hợp lệ: {', '.join(sorted(invalid_stations))}.")

        invalid_segments = {segment for segment in blocked_segments if normalize_segment(*segment) not in available_segments()}
        if invalid_segments:
            invalid_text = ", ".join(f"{segment[0]} - {segment[1]}" for segment in sorted(invalid_segments))
            raise ValueError(f"Đoạn bị cấm không hợp lệ: {invalid_text}.")
    if algorithm is not None and algorithm.lower() not in set(available_algorithms()):
        raise ValueError(f"Thuật toán không hợp lệ: {algorithm}.")

    normalized_segments = {normalize_segment(*segment) for segment in (blocked_segments or set())}
    filtered_graph = build_filtered_graph(blocked_lines, normalized_segments)

    try:
        if algorithm is not None:
            return [run_algorithm(algorithm, filtered_graph, start, goal)]

        return [
            uniform_cost_search(filtered_graph, start, goal),
            greedy_best_first_search(filtered_graph, STATIONS, start, goal),
            a_star_search(filtered_graph, STATIONS, start, goal),
        ]
    except ValueError as error:
        if blocked_lines:
            blocked_text = ", ".join(sorted(blocked_lines))
            raise ValueError(f"Không tìm được lộ trình hợp lệ khi cấm các tuyến: {blocked_text}.") from error
        if normalized_segments:
            blocked_text = ", ".join(f"{segment[0]} - {segment[1]}" for segment in sorted(normalized_segments))
            raise ValueError(f"Không tìm được lộ trình hợp lệ khi cấm các đoạn: {blocked_text}.") from error
        raise


def find_routes_by_points(
    start_lat: float,
    start_lon: float,
    goal_lat: float,
    goal_lon: float,
    blocked_lines: set[str] | None = None,
    blocked_segments: set[tuple[str, str]] | None = None,
    algorithm: str | None = None,
) -> list[SearchResult]:
    start_station_name, _ = find_nearest_station(start_lat, start_lon)
    goal_station_name, _ = find_nearest_station(goal_lat, goal_lon)
    if start_station_name == goal_station_name:
        raise ValueError(
            f"Hai điểm bạn chọn đều thuộc ga {start_station_name}. "
            f"Hãy chọn 2 điểm xa nhau hơn."
        )
    return find_routes(start_station_name, goal_station_name, blocked_lines, blocked_segments, algorithm)


def summarize_segments(path: list[str], lines: list[str]) -> list[str]:
    if len(path) < 2:
        return []

    summary: list[str] = []
    current_line = lines[0]
    segment_start = path[0]

    for index in range(1, len(lines)):
        if lines[index] != current_line:
            summary.append(f"{current_line}: {segment_start} -> {path[index]}")
            segment_start = path[index]
            current_line = lines[index]

    summary.append(f"{current_line}: {segment_start} -> {path[-1]}")
    return summary
