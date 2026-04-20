# Post-Audit Improvements — Metro Thượng Hải

**Ngày tạo:** 2026-04-20 23:41
**Nguồn:** [plans/reports/code-reviewer-260420-2341-full-project-audit.md](../../../../plans/reports/code-reviewer-260420-2341-full-project-audit.md)
**Scope:** Top 3 + P1/P2 khả thi, **bỏ** Compare-3-Algos UI, Share URL, CI GitHub Actions.
**Nguyên tắc:** YAGNI • KISS • DRY

## Mục tiêu
Fix các vấn đề audit chỉ ra, không thêm feature lớn. Mọi phase đều nhỏ, có test, không đụng API contract.

## Danh sách phases

| # | Phase | Priority | File ảnh hưởng | Est |
|---|-------|----------|----------------|-----|
| 01 | [Quick wins UI/UX — data-state, shortcuts, dead code](phase-01-quick-wins-ui.md) | P1 | `web/app.js`, `web/index.html`, `web/styles.css` | 30 min |
| 02 | [HTTP server integration tests](phase-02-http-server-tests.md) | P1 | `tests/test-http-server.py` (mới) | 45 min |
| 03 | [Backend correctness fixes — nearest-station bounds, greedy pure, same-station msg](phase-03-backend-correctness.md) | P1 | `metro_app/service.py`, `metro_app/algorithms.py` | 40 min |
| 04 | [DRY refactor — consolidate haversine into `metro_app/geo.py`](phase-04-haversine-geo-module.md) | P2 | 4 files | 20 min |
| 05 | [Performance — cache Leaflet polylines thay vì rebuild](phase-05-polyline-cache-perf.md) | P2 | `web/app.js` | 45 min |
| 06 | [README update — reflect Phase 01-04 UI + document magic constants](phase-06-readme-update.md) | P1 | `README.md` | 25 min |
| 07 | [Checkbox layer filter — thay segmented control bằng bảng tích hiện/ẩn trạm + từng tuyến](phase-07-checkbox-layer-filter.md) | P1 | `web/index.html`, `web/app.js`, `web/styles.css` | 40 min |
| 08 | [Fix layout bug — "Điểm đến" bị che khuất sau khi chọn "Điểm đi"](phase-08-point-picker-layout-fix.md) | **P0** | `web/app.js`, `web/styles.css` | 20 min |

**Tổng:** ~4 giờ 25 phút (thêm Phase 07+08).

## Dependencies
- Phase 04 (haversine DRY) ảnh hưởng Phase 03 (backend). **Làm Phase 04 trước Phase 03**.
- Phase 07 (checkbox filter) thay thế `state.stationVisibility` — nên làm **sau** Phase 05 (cache polyline) để tận dụng `state.edgePolylines`.
- Phase 08 (layout fix) nên làm **sau** Phase 01 (vì Phase 01 đã chạm setStatus + aria-pressed của point-picker).
- Phase 02, 06 độc lập nhau.

## Thứ tự đề xuất
```
Parallel wave 1:  Phase 01 ─┐
                  Phase 02 ─┤
                  Phase 04 ─┤
                  Phase 06 ─┘
Wave 2:           Phase 03 (cần Phase 04 xong trước)
                  Phase 08 (cần Phase 01 xong trước) — P0 UX blocker
Wave 3:           Phase 05 (performance)
Wave 4:           Phase 07 (dùng edgePolylines từ Phase 05)
```

## Success Criteria (tổng thể)
- 14 backend tests hiện có **không regression**.
- Thêm ≥5 HTTP tests mới (Phase 02).
- `data-state` hiện đúng màu loading/error/success trên status-message.
- `Esc` huỷ picking, `Enter` không submit nhầm mode.
- `metro_app/geo.py` tồn tại, 3 file cũ import từ đó (không còn duplicate).
- README có section mô tả UI mới + giải thích công thức 35 km/h.
- Toggle block-line/segment không còn rebuild toàn bộ 2000 polyline.
- **Checkbox filter panel**: uncheck tuyến/trạm → ẩn visual ngay, không ảnh hưởng pathfinding.
- **Layout fix**: 2 card Điểm đi / Điểm đến luôn visible, equal height, click được độc lập.

## Scope không làm (confirmed với user)
- ❌ Compare-3-algorithms UI toggle
- ❌ Share URL (encode state vào query string)
- ❌ CI GitHub Actions
- ❌ OAuth / database / caching layer (over-engineering)

## Rollout
Sau mỗi phase: chạy `python -m unittest discover -s tests -v` để bảo đảm không regression. Sau phase cuối: smoke test browser 4 scenario chính.
