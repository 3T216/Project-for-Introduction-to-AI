# Ứng dụng Chỉ Đường Metro Thượng Hải

Đây là web app mô phỏng chỉ đường bằng tàu điện ở Thượng Hải, sử dụng dữ liệu mạng metro từ OpenStreetMap và các thuật toán tìm đường:

- `Uniform Cost Search (UCS)`
- `Greedy Best-First Search`
- `A* Search`

Ứng dụng hiện có:

- Backend bằng `Python`
- Frontend bằng `HTML/CSS/JavaScript`
- Bản đồ nền OSM thật, giới hạn quanh khu vực Thượng Hải
- Chọn ga bằng cách nhập tên
- Chọn điểm bất kỳ trên bản đồ, hệ thống tự tìm ga gần nhất
- Cấm theo tuyến metro
- Cấm theo đoạn giữa 2 ga
- Chọn một thuật toán cụ thể để chạy

## Tính năng

- Tìm đường giữa 2 ga metro
- Tìm đường từ 2 điểm bất kỳ trên bản đồ
- Tự ánh xạ điểm đi và điểm đến sang ga gần nhất
- Hiển thị lộ trình, quãng đường, chi phí ước lượng và các đoạn chuyển tuyến
- Làm nổi bật mạng metro trên nền bản đồ
- Loại bỏ một hoặc nhiều tuyến khỏi graph trước khi chạy thuật toán
- Loại bỏ một hoặc nhiều đoạn trực tiếp giữa hai ga trước khi chạy thuật toán

## Cấu trúc thư mục

- `app.py`: điểm khởi động ứng dụng
- `server.py`: HTTP server và API
- `metro_app/data.py`: nạp dữ liệu mạng metro
- `metro_app/osm_import.py`: tải và chuẩn hóa dữ liệu từ Overpass / OpenStreetMap
- `metro_app/algorithms.py`: cài đặt `UCS`, `Greedy Best-First Search`, `A*`
- `metro_app/service.py`: xử lý nghiệp vụ tìm đường, lọc tuyến bị cấm, lọc đoạn bị cấm, tìm ga gần nhất
- `web/index.html`: giao diện web
- `web/app.js`: logic frontend
- `web/styles.css`: style giao diện
- `tests/test_algorithms.py`: kiểm thử backend

## Nguồn dữ liệu

Project ưu tiên dùng dữ liệu thật từ OpenStreetMap thông qua Overpass API.

- Script import dữ liệu: [metro_app/osm_import.py](metro_app/osm_import.py)
- File dữ liệu đã chuẩn hóa: `data/shanghai_metro_osm.json`

Nếu file dữ liệu chưa tồn tại, hệ thống sẽ fallback sang bộ dữ liệu mẫu nhỏ để vẫn có thể chạy được.

## Cách tải dữ liệu OSM

```bash
python -m metro_app.osm_import
```

Script sẽ:

1. Gọi Overpass API để lấy các `relation` có `route=subway` trong khu vực Thượng Hải.
2. Trích xuất danh sách ga và thứ tự ga trên từng tuyến.
3. Tạo graph giữa các ga liền kề.
4. Ước lượng trọng số cạnh dựa trên khoảng cách địa lý giữa 2 ga.

## Tham số mô hình

### Công thức chi phí đoạn (Cost function)

Mỗi cạnh (edge) giữa 2 ga liền kề được gán chi phí bằng công thức sau:

```
cost = max(1.0, (distance_km / 35.0) × 60 + 0.8)
```

**Giải thích:**
- `distance_km`: khoảng cách địa lý giữa 2 ga (tính bằng Haversine trên hình cầu)
- `35.0`: giả định tốc độ trung bình của metro Thượng Hải là **35 km/h** (gồm cả thời gian dừng tại ga)
- `× 60`: chuyển từ giờ sang phút
- `+ 0.8`: phụ phí **0.8 phút** mỗi đoạn để tính gia tốc ban đầu, dừng, và dwell time tại ga
- `max(1.0, ...)`: chi phí tối thiểu là 1 phút (ngay cả đoạn rất ngắn)

### Heuristic cho A* và Greedy Best-First Search

Cho các thuật toán sử dụng heuristic (A* và Greedy), hàm heuristic được tính:

```
heuristic = haversine(current_station, goal_station) / 35.0 × 60
```

- Heuristic này ước lượng chi phí tối thiểu từ node hiện tại đến goal theo chiều gió (không qua các ga).
- Admissible (luôn nhỏ hơn chi phí thực) nên đảm bảo A* tìm được đường tối ưu.

### Hằng số địa lý

- **Earth radius (Haversine):** `6371 km` — bán kính trung bình của Trái Đất
- **Ngưỡng reject nearest-station:** `50 km` — điểm ngoài vùng này (khi picking trên map) sẽ bị từ chối hoặc cảnh báo (sau Phase 03)

## Lưu ý về trọng số

OpenStreetMap cung cấp tốt:

- tên ga
- tên tuyến
- cấu trúc mạng
- thứ tự ga trên tuyến

Nhưng thường không có thời gian chạy chi tiết cho từng đoạn.

Vì vậy trong project này:

- topology của mạng là dữ liệu thật từ OSM
- chi phí cạnh được ước lượng từ khoảng cách địa lý giữa 2 ga theo công thức ở trên

## Cách chạy

Chạy trong thư mục project:

```bash
python app.py
```

Sau đó mở trình duyệt:

```text
http://127.0.0.1:8000
```

## Giao diện & Chế độ sử dụng

### Chế độ "Chọn ga"

- Nhập tên `Ga đi` vào ô tìm kiếm với gợi ý từ datalist
- Nhập tên `Ga đến` vào ô tìm kiếm với gợi ý từ datalist
- Chọn thuật toán từ dropdown
- (Tùy chọn) Cấm một hoặc nhiều `Tuyến bị cấm` bằng cách chọn trong danh sách
- (Tùy chọn) Cấm một hoặc nhiều `Đoạn bị cấm giữa 2 ga` bằng cách chọn ga đầu và ga cuối
- Bấm `Tìm đường` để thực thi thuật toán

### Chế độ "Click trên map"

- Bấm nút `Điểm đi` → nhấn vào một vị trí trên bản đồ để đặt điểm khởi hành → điểm sẽ tự thoát chế độ picking
- Tương tự, bấm nút `Điểm đến` → nhấn vào một vị trí trên bản đồ để đặt điểm đích → tự thoát
- Hệ thống sẽ tự tìm ga gần nhất cho mỗi điểm (với ngưỡng tối đa 50 km)
- Chọn thuật toán từ dropdown
- (Tùy chọn) Cấm tuyến hoặc đoạn nếu cần
- Bấm `Tìm đường từ điểm đã chọn` để thực thi
- **Phím tắt:** Nhấn `Esc` để hủy chế độ picking điểm (trong lúc chọn)

### Hiển thị / Ẩn trạm trên bản đồ

- Sử dụng segmented control **"Tất cả / Chỉ chấm / Ẩn"** ở phía trên bản đồ:
  - **"Tất cả":** Hiển thị đầy đủ tên ga và ký hiệu chấm
  - **"Chỉ chấm":** Chỉ hiển thị ký hiệu chấm mà không có tên ga (giảm mù mắt)
  - **"Ẩn":** Ẩn hoàn toàn các trạm, chỉ hiển thị đường tuyến
  - *Lưu ý:* Phiên bản tiếp theo có thể thay thế segmented control bằng checkbox filter panel

### Nút "Tìm tuyến mới"

- Bấm `Tìm tuyến mới` để đặt lại route đang hiển thị
- **Giữ nguyên:** Các tuyến/đoạn bị cấm, thuật toán đã chọn, điểm đi/đến
- **Reset:** Kết quả đã tìm và biểu diễn trên bản đồ

## API Endpoints

Server cung cấp 4 endpoint chính để truy vấn dữ liệu mạng và tìm đường:

### `GET /`

Trả về HTML web UI (file `web/index.html`).

### `GET /api/network`

Metadata của mạng lưới metro.

**Tham số query:** Không có

**Response shape:**
```json
{
  "data_source": "osm_overpass_shanghai",
  "stations": [
    {"name": "...", "lat": 31.xxx, "lon": 121.xxx},
    ...
  ],
  "edges": [
    {"source": "...", "target": "...", "line": "...", "distance_km": 2.1, "travel_time": 4.5},
    ...
  ],
  "lines": ["1", "2", "3", ...],
  "algorithms": ["ucs", "greedy", "astar"]
}
```

### `GET /api/routes`

Tìm đường giữa 2 ga theo tên.

**Tham số query:**
- `start` (string, required): tên ga khởi hành
- `goal` (string, required): tên ga đích
- `algorithm` (string, optional): `ucs`, `greedy`, hoặc `astar` (nếu không chỉ định, trả về cả 3)
- `blocked_lines` (string, multiple): cấm tuyến (có thể truyền nhiều lần hoặc phân cách bằng `,`)
- `blocked_segments` (string, multiple): cấm đoạn theo định dạng `GaA|||GaB` (có thể truyền nhiều lần)

**Ví dụ:**
```bash
curl "http://127.0.0.1:8000/api/routes?start=Hongqiao%20Railway%20Station&goal=Century%20Avenue&algorithm=astar"
```

**Response shape:**
```json
{
  "start": "Hongqiao Railway Station",
  "goal": "Century Avenue",
  "blocked_lines": [],
  "blocked_segments": [],
  "algorithm": "astar",
  "results": [
    {
      "algorithm": "A*",
      "path": ["Station A", "Station B", ...],
      "total_cost": 25.5,
      "explored_nodes": 42,
      "line_sequence": ["Line 2", "Line 2", ...],
      "total_distance_km": 10.2,
      "segments": ["Line 2: Station A -> Station C", ...]
    }
  ]
}
```

### `GET /api/nearest-station`

Tìm ga gần nhất tới một điểm địa lý.

**Tham số query:**
- `lat` (float, required): vĩ độ
- `lon` (float, required): kinh độ

**Ví dụ:**
```bash
curl "http://127.0.0.1:8000/api/nearest-station?lat=31.2304&lon=121.4737"
```

**Response shape:**
```json
{
  "query_point": {"lat": 31.2304, "lon": 121.4737},
  "station": {
    "name": "Century Avenue",
    "lat": 31.2303,
    "lon": 121.5190,
    "distance_km": 3.2
  }
}
```

### `GET /api/routes-by-points`

Tìm đường giữa 2 điểm địa lý (hệ thống tự tìm ga gần nhất).

**Tham số query:**
- `start_lat`, `start_lon` (float, required): tọa độ điểm khởi hành
- `goal_lat`, `goal_lon` (float, required): tọa độ điểm đích
- `algorithm` (string, optional): như `/api/routes`
- `blocked_lines`, `blocked_segments` (string, multiple): như `/api/routes`

**Ví dụ:**
```bash
curl "http://127.0.0.1:8000/api/routes-by-points?start_lat=31.1949&start_lon=121.3270&goal_lat=31.2303&goal_lon=121.5190&algorithm=astar"
```

**Response shape:**
```json
{
  "start": "...",
  "goal": "...",
  "results": [...],
  "point_selection": {
    "start_point": {"lat": 31.1949, "lon": 121.3270},
    "goal_point": {"lat": 31.2303, "lon": 121.5190},
    "start_station": {"name": "...", "lat": 31.xxx, "lon": 121.xxx, "distance_km": 0.5},
    "goal_station": {"name": "...", "lat": 31.xxx, "lon": 121.xxx, "distance_km": 0.3}
  }
}
```

## Kiểm thử

Chạy toàn bộ test suite:

```bash
python -m unittest discover -s tests -v
```

**Hiện tại:** 24 tests bao gồm:
- **14 tests backend** (test_algorithms.py): thuật toán, tìm đường, filter tuyến/đoạn
- **10 tests HTTP server** (test_http_server.py): endpoint `/`, `/api/network`, `/api/routes`, `/api/nearest-station`, `/api/routes-by-points`

**Kỳ vọng:** Số tests sẽ tăng khi các phase cải tiến (Phase 02-04) hoàn tất (dự kiến ≥24+ tests).
