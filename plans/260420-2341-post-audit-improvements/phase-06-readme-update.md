# Phase 06 — README Update: Reflect Phase 01-04 UI + Document Magic Constants

## Context Links
- Audit item: P1 #6
- File: [README.md](../../README.md)
- UI changes: [plans/260420-2323-frontend-ux-improvements/plan.md](../260420-2323-frontend-ux-improvements/plan.md)

## Overview
- **Priority:** P1
- **Status:** Todo
- **Mô tả:** README hiện không nói về các UI element mới (point-picker, station visibility, new-route button) và không giải thích magic number như `35 km/h`, `0.8 min dwell`.

## Key Insights
- README tiếng Việt, đối tượng là giảng viên/sinh viên → giữ tone và ngôn ngữ.
- Không rewrite toàn bộ — chỉ **update section "Cách dùng"** và **thêm section "Tham số mô hình"**.
- Section "API endpoints" nếu chưa có thì thêm ngắn gọn.

## Requirements

### Functional (content)
1. Section "Giao diện" (hoặc "Cách dùng"): mô tả:
   - 2 chế độ: Chọn ga / Click trên map.
   - Trong Click map: **nhấn nút "Điểm đi" → click map → tự thoát**; tương tự cho "Điểm đến".
   - Segmented control **"Tất cả / Chỉ chấm / Ẩn"** hiển thị trạm.
   - Nút **"Tìm tuyến mới"** reset route mà giữ blocked.
   - Esc huỷ picking; Enter không submit khi đang focus ô blocked-segment (sau Phase 01).
2. Section mới "Tham số mô hình":
   - Công thức cost edge: `max(1.0, distance_km / 35.0 × 60 + 0.8)` phút.
   - Giả định: metro Thượng Hải trung bình **35 km/h** (gồm thời gian dừng), cộng **0.8 phút** mỗi đoạn cho gia tốc/dwell.
   - Earth radius Haversine: **6371 km**.
   - Ngưỡng reject nearest-station: **50 km** (sau Phase 03).
3. Section "API endpoints" (nếu chưa có):
   - Liệt kê 4 endpoint với query params và sample response shape ngắn.
4. Section "Chạy test":
   - `python -m unittest discover -s tests -v` → kỳ vọng **≥17 test** sau Phase 02+03.

### Non-functional
- README giữ dưới 300 dòng.
- Tone Việt nhất quán.
- Không thêm ảnh (repo không có `docs/images`).

## Architecture

### Cấu trúc README sau update
```
# Tiêu đề
## Giới thiệu
## Kiến trúc (giữ nguyên)
## Cài đặt (giữ nguyên)
## Cách chạy (giữ nguyên)
## Giao diện & chế độ sử dụng       ← UPDATE
  - Chế độ "Chọn ga"
  - Chế độ "Click trên map"
  - Ẩn/hiện trạm
  - Tìm tuyến mới
  - Phím tắt
## Thuật toán (giữ nguyên)
## Tham số mô hình                    ← MỚI
## API endpoints                      ← MỚI hoặc UPDATE
## Chạy test                          ← UPDATE số test
## License
```

## Related Code Files

### Modify
- `README.md` (sections listed above).

### Reference (chỉ đọc)
- [web/index.html](../../web/index.html) — xác định text Việt trong UI để README match.
- [metro_app/algorithms.py](../../metro_app/algorithms.py), [metro_app/osm_import.py](../../metro_app/osm_import.py) — verify magic numbers.

### Create / Delete
- Không.

## Implementation Steps

1. Đọc `README.md` hiện tại hết.
2. Đọc các source file nêu trên để verify magic numbers.
3. Cập nhật sections theo mục Requirements.
4. Render preview (markdown viewer hoặc GitHub preview).
5. Verify liên kết nội bộ và code block syntax OK.

## Todo List
- [ ] Đọc README.md.
- [ ] Verify 35 km/h, 0.8 min, 50 km threshold trong code.
- [ ] Update/thêm section "Giao diện & chế độ sử dụng".
- [ ] Thêm section "Tham số mô hình".
- [ ] Thêm/update section "API endpoints".
- [ ] Update section "Chạy test".
- [ ] README < 300 dòng.

## Success Criteria
- README mô tả đúng UI sau Phase 01-04 (post-audit).
- Magic numbers giải thích rõ, nguồn gốc.
- 4 endpoint đều được document với 1 sample request.
- Số test trong README match thực tế.

## Risk Assessment
- **Risk:** Phase 02/03 chưa chạy khi làm Phase 06 → số test thực tế chưa là 17.
  - **Mitigation:** Viết "Dự kiến ≥17 sau khi hoàn tất các phase" hoặc làm Phase 06 cuối cùng.
- **Risk:** Magic number đổi trong future (vd. 35 → 32 km/h) → README lỗi thời.
  - **Mitigation:** Thêm comment trong code `algorithms.py`/`osm_import.py` nhắc update README khi đổi.

## Security Considerations
- Không có.

## Next Steps
- Sau Phase 06, plan này coi như xong. Commit `docs: update README post-audit improvements`.
