from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict
from pathlib import Path

from metro_app.data import DATA_DIR
from metro_app.geo import haversine_km


OVERPASS_URLS = (
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
DEFAULT_OUTPUT = DATA_DIR / "shanghai_metro_osm.json"
SHANGHAI_QUERY = """
[out:json][timeout:120];
area["name:en"="Shanghai"]["boundary"="administrative"]->.searchArea;
(
  relation(area.searchArea)["type"="route"]["route"="subway"];
);
out body center qt;
>;
out body center qt;
""".strip()


def _station_name(tags: dict[str, str]) -> str | None:
    for key in ("name:en", "official_name:en", "name", "official_name"):
        value = tags.get(key)
        if value:
            return value.strip()
    return None


def _element_coords(element: dict) -> tuple[float, float] | None:
    if "lat" in element and "lon" in element:
        return element["lat"], element["lon"]
    center = element.get("center")
    if center:
        return center["lat"], center["lon"]
    return None


def _estimate_minutes(distance_km: float) -> float:
    # Shanghai Metro segment travel times are not stored reliably in OSM,
    # so use a distance-based approximation for routing cost.
    return round(max(1.0, (distance_km / 35.0) * 60.0 + 0.8), 2)


def _looks_like_station_member(member: dict) -> bool:
    role = member.get("role", "")
    return any(token in role for token in ("stop", "platform", "station"))


def fetch_overpass(query: str = SHANGHAI_QUERY) -> dict:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "User-Agent": "ShanghaiMetroRouteFinder/1.0",
    }
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    last_error: Exception | None = None

    for url in OVERPASS_URLS:
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as error:
            last_error = error

        get_url = f"{url}?{urllib.parse.urlencode({'data': query})}"
        request = urllib.request.Request(get_url, headers={"Accept": "application/json", "User-Agent": "ShanghaiMetroRouteFinder/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as error:
            last_error = error

    assert last_error is not None
    raise last_error


def build_dataset(elements: list[dict]) -> dict:
    by_key = {(element["type"], element["id"]): element for element in elements}
    stations: "OrderedDict[str, dict[str, float | str]]" = OrderedDict()
    edge_map: dict[tuple[str, str, str], dict[str, float | str]] = {}

    for relation in elements:
        if relation.get("type") != "relation":
            continue
        tags = relation.get("tags", {})
        if tags.get("type") != "route" or tags.get("route") != "subway":
            continue

        line_name = tags.get("ref") or tags.get("name:en") or tags.get("name") or f"relation-{relation['id']}"
        ordered_stations: list[str] = []

        for member in relation.get("members", []):
            if not _looks_like_station_member(member):
                continue
            element = by_key.get((member["type"], member["ref"]))
            if not element:
                continue
            element_tags = element.get("tags", {})
            station_name = _station_name(element_tags)
            coords = _element_coords(element)
            if not station_name or coords is None:
                continue

            if station_name not in stations:
                stations[station_name] = {
                    "name": station_name,
                    "lat": coords[0],
                    "lon": coords[1],
                }

            if not ordered_stations or ordered_stations[-1] != station_name:
                ordered_stations.append(station_name)

        for source, target in zip(ordered_stations, ordered_stations[1:]):
            source_station = stations[source]
            target_station = stations[target]
            distance_km = haversine_km(
                float(source_station["lat"]),
                float(source_station["lon"]),
                float(target_station["lat"]),
                float(target_station["lon"]),
            )
            travel_time = _estimate_minutes(distance_km)
            for left, right in ((source, target), (target, source)):
                edge_map[(left, right, line_name)] = {
                    "source": left,
                    "target": right,
                    "line": line_name,
                    "distance_km": round(distance_km, 3),
                    "travel_time": travel_time,
                }

    return {
        "source": "osm_overpass_shanghai",
        "query": SHANGHAI_QUERY,
        "stations": list(stations.values()),
        "edges": list(edge_map.values()),
    }


def save_dataset(output_path: Path = DEFAULT_OUTPUT) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = fetch_overpass()
    dataset = build_dataset(payload["elements"])
    output_path.write_text(json.dumps(dataset, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    try:
        path = save_dataset()
        print(f"Saved OSM Shanghai Metro data to {path}")
    except urllib.error.URLError as error:
        print(f"Failed to download OSM data: {error}")
