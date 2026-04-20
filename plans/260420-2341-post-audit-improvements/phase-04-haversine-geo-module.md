# Phase 04 — DRY Refactor: Consolidate Haversine into `metro_app/geo.py`

## Context Links
- Audit item: P2 #2 — 3 copy haversine
- Locations:
  - [metro_app/algorithms.py#L54-L61](../../metro_app/algorithms.py#L54)
  - [metro_app/service.py#L14-L21](../../metro_app/service.py#L14)
  - [metro_app/osm_import.py#L49-L56](../../metro_app/osm_import.py#L49)

## Overview
- **Priority:** P2
- **Status:** Todo
- **Mô tả:** 3 file đang có cùng logic Haversine. Gom thành một module `metro_app/geo.py` để DRY + test được độc lập.

## Key Insights
- 3 hàm cơ bản giống nhau (có thể khác tên: `_haversine_km`, `haversine`, etc.) — cần so sánh kỹ trước khi gom để đảm bảo không khác về đơn vị hay bán kính Trái Đất.
- Sau khi gom, Phase 03 cần import module mới.
- Module mới có thể expand sau (khoảng cách Manhattan, geodesic area, v.v.) nhưng hiện tại **chỉ 1 hàm** — YAGNI.

## Requirements

### Functional
1. Tạo `metro_app/geo.py` với 1 hàm public `haversine_km(lat1, lon1, lat2, lon2) -> float`.
2. 3 file cũ xoá hàm private, import từ geo.
3. Tất cả 14 test pass không regression.

### Non-functional
- Module `geo.py` < 30 dòng, không dependency ngoài `math`.
- Hàm có docstring 1 dòng giải thích đơn vị (km) và giả định (Earth radius = 6371 km).

## Architecture

### metro_app/geo.py (nội dung đầy đủ)
```python
"""Geographic distance utilities."""
from math import asin, cos, radians, sin, sqrt

EARTH_RADIUS_KM = 6371.0

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometers."""
    lat1_r, lat2_r = radians(lat1), radians(lat2)
    dlat = lat2_r - lat1_r
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))
```

### Imports trong 3 file cũ
```python
from metro_app.geo import haversine_km
```
(hoặc relative: `from .geo import haversine_km`)

## Related Code Files

### Create
- `metro_app/geo.py`

### Modify
- `metro_app/algorithms.py` — xoá `_haversine_km`, thay bằng import + rename call site.
- `metro_app/service.py` — tương tự.
- `metro_app/osm_import.py` — tương tự.

### Delete
- Không xoá file.

## Implementation Steps

1. Đọc 3 hàm hiện tại, verify cùng Earth radius (6371) và cùng return unit (km).
2. Tạo `metro_app/geo.py` theo nội dung ở trên.
3. Trong mỗi file cũ:
   - Xoá hàm `_haversine_km`/`haversine` cũ.
   - Thêm `from metro_app.geo import haversine_km` (nếu file ở package root) hoặc `from .geo import haversine_km`.
   - Rename call site: `_haversine_km(...)` → `haversine_km(...)`.
4. Chạy `python -m unittest discover -s tests -v` — 14 test vẫn pass.
5. Chạy `python -c "from metro_app.osm_import import fetch_overpass"` và các import test sanity.

## Todo List
- [ ] Verify 3 hàm cũ đồng bộ (Earth radius, unit).
- [ ] Tạo `metro_app/geo.py`.
- [ ] Cập nhật `algorithms.py` — import + rename.
- [ ] Cập nhật `service.py` — import + rename.
- [ ] Cập nhật `osm_import.py` — import + rename.
- [ ] `python -m unittest discover -s tests -v` pass.
- [ ] Smoke test: `python app.py` + `curl /api/routes` vẫn trả đúng distance.

## Success Criteria
- `grep -r "_haversine_km\|def haversine" metro_app/` chỉ match trong `geo.py`.
- 14 test vẫn pass.
- Distance trong API response không đổi (same formula, same radius).

## Risk Assessment
- **Risk:** 3 hàm hiện tại có thể khác nhẹ (vd. một dùng 6371.0, một dùng 6372.8). Gom làm đổi result → test expected bị lệch.
  - **Mitigation:** Đọc cả 3, nếu khác thì chọn 6371.0 (chuẩn phổ biến), rerun test, cập nhật expected nếu lệch < 0.01 km (chấp nhận được).
- **Risk:** Import circular nếu `service.py` import `algorithms.py` import `geo.py` → `geo.py` không import gì trong package nên safe.

## Security Considerations
- Không có — pure math.

## Next Steps
- Phase 03 cần phase này xong để dùng `geo.haversine_km`.
