from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from itertools import count

from metro_app.data import Edge, Station


@dataclass
class SearchResult:
    algorithm: str
    path: list[str]
    total_cost: float
    explored_nodes: int
    line_sequence: list[str]
    total_distance_km: float


def _reconstruct_path(
    came_from: dict[str, tuple[str, str] | None],
    goal: str,
) -> tuple[list[str], list[str]]:
    path = [goal]
    lines: list[str] = []
    current = goal
    while came_from[current] is not None:
        previous, line = came_from[current]
        path.append(previous)
        lines.append(line)
        current = previous
    path.reverse()
    lines.reverse()
    return path, lines


def _path_distance(graph: dict[str, list[Edge]], path: list[str], lines: list[str]) -> float:
    total = 0.0
    for source, target, line in zip(path, path[1:], lines):
        for edge in graph[source]:
            if edge.target == target and edge.line == line:
                total += edge.distance_km
                break
    return round(total, 2)


def heuristic(stations: dict[str, Station], current: str, goal: str) -> float:
    here = stations[current]
    destination = stations[goal]
    return _haversine_km(here.lat, here.lon, destination.lat, destination.lon) / 35.0 * 60.0


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def uniform_cost_search(
    graph: dict[str, list[Edge]],
    start: str,
    goal: str,
) -> SearchResult:
    queue: list[tuple[float, int, str]] = [(0.0, 0, start)]
    tracker = count(1)
    came_from: dict[str, tuple[str, str] | None] = {start: None}
    best_cost = {start: 0.0}
    explored = 0

    while queue:
        current_cost, _, current = heapq.heappop(queue)
        if current_cost > best_cost[current]:
            continue

        explored += 1
        if current == goal:
            path, lines = _reconstruct_path(came_from, goal)
            return SearchResult("UCS", path, round(current_cost, 2), explored, lines, _path_distance(graph, path, lines))

        for edge in graph[current]:
            new_cost = current_cost + edge.travel_time
            if edge.target not in best_cost or new_cost < best_cost[edge.target]:
                best_cost[edge.target] = new_cost
                came_from[edge.target] = (current, edge.line)
                heapq.heappush(queue, (new_cost, next(tracker), edge.target))

    raise ValueError(f"Cannot reach {goal} from {start}.")


def greedy_best_first_search(
    graph: dict[str, list[Edge]],
    stations: dict[str, Station],
    start: str,
    goal: str,
) -> SearchResult:
    queue: list[tuple[float, float, int, str]] = [(heuristic(stations, start, goal), 0.0, 0, start)]
    tracker = count(1)
    came_from: dict[str, tuple[str, str] | None] = {start: None}
    best_cost = {start: 0.0}
    visited: set[str] = set()
    explored = 0

    while queue:
        _, current_cost, _, current = heapq.heappop(queue)
        if current in visited:
            continue

        visited.add(current)
        explored += 1
        if current == goal:
            path, lines = _reconstruct_path(came_from, goal)
            return SearchResult(
                "Greedy Best-First Search",
                path,
                round(current_cost, 2),
                explored,
                lines,
                _path_distance(graph, path, lines),
            )

        for edge in graph[current]:
            if edge.target in visited:
                continue
            new_cost = current_cost + edge.travel_time
            if edge.target not in best_cost or new_cost < best_cost[edge.target]:
                best_cost[edge.target] = new_cost
                came_from[edge.target] = (current, edge.line)
                priority = heuristic(stations, edge.target, goal)
                heapq.heappush(queue, (priority, new_cost, next(tracker), edge.target))

    raise ValueError(f"Cannot reach {goal} from {start}.")


def a_star_search(
    graph: dict[str, list[Edge]],
    stations: dict[str, Station],
    start: str,
    goal: str,
) -> SearchResult:
    queue: list[tuple[float, float, int, str]] = [(heuristic(stations, start, goal), 0.0, 0, start)]
    tracker = count(1)
    came_from: dict[str, tuple[str, str] | None] = {start: None}
    best_cost = {start: 0.0}
    explored = 0

    while queue:
        _, current_cost, _, current = heapq.heappop(queue)
        if current_cost > best_cost[current]:
            continue

        explored += 1
        if current == goal:
            path, lines = _reconstruct_path(came_from, goal)
            return SearchResult("A*", path, round(current_cost, 2), explored, lines, _path_distance(graph, path, lines))

        for edge in graph[current]:
            new_cost = current_cost + edge.travel_time
            if edge.target not in best_cost or new_cost < best_cost[edge.target]:
                best_cost[edge.target] = new_cost
                came_from[edge.target] = (current, edge.line)
                priority = new_cost + heuristic(stations, edge.target, goal)
                heapq.heappush(queue, (priority, new_cost, next(tracker), edge.target))

    raise ValueError(f"Cannot reach {goal} from {start}.")
