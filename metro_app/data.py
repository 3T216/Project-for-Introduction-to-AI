from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OSM_EXPORT_PATH = DATA_DIR / "shanghai_metro_osm.json"


@dataclass(frozen=True)
class Station:
    name: str
    lat: float
    lon: float


@dataclass(frozen=True)
class Edge:
    target: str
    travel_time: float
    line: str
    distance_km: float


def _build_sample_dataset() -> tuple[dict[str, Station], dict[str, list[Edge]], str]:
    stations: dict[str, Station] = {
        "Fujin Road": Station("Fujin Road", 31.3872, 121.4896),
        "Tonghe Xincun": Station("Tonghe Xincun", 31.3610, 121.4769),
        "Shanghai Circus World": Station("Shanghai Circus World", 31.2781, 121.4547),
        "Shanghai Railway Station": Station("Shanghai Railway Station", 31.2558, 121.4647),
        "People's Square": Station("People's Square", 31.2336, 121.4752),
        "South Shaanxi Road": Station("South Shaanxi Road", 31.2200, 121.4587),
        "Xujiahui": Station("Xujiahui", 31.1947, 121.4368),
        "Shanghai Indoor Stadium": Station("Shanghai Indoor Stadium", 31.1859, 121.4385),
        "Jinjiang Park": Station("Jinjiang Park", 31.1504, 121.4158),
        "Hongqiao Railway Station": Station("Hongqiao Railway Station", 31.1949, 121.3270),
        "Songhong Road": Station("Songhong Road", 31.2218, 121.3608),
        "Zhongshan Park": Station("Zhongshan Park", 31.2241, 121.4246),
        "Jing'an Temple": Station("Jing'an Temple", 31.2239, 121.4457),
        "East Nanjing Road": Station("East Nanjing Road", 31.2416, 121.4902),
        "Lujiazui": Station("Lujiazui", 31.2384, 121.4997),
        "Century Avenue": Station("Century Avenue", 31.2303, 121.5190),
        "Longyang Road": Station("Longyang Road", 31.2107, 121.5570),
        "Yuyuan Garden": Station("Yuyuan Garden", 31.2270, 121.4929),
        "Laoximen": Station("Laoximen", 31.2174, 121.4907),
        "Xintiandi": Station("Xintiandi", 31.2205, 121.4740),
        "Shanghai Library": Station("Shanghai Library", 31.2088, 121.4498),
        "Jiaotong University": Station("Jiaotong University", 31.2022, 121.4350),
        "Shaanxi South Road": Station("Shaanxi South Road", 31.2200, 121.4587),
    }

    graph: dict[str, list[Edge]] = {station: [] for station in stations}

    def connect(station_a: str, station_b: str, travel_time: float, line: str, distance_km: float) -> None:
        graph[station_a].append(Edge(station_b, travel_time, line, distance_km))
        graph[station_b].append(Edge(station_a, travel_time, line, distance_km))

    connect("Fujin Road", "Tonghe Xincun", 5.0, "Line 1", 2.9)
    connect("Tonghe Xincun", "Shanghai Circus World", 6.0, "Line 1", 4.2)
    connect("Shanghai Circus World", "Shanghai Railway Station", 7.0, "Line 1", 4.3)
    connect("Shanghai Railway Station", "People's Square", 5.0, "Line 1", 3.1)
    connect("People's Square", "South Shaanxi Road", 4.0, "Line 1", 2.1)
    connect("South Shaanxi Road", "Xujiahui", 5.0, "Line 1", 3.5)
    connect("Xujiahui", "Shanghai Indoor Stadium", 3.0, "Line 1", 1.1)
    connect("Shanghai Indoor Stadium", "Jinjiang Park", 6.0, "Line 1", 4.6)

    connect("Hongqiao Railway Station", "Songhong Road", 6.0, "Line 2", 4.8)
    connect("Songhong Road", "Zhongshan Park", 7.0, "Line 2", 6.1)
    connect("Zhongshan Park", "Jing'an Temple", 4.0, "Line 2", 2.0)
    connect("Jing'an Temple", "People's Square", 4.0, "Line 2", 2.8)
    connect("People's Square", "East Nanjing Road", 3.0, "Line 2", 1.7)
    connect("East Nanjing Road", "Lujiazui", 4.0, "Line 2", 1.3)
    connect("Lujiazui", "Century Avenue", 3.0, "Line 2", 2.1)
    connect("Century Avenue", "Longyang Road", 5.0, "Line 2", 4.2)

    connect("Hongqiao Railway Station", "Zhongshan Park", 9.0, "Line 10", 9.3)
    connect("Zhongshan Park", "Jiaotong University", 5.0, "Line 10", 2.8)
    connect("Jiaotong University", "Shaanxi South Road", 4.0, "Line 10", 2.7)
    connect("Shaanxi South Road", "Xintiandi", 4.0, "Line 10", 1.9)
    connect("Xintiandi", "Yuyuan Garden", 4.0, "Line 10", 2.1)
    connect("Yuyuan Garden", "East Nanjing Road", 4.0, "Line 10", 1.8)

    connect("Shanghai Indoor Stadium", "Xujiahui", 3.0, "Line 9", 1.1)
    connect("Xujiahui", "Jiaotong University", 3.0, "Line 9", 1.2)
    connect("Jiaotong University", "Shanghai Library", 3.0, "Line 9", 1.5)
    connect("Shanghai Library", "Shaanxi South Road", 3.0, "Line 9", 1.8)
    connect("Shaanxi South Road", "Laoximen", 5.0, "Line 9", 4.0)
    connect("Laoximen", "Century Avenue", 8.0, "Line 9", 5.5)

    connect("Zhongshan Park", "Xintiandi", 7.0, "Line 13", 6.0)
    connect("Xintiandi", "Laoximen", 3.0, "Line 13", 1.7)
    connect("Laoximen", "Yuyuan Garden", 2.0, "Line 13", 1.1)

    return stations, graph, "sample"


def _load_osm_export(path: Path) -> tuple[dict[str, Station], dict[str, list[Edge]], str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    stations = {
        station["name"]: Station(
            name=station["name"],
            lat=station["lat"],
            lon=station["lon"],
        )
        for station in payload["stations"]
    }
    graph: dict[str, list[Edge]] = {station_name: [] for station_name in stations}
    for edge in payload["edges"]:
        graph[edge["source"]].append(
            Edge(
                target=edge["target"],
                travel_time=edge["travel_time"],
                line=edge["line"],
                distance_km=edge["distance_km"],
            )
        )
    return stations, graph, payload.get("source", "osm")


def load_network() -> tuple[dict[str, Station], dict[str, list[Edge]], str]:
    if OSM_EXPORT_PATH.exists():
        return _load_osm_export(OSM_EXPORT_PATH)
    return _build_sample_dataset()


STATIONS, GRAPH, DATA_SOURCE = load_network()
