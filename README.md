# Ứng dụng Chỉ Đường Metro Thượng Hải

Web app mô phỏng chỉ đường bằng tàu điện ngầm ở Thượng Hải, dùng dữ liệu mạng metro thật từ OpenStreetMap và ba thuật toán tìm đường cổ điển:

- `Uniform Cost Search (UCS)`
- `Greedy Best-First Search`
- `A* Search`

Phát triển cho môn **Nhập môn Trí tuệ Nhân tạo (Introduction to AI)**.

---

## Mục lục
1. [Tính năng](#tính-năng)
2. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
3. [Cách chạy](#cách-chạy)
4. [Cấu trúc thư mục](#cấu-trúc-thư-mục)
5. [Giao diện & Chế độ sử dụng](#giao-diện--chế-độ-sử-dụng)
6. [Thuật toán & So sánh](#thuật-toán--so-sánh)
7. [Tham số mô hình](#tham-số-mô-hình)
8. [Nguồn dữ liệu](#nguồn-dữ-liệu)
9. [API Endpoints](#api-endpoints)
10. [Kiến trúc](#kiến-trúc)
11. [Kiểm thử](#kiểm-thử)
12. [Phím tắt](#phím-tắt)
13. [Hạn chế đã biết](#hạn-chế-đã-biết)
14. [Hiệu năng](#hiệu-năng)
15. [Accessibility](#accessibility)
16. [Tác giả](#tác-giả)
17. [License](#license)

---

## Tính năng

- Tìm đường giữa 2 ga metro bằng cách **click chọn** từ dropdown (411 ga)
- Tìm đường từ 2 điểm bất kỳ trên bản đồ (hệ thống tự map tới ga gần nhất, tối đa 50 km)
- Hiển thị lộ trình, quãng đường, chi phí ước lượng, số node explored và các đoạn chuyển tuyến
- Highlight mạng metro trên nền bản đồ OSM thật (Leaflet)
- Cấm một hoặc nhiều **tuyến** metro trước khi chạy thuật toán
- Cấm một hoặc nhiều **đoạn** giữa 2 ga trước khi chạy thuật toán
- Popover filter: toggle hiện/ẩn **từng tuyến** và trạm trên map (chỉ visual, không ảnh hưởng pathfinding)
- Nút **"Tìm tuyến mới"** reset route mà vẫn giữ ràng buộc đã chọn
- Responsive từ desktop (1280+) → tablet → mobile (360px)

---

## Yêu cầu hệ thống

- **Python:** 3.10 trở lên (sử dụng syntax `tuple[str, str]`, union types)
- **Trình duyệt:** Modern browser hỗ trợ ES2020 + CSS custom properties (Chrome 90+, Firefox 90+, Edge 90+, Safari 15+)
- **Kết nối Internet:** chỉ cần cho bản đồ nền OSM tile (Leaflet fetch trực tiếp)
- **Dependencies:** **không cần `pip install`** — dùng stdlib Python thuần (`http.server`, `urllib`, `json`, `math`, `threading`)

---

## Cách chạy

> **Dữ liệu metro đã đóng gói sẵn** trong `data/shanghai_metro_osm.json` (206 KB, 411 ga, 20 tuyến). Clone về là chạy ngay, **không cần internet để load dữ liệu** (chỉ cần cho OSM tile nền).

```bash
git clone https://github.com/3T216/Project-for-Introduction-to-AI
cd Project-for-Introduction-to-AI
python app.py
```

Mở trình duyệt:
```
http://127.0.0.1:8000
```

### Refresh dữ liệu OSM (tuỳ chọn)

Chỉ chạy nếu muốn cập nhật mạng metro mới nhất từ Overpass API:

```bash
python -m metro_app.osm_import
```

Script sẽ:
1. Gọi Overpass API (3 mirror fallback) lấy `relation route=subway` khu vực Thượng Hải
2. Trích xuất ga và thứ tự ga trên từng tuyến
3. Tạo graph giữa các ga liền kề
4. Ước lượng chi phí cạnh theo khoảng cách địa lý
5. Ghi đè `data/shanghai_metro_osm.json`

---

## Cấu trúc thư mục

```
Project-for-Introduction-to-AI/
├── app.py                          # Entry point — gọi server.run()
├── server.py                       # HTTP server + 4 JSON API endpoints
├── README.md
├── .gitignore
│
├── metro_app/                      # Backend Python package
│   ├── __init__.py
│   ├── data.py                     # Nạp dữ liệu mạng metro (OSM hoặc sample)
│   ├── osm_import.py               # Tải + chuẩn hoá từ Overpass API
│   ├── algorithms.py               # UCS, Greedy Best-First, A*
│   ├── service.py                  # Business logic (tìm đường, filter, nearest)
│   └── geo.py                      # Haversine distance (dùng chung)
│
├── web/                            # Frontend
│   ├── index.html
│   ├── app.js                      # Logic + state + Leaflet
│   └── styles.css                  # Design tokens + responsive
│
├── data/
│   ├── shanghai_metro_osm.json     # Dữ liệu OSM đã đóng gói (206 KB)
│   └── .gitkeep
│
├── tests/                          # Unit + integration tests
│   ├── __init__.py
│   ├── test_algorithms.py          # 17 tests — backend logic
│   └── test_http_server.py         # 10 tests — HTTP endpoints
│
└── plans/                          # Plans + phase docs + design spec
    ├── 260420-2323-frontend-ux-improvements/
    └── 260420-2341-post-audit-improvements/
```

---

## Giao diện & Chế độ sử dụng

### Chế độ "Chọn ga"

- **Click vào dropdown** `Ga đi` để chọn từ danh sách 411 ga (sort alphabet)
- **Click vào dropdown** `Ga đến` tương tự
- Chọn thuật toán từ dropdown `Thuật toán`
- *(Tuỳ chọn)* Tick **Tuyến bị cấm** để loại tuyến khỏi pathfinding
- *(Tuỳ chọn)* Chọn 2 ga trong phần **Đoạn bị cấm** → bấm "Thêm đoạn" để cấm đoạn
- Bấm `Tìm đường`

> Mẹo: Khi dropdown mở, gõ chữ cái đầu (typeahead) để nhảy nhanh đến ga.

### Chế độ "Click trên map"

- Bấm nút `Điểm đi` → cursor đổi thành crosshair → click vị trí trên map → tự động thoát mode
- Tương tự với `Điểm đến`
- Hệ thống tự tìm ga gần nhất cho mỗi điểm (ngưỡng tối đa **50 km**; ngoài khoảng đó sẽ báo lỗi)
- Bấm lại nút cùng mode để huỷ, hoặc nhấn `Esc`
- Bấm `Tìm đường từ điểm đã chọn` (nút này chỉ enabled khi đã chọn đủ 2 điểm)

### Bộ lọc hiển thị map (popover)

Bấm nút `⚙ Hiển thị` ở góc trên-phải của map để mở popover:
- Checkbox **Trạm** — toggle hiện/ẩn toàn bộ marker ga
- Checkbox **Tất cả tuyến** (master) — bật/tắt hàng loạt
- Checkbox **từng tuyến** (20 checkbox, mỗi dòng có chấm màu) — toggle riêng

> Bộ lọc này **chỉ ảnh hưởng visual**. Không làm đổi kết quả pathfinding — để đổi kết quả hãy dùng panel "Tuyến bị cấm".

### Nút "Tìm tuyến mới"

- **Reset:** route highlight, điểm đi/đến đã pick, kết quả hiển thị, zoom map về toàn mạng
- **Giữ nguyên:** tuyến/đoạn bị cấm, thuật toán đã chọn, bộ lọc hiển thị

---

## Thuật toán & So sánh

| Tiêu chí | UCS | Greedy Best-First | A* |
|----------|:---:|:-----------------:|:--:|
| Hoàn chỉnh (Complete) | ✅ | ✅* | ✅ |
| Tối ưu (Optimal) | ✅ | ❌ | ✅** |
| Dùng heuristic | ❌ | ✅ | ✅ |
| Time complexity (worst) | O(b^(C*/ε)) | O(b^m) | O(b^(C*/ε)) |
| Space complexity | O(b^(C*/ε)) | O(b^m) | O(b^(C*/ε)) |
| Số node explored (ví dụ Hongqiao→Century) | 170 | 15 ⚡ | 64 |
| Use case | Baseline, đảm bảo tối ưu | Nhanh, chấp nhận không tối ưu | Cân bằng tốc độ + tối ưu |

*Greedy hoàn chỉnh với đồ thị hữu hạn và tracking `visited`.
**A\* tối ưu khi heuristic **admissible** (không overestimate). Project này dùng Haversine / 35 km/h, luôn nhỏ hơn chi phí thực → admissible.

Chi tiết cài đặt: [metro_app/algorithms.py](metro_app/algorithms.py)

---

## Tham số mô hình

### Công thức chi phí cạnh

```
cost = max(1.0, (distance_km / 35.0) × 60 + 0.8)   [phút]
```

| Thành phần | Giải thích |
|------------|------------|
| `distance_km` | Haversine giữa 2 ga |
| `35.0` | Tốc độ trung bình metro Thượng Hải 35 km/h (gồm dừng tại ga) |
| `× 60` | Giờ → phút |
| `+ 0.8` | Phụ phí 0.8 phút/đoạn (gia tốc, dừng, dwell) |
| `max(1.0, …)` | Chi phí tối thiểu 1 phút |

### Heuristic (A\* và Greedy)

```
h(n) = haversine(n, goal) / 35.0 × 60   [phút]
```

Admissible → A\* luôn tối ưu.

### Hằng số địa lý

- **Earth radius (Haversine):** `6371 km`
- **Ngưỡng reject nearest-station:** `50 km` (điểm ngoài vùng Thượng Hải bị từ chối)

---

## Nguồn dữ liệu

Ưu tiên dữ liệu thật từ OpenStreetMap qua Overpass API.

- Script import: [metro_app/osm_import.py](metro_app/osm_import.py)
- File đã chuẩn hoá (đi kèm repo): `data/shanghai_metro_osm.json`
- Nếu file chưa tồn tại → fallback sample dataset nhỏ (23 ga, 5 tuyến) để chạy được

### Lưu ý về trọng số

OSM cung cấp tốt: **tên ga**, **tên tuyến**, **topology**, **thứ tự ga trên tuyến**. Nhưng **không có** thời gian chạy chi tiết từng đoạn → chi phí phải ước lượng bằng công thức ở trên.

---

## API Endpoints

Server expose 4 JSON endpoints:

### `GET /`
HTML web UI (`web/index.html`).

### `GET /api/network`
Metadata mạng.
```json
{
  "data_source": "osm_overpass_shanghai",
  "stations": [{"name": "...", "lat": 31.xx, "lon": 121.xx}, ...],
  "edges":    [{"source": "...", "target": "...", "line": "...", "distance_km": 2.1, "travel_time": 4.5}, ...],
  "lines":    ["1", "2", "3", ...],
  "algorithms": ["ucs", "greedy", "astar"]
}
```

### `GET /api/routes`
Tham số: `start`, `goal`, `algorithm?`, `blocked_lines?` (multiple), `blocked_segments?` (multiple, format `GaA|||GaB`).
```bash
curl "http://127.0.0.1:8000/api/routes?start=Hongqiao%20Railway%20Station&goal=Century%20Avenue&algorithm=astar"
```

### `GET /api/nearest-station`
Tham số: `lat`, `lon`. Trả lỗi 400 nếu điểm cách ga gần nhất > 50 km.
```bash
curl "http://127.0.0.1:8000/api/nearest-station?lat=31.2304&lon=121.4737"
```

### `GET /api/routes-by-points`
Tham số: `start_lat`, `start_lon`, `goal_lat`, `goal_lon`, + optionals như `/api/routes`. Response có thêm field `point_selection` map điểm → ga gần nhất.

---

## Kiến trúc

```
┌────────────────────────┐     HTTP/JSON      ┌──────────────────────┐
│ Browser (Leaflet UI)   │ ◄─────────────────► │ Python HTTP Server   │
│ web/index.html         │                     │ server.py            │
│ web/app.js             │                     │ (ThreadingHTTP)      │
│ web/styles.css         │                     └─────────┬────────────┘
└────────────────────────┘                               │
                                                         ▼
                                             ┌──────────────────────┐
                                             │ metro_app.service    │
                                             │ ┌──────────────────┐ │
                                             │ │ find_routes      │ │
                                             │ │ find_nearest_sta │ │
                                             │ │ build_filter_grp │ │
                                             │ └────────┬─────────┘ │
                                             └──────────┼───────────┘
                                              ┌─────────┴─────────┐
                                              ▼                   ▼
                                   ┌────────────────┐    ┌────────────────┐
                                   │ algorithms.py  │    │ data.py        │
                                   │ UCS            │    │ Station/Edge   │
                                   │ Greedy BFS     │    │ load_network() │
                                   │ A*             │    └────────┬───────┘
                                   └────────┬───────┘             │
                                            ▼                     ▼
                                   ┌────────────────┐    ┌────────────────┐
                                   │ geo.py         │    │ data/*.json    │
                                   │ haversine_km   │    │ (hoặc sample)  │
                                   └────────────────┘    └────────────────┘
```

**Data flow:** Browser → HTTP Server → Service → (Algorithms + Data + Geo) → JSON response → Leaflet render.

---

## Kiểm thử

```bash
python -m unittest discover -s tests -v
```

**Tổng:** 27 tests (~0.6s), gồm:
- **17 tests backend** ([tests/test_algorithms.py](tests/test_algorithms.py)): thuật toán, filter tuyến/đoạn, geo bounds, same-station, pure greedy
- **10 tests HTTP** ([tests/test_http_server.py](tests/test_http_server.py)): 4 endpoint × (happy path + malformed input)

---

## Phím tắt

| Phím | Hành động | Điều kiện |
|------|-----------|-----------|
| `Esc` | Đóng popover filter | Popover đang mở |
| `Esc` | Huỷ chế độ pick điểm map | Đang pick Điểm đi/Điểm đến |
| Chữ cái | Typeahead trong dropdown `<select>` | Dropdown mở |
| `Enter` | Submit form | Focus trong ô form chính |
| Click ngoài popover | Đóng popover | Popover đang mở |

---

## Hạn chế đã biết

1. **Dữ liệu OSM có typo:** `"National Exhibiation and Convention Center"` (đúng phải là *Exhibition*). Không phải bug của code, là data quality của OSM.
2. **Một số ga tên chỉ là số:** `"1"`, `"2"` — do OSM relation thiếu tag `name` → script import lấy `ref` thay thế. Ảnh hưởng UX dropdown (hai item đầu không nhận ra được).
3. **Chi phí ước lượng, không chính xác 100%:** vì OSM không có thời gian chạy thực tế, mọi edge cost đều từ công thức `35 km/h + 0.8 phút/đoạn`. Kết quả "tối ưu" là tối ưu **với mô hình này**, không nhất thiết là tối ưu thực tế.
4. **Nearest station chỉ làm gần đúng:** dùng Haversine thẳng, không tính địa hình/đường bộ từ điểm user click đến ga.
5. **Không có persist state:** F5 mất hết blocked lines/segments/picked points.

---

## Hiệu năng

- **Dataset:** 411 ga, ~1000 cạnh (lưu bidirectional → ~2000 polyline Leaflet)
- **Test suite:** 27 tests chạy trong ~0.6s
- **API response:** `/api/routes` ~5-20ms cho query điển hình
- **Frontend optimization:**
  - Polyline cache (Phase 05): toggle blocked-line gọi `setStyle()` thay vì clear + rebuild 2000 object → tiết kiệm ~10× thời gian
  - `state.stationMarkers` cache: ẩn/hiện trạm chỉ toggle tooltip, không re-create marker

---

## Accessibility

- `aria-pressed` trên nút mode-toggle, point-picker, visibility
- `aria-expanded` + `aria-controls` trên popover filter
- `role="dialog"` + `aria-label` cho filter dropdown
- `focus-visible` ring với màu tương phản AA (`--shadow-focus`)
- `prefers-reduced-motion` → transition → 0.01ms
- Contrast AA cho body text (`#14181c` trên `#ffffff` ~ 17:1)
- Button `min-height: 40px` (primary 44px) đáp ứng touch-target

---

## Tác giả

- **Tên sinh viên:** *(điền tên tại đây)*
- **Mã sinh viên:** *(điền MSSV tại đây)*
- **Lớp / Khoá:** *(điền tại đây)*
- **Môn học:** Nhập môn Trí tuệ Nhân tạo
- **Giảng viên:** *(điền tên GV)*
- **Email:** 

Đồng đội (nếu project nhóm): *(điền)*

---

## License

Dùng cho mục đích học tập & nghiên cứu (non-commercial). Dữ liệu bản đồ © OpenStreetMap contributors, ODbL.

Nếu muốn mở source chính thức, khuyến nghị `MIT License` hoặc `CC-BY-4.0`.
