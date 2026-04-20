# Phase 02 — HTTP Server Integration Tests

## Context Links
- Audit: `plans/reports/code-reviewer-260420-2341-full-project-audit.md` (P1 item #5)
- Server: [server.py](../../server.py) — 4 endpoints, ~243 lines
- Existing tests: [tests/test_algorithms.py](../../tests/test_algorithms.py) — 14 unit tests, chưa có HTTP test

## Overview
- **Priority:** P1
- **Status:** Todo
- **Mô tả:** Thêm tests cho 4 endpoint: `/api/network`, `/api/routes`, `/api/nearest-station`, `/api/routes-by-points`. Test cả happy path lẫn malformed input (missing param, non-float, unknown algorithm, unknown station).

## Key Insights
- `server.py` expose hàm `run(host, port)` (line ~240). Cần cách spin server trên **ephemeral port** để test parallel không conflict.
- Dùng `ThreadingHTTPServer` từ `server.py` nhưng **không gọi `run()`** — tạo server instance thủ công, serve trong thread, shutdown sau test.
- Hoặc đơn giản hơn: dùng `urllib.request` sau khi start thread, nhưng cần fixture reliable.
- Pattern chuẩn:
  ```python
  server = ThreadingHTTPServer(("127.0.0.1", 0), MetroRequestHandler)
  port = server.server_address[1]  # ephemeral
  thread = threading.Thread(target=server.serve_forever, daemon=True)
  thread.start()
  # ... test ...
  server.shutdown()
  ```

## Requirements

### Functional test cases (tối thiểu 8)
1. `GET /api/network` → 200, JSON có `stations`, `edges`, `lines`, `algorithms`.
2. `GET /api/routes?start=X&goal=Y` (valid) → 200, `results[0].path` chứa start và goal.
3. `GET /api/routes` missing `start` → 400 JSON `error`.
4. `GET /api/routes?start=UNKNOWN&goal=Century Avenue` → 400/404 error message rõ.
5. `GET /api/routes?...&algorithm=invalid` → 400 error.
6. `GET /api/nearest-station?lat=31.23&lon=121.47` → 200, `station.distance_km` ≥ 0.
7. `GET /api/nearest-station?lat=abc&lon=def` → 400 error (non-float).
8. `GET /api/routes-by-points?start_lat=...&start_lon=...&goal_lat=...&goal_lon=...` → 200.
9. `GET /api/unknown-endpoint` → 404.
10. `GET /` → 200, trả HTML (không phải JSON).

### Non-functional
- Test chạy < 2 giây tổng.
- Không hardcode port (dùng ephemeral).
- Không phụ thuộc network ngoài (không gọi Overpass).

## Architecture

### File mới
- `tests/test-http-server.py` — class `HTTPEndpointsTests(unittest.TestCase)` với `setUpClass/tearDownClass` khởi động/tắt server một lần.

### Helpers
```python
import json, threading, urllib.request, urllib.error
from http.server import ThreadingHTTPServer
from server import MetroRequestHandler

@classmethod
def setUpClass(cls):
    cls.server = ThreadingHTTPServer(("127.0.0.1", 0), MetroRequestHandler)
    cls.port = cls.server.server_address[1]
    cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
    cls.thread.start()

@classmethod
def tearDownClass(cls):
    cls.server.shutdown()

def _get(self, path):
    url = f"http://127.0.0.1:{self.port}{path}"
    try:
        with urllib.request.urlopen(url) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
```

## Related Code Files

### Modify
- Không đụng `server.py`. Nếu `MetroRequestHandler` class name khác, grep để confirm:
  ```
  Grep: "class.*BaseHTTPRequestHandler" in server.py
  ```

### Create
- `tests/test-http-server.py` (~100 dòng)

### Delete
- Không.

## Implementation Steps

1. Grep `server.py` để xác định handler class name và confirm `run()` signature.
2. Tạo `tests/test-http-server.py` với setUpClass/tearDownClass.
3. Viết 10 test case ở trên.
4. Chạy `python -m unittest discover -s tests -v`:
   - Expect: 14 test cũ + 10 test mới = 24 pass.
5. Nếu test flaky vì port conflict: dùng `socket.SO_REUSEADDR`.

## Todo List
- [ ] Grep `server.py` tìm tên handler class.
- [ ] Tạo skeleton `test-http-server.py` với fixture.
- [ ] Viết 10 test case.
- [ ] Chạy full test suite, fix flaky nếu có.
- [ ] Xác nhận time total < 2s.

## Success Criteria
- `python -m unittest discover -s tests -v` báo ≥24 tests, tất cả pass.
- Test chạy trong dưới 2 giây.
- Không cần khởi động `python app.py` thủ công.

## Risk Assessment
- **Risk:** Handler class có state toàn cục (vd. dataset cache) không chia sẻ tốt với ephemeral server.
  - **Mitigation:** Kiểm tra `server.py` có import lazy dataset không. Nếu có global, test cần load trước.
- **Risk:** Thread server không shutdown sạch → port leak giữa test class.
  - **Mitigation:** `daemon=True` + `server.shutdown()` trong `tearDownClass`; dùng ephemeral port tránh collision.
- **Risk:** `unittest discover` yêu cầu file pattern mặc định `test*.py`. File `test-http-server.py` (kebab-case) không match.
  - **Mitigation:** Đặt pattern `discover -p 'test*.py'` — kebab-case hoạt động với `discover`. Nhưng để an toàn, dùng **snake_case** `test_http_server.py` theo convention Python/unittest (override kebab rule cho file test).

**LƯU Ý:** Python unittest discover default pattern là `test*.py` → file `test-http-server.py` vẫn match. Nhưng `unittest.TestLoader` cần `importlib` load được module — kebab-case trong Python module không import được bằng `import test-http-server`. **Dùng snake_case: `tests/test_http_server.py`**.

## Security Considerations
- Test chạy trên `127.0.0.1`, không expose ra ngoài.
- Không test với payload độc hại thật (XSS, SQLi) vì app không có DB/template engine.

## Next Steps
- Sau Phase 02: có thể thêm test cho Phase 03 changes (nearest-station bounds check, same-station error).
