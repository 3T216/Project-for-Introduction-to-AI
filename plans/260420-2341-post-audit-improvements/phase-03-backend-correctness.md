# Phase 03 — Backend Correctness Fixes

## Context Links
- Audit items: P1 #2 (same-station error), P1 #3 (geo bounds), P1 #4 (Greedy pure)
- Files: [metro_app/service.py](../../metro_app/service.py), [metro_app/algorithms.py](../../metro_app/algorithms.py)

## Overview
- **Priority:** P1
- **Status:** Todo
- **Dependency:** Cần [Phase 04](phase-04-haversine-geo-module.md) xong trước (dùng `geo.haversine_km` mới).
- **Mô tả:** 3 fix nhỏ ở backend:
  1. Khi 2 điểm click map quá gần → rơi vào cùng ga → báo lỗi rõ ràng thay vì generic "Ga đi và ga đến phải khác nhau".
  2. `find_nearest_station` reject khi điểm cách > 50 km ga gần nhất (ngoài vùng Thượng Hải).
  3. Greedy BFS: chỉ set `came_from` lần đầu enqueue — "pure greedy" theo sách.

## Key Insights

### Same-station message
[service.py:99](../../metro_app/service.py#L99) — `_route_by_points_payload` gọi `find_routes(start_station_name, goal_station_name)`. Nếu trùng, `find_routes` raise `ValueError("Ga đi và ga đến phải khác nhau.")`. Với map click, lý do thực là 2 điểm quá gần → nên check sớm và raise message cụ thể.

### Geo bounds
[service.py:24-37](../../metro_app/service.py#L24) — `find_nearest_station(lat, lon, stations)` scan toàn bộ → return min. Click ở châu Phi vẫn ra ga Thượng Hải. Frontend `maxBounds` chặn 99% nhưng API trần vẫn bị. Thêm soft check: nếu `distance_km > 50` → raise `ValueError("Điểm bạn chọn nằm ngoài vùng Thượng Hải (cách ga gần nhất {distance} km).")`.

### Greedy pure
[algorithms.py:95-136](../../metro_app/algorithms.py#L95) — hiện tại: mỗi lần pop node, iterate neighbors, push vào heap, và **set `came_from[neighbor] = (current, line)` mỗi lần** (line ~132). Vấn đề: nếu neighbor đã được enqueue bởi node khác, `came_from` bị ghi đè → đường đi phụ thuộc thứ tự pop, không "thuần" theo heuristic.

Fix: set `came_from[neighbor]` **chỉ khi `neighbor not in came_from`**.

## Requirements

### Functional
1. `find_nearest_station` raise `ValueError` nếu distance > 50 km.
2. `_route_by_points_payload` check `start_station.name == goal_station.name` **trước** khi gọi `find_routes`, raise message Việt rõ ràng.
3. `greedy_best_first_search` không ghi đè `came_from` khi neighbor đã có.

### Non-functional
- Không đổi API signature — chỉ đổi error message/raise condition.
- Tất cả 14 test hiện tại vẫn pass.
- Thêm 3 test mới cho 3 hành vi mới.

## Architecture

### service.py thay đổi
```python
MAX_NEAREST_DISTANCE_KM = 50.0

def find_nearest_station(lat, lon, stations):
    nearest = min(stations, key=lambda s: geo.haversine_km(lat, lon, s.lat, s.lon))
    distance = geo.haversine_km(lat, lon, nearest.lat, nearest.lon)
    if distance > MAX_NEAREST_DISTANCE_KM:
        raise ValueError(
            f"Điểm bạn chọn nằm ngoài vùng Thượng Hải "
            f"(cách ga gần nhất {distance:.1f} km)."
        )
    return nearest, distance
```

### _route_by_points_payload check
```python
start_station, start_distance = find_nearest_station(start_lat, start_lon, stations)
goal_station, goal_distance = find_nearest_station(goal_lat, goal_lon, stations)
if start_station.name == goal_station.name:
    raise ValueError(
        f"Hai điểm bạn chọn đều thuộc ga {start_station.name}. "
        f"Hãy chọn 2 điểm xa nhau hơn."
    )
# ... continue
```

### algorithms.py Greedy pure
Trong loop:
```python
for edge in graph.get(current, []):
    if edge.target in came_from:    # <-- NEW: skip revisits
        continue
    came_from[edge.target] = (current, edge.line)
    heapq.heappush(heap, (heuristic(edge.target), edge.target))
```

## Related Code Files

### Modify
- `metro_app/service.py`:
  - Import `from metro_app import geo` (sau Phase 04).
  - Thêm constant `MAX_NEAREST_DISTANCE_KM = 50.0`.
  - Sửa `find_nearest_station` return tuple `(station, distance)` thay vì chỉ `station` — HOẶC raise trước khi return. **Chọn raise để không đổi contract**.
  - Trong `_route_by_points_payload`, check same-station sau 2 lần gọi `find_nearest_station`.
- `metro_app/algorithms.py`:
  - Sửa `greedy_best_first_search` — thêm check `if edge.target in came_from`.

### Tests
- `tests/test_algorithms.py`:
  - `test_nearest_station_rejects_far_point` — truyền `lat=0, lon=0` → expect ValueError.
  - `test_same_station_points_raise_clear_error` — 2 lat/lon rất gần → expect ValueError chứa "cùng ga" hoặc tương đương.
  - `test_greedy_does_not_overwrite_came_from` — verify path ổn định khi chạy nhiều lần.

### Create / Delete
- Không.

## Implementation Steps

1. **Sau Phase 04 xong.**
2. Thêm `MAX_NEAREST_DISTANCE_KM` constant + raise check trong `find_nearest_station`.
3. Thêm same-station check trong `_route_by_points_payload`.
4. Sửa greedy loop.
5. Viết 3 test mới.
6. Chạy `python -m unittest discover -s tests -v` → 17 tests pass.

## Todo List
- [ ] `MAX_NEAREST_DISTANCE_KM` + check trong `find_nearest_station`.
- [ ] Same-station check + Vietnamese error message trong `_route_by_points_payload`.
- [ ] Greedy `if edge.target in came_from: continue`.
- [ ] Test `nearest_station_rejects_far_point`.
- [ ] Test `same_station_points_raise_clear_error`.
- [ ] Test `greedy_stable_path`.
- [ ] Toàn bộ 17 test pass.

## Success Criteria
- `/api/nearest-station?lat=0&lon=0` trả 400 với message Việt rõ ràng.
- `/api/routes-by-points` với 2 điểm trong cùng ga → 400 message "Hai điểm bạn chọn đều thuộc ga X".
- Greedy chạy 10 lần trên cùng input → cùng path (không còn dao động).

## Risk Assessment
- **Risk:** 50 km threshold quá nhỏ nếu user muốn search Pudong airport → tính toán: Shanghai diameter ~100 km, từ trung tâm đến airport ~40 km → 50 km OK, tăng lên 70 nếu cần.
  - **Mitigation:** Dùng constant, dễ chỉnh.
- **Risk:** Greedy fix có thể ảnh hưởng `test_route_results_cover_three_algorithms` hiện có nếu path đổi.
  - **Mitigation:** Nếu test fail, verify path mới vẫn hợp lệ (vẫn từ start đến goal, đi qua cạnh hợp lệ) và update expected.
- **Risk:** `find_nearest_station` đang được `test_find_nearest_station_returns_station_and_distance` gọi với điểm gần Shanghai → test hiện có không bị ảnh hưởng.

## Security Considerations
- Error messages không leak dữ liệu nhạy cảm (OK với tiếng Việt user-facing).

## Next Steps
- Sau Phase 03, chạy Phase 05 (performance) cuối cùng.
