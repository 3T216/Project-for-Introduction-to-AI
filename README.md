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

## Lưu ý về trọng số

OpenStreetMap cung cấp tốt:

- tên ga
- tên tuyến
- cấu trúc mạng
- thứ tự ga trên tuyến

Nhưng thường không có thời gian chạy chi tiết cho từng đoạn.

Vì vậy trong project này:

- topology của mạng là dữ liệu thật từ OSM
- chi phí cạnh được ước lượng từ khoảng cách địa lý giữa 2 ga

## Cách chạy

Chạy trong thư mục project:

```bash
python app.py
```

Sau đó mở trình duyệt:

```text
http://127.0.0.1:8000
```

## Cách sử dụng

### 1. Chế độ chọn ga

- Nhập tên `Ga đi`
- Nhập tên `Ga đến`
- Chọn thuật toán
- Nếu muốn, chọn thêm các `Tuyến bị cấm`
- Nếu muốn, thêm các `Đoạn bị cấm giữa 2 ga`
- Bấm `Tìm đường`

### 2. Chế độ chọn trên bản đồ

- Chuyển sang chế độ `Click trên map`
- Click lần 1 để đặt điểm bắt đầu
- Click lần 2 để đặt điểm đích
- Hệ thống sẽ tự tìm ga gần nhất cho mỗi điểm
- Chọn thuật toán
- Nếu muốn, thêm tuyến hoặc đoạn bị cấm
- Bấm `Tìm đường từ điểm đã chọn`

## API chính

### `GET /api/network`

Trả về:

- danh sách ga
- danh sách cạnh
- danh sách tuyến
- danh sách thuật toán có sẵn
- nguồn dữ liệu hiện tại

### `GET /api/routes`

Ví dụ:

```text
/api/routes?start=Hongqiao Railway Station&goal=Century Avenue&algorithm=astar&blocked_lines=2&blocked_segments=East%20Nanjing%20Road%7C%7C%7CLujiazui
```

Tham số:

- `start`: tên ga bắt đầu
- `goal`: tên ga đích
- `algorithm`: `ucs`, `greedy`, hoặc `astar`
- `blocked_lines`: có thể truyền nhiều lần để cấm nhiều tuyến
- `blocked_segments`: có thể truyền nhiều lần theo định dạng `GaA|||GaB`

### `GET /api/nearest-station`

Ví dụ:

```text
/api/nearest-station?lat=31.1949&lon=121.3270
```

Dùng để tìm ga gần nhất với một điểm trên bản đồ.

### `GET /api/routes-by-points`

Ví dụ:

```text
/api/routes-by-points?start_lat=31.1949&start_lon=121.3270&goal_lat=31.2303&goal_lon=121.5190&algorithm=ucs&blocked_lines=2&blocked_segments=East%20Nanjing%20Road%7C%7C%7CLujiazui
```

Dùng khi chọn điểm trực tiếp trên bản đồ thay vì chọn tên ga.

## Kiểm thử

Chạy test:

```bash
python -m unittest discover -s tests -v
```
