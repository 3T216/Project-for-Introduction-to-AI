from __future__ import annotations

import heapq
from dataclasses import dataclass
from itertools import count

from metro_app.data import Edge, Station
from metro_app.geo import haversine_km


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
    return haversine_km(here.lat, here.lon, destination.lat, destination.lon) / 35.0 * 60.0


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
            if edge.target in came_from:
                continue
            came_from[edge.target] = (current, edge.line)
            new_cost = current_cost + edge.travel_time
            best_cost[edge.target] = new_cost
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


def dijkstra_search(
    graph: dict[str, list[Edge]],
    start: str,
    goal: str,
) -> SearchResult:
    dist: dict[str, float] = {start: 0.0}
    came_from: dict[str, tuple[str, str] | None] = {start: None}
    heap: list[tuple[float, str]] = [(0.0, start)]
    explored = 0

    while heap:
        cost, node = heapq.heappop(heap)
        if cost > dist[node]:  # stale entry
            continue
        explored += 1
        for edge in graph.get(node, []):
            new_cost = cost + edge.travel_time
            if new_cost < dist.get(edge.target, float("inf")):
                dist[edge.target] = new_cost
                came_from[edge.target] = (node, edge.line)
                heapq.heappush(heap, (new_cost, edge.target))

    if goal not in dist:
        raise ValueError(f"Không có đường từ {start} đến {goal}.")

    path, lines = _reconstruct_path(came_from, goal)
    return SearchResult(
        algorithm="Dijkstra",
        path=path,
        total_cost=round(dist[goal], 2),
        explored_nodes=explored,
        line_sequence=lines,
        total_distance_km=_path_distance(graph, path, lines),
    )
