# Frontend UX Improvements — Metro Thượng Hải

**Ngày tạo:** 2026-04-20 23:23
**Phạm vi:** Chỉ frontend (`web/index.html`, `web/app.js`, `web/styles.css`). Không chạm backend.
**Nguyên tắc:** YAGNI • KISS • DRY

## Mục tiêu
Cải tiến UX/UI dựa trên 4 yêu cầu người dùng:
1. Chế độ click map hiện tại auto-alternate start/goal → gây nhầm lẫn.
2. Map quá rối với 411 trạm, cần ẩn/hiện nhãn hoặc toàn bộ trạm phụ.
3. Tuyến cũ không tự xoá khi tìm tuyến mới.
4. UI nhìn cũ, spacing và typography chưa tốt.

## Danh sách phases

| # | Phase | Trạng thái | Độ ưu tiên |
|---|-------|------------|------------|
| 01 | [Refactor click-mode: 2 nút Set Start / Set Goal](phase-01-map-click-mode-refactor.md) | Todo | P0 |
| 02 | [Nút ẩn/hiện trạm (stations visibility toggle)](phase-02-station-visibility-filter.md) | Todo | P1 |
| 03 | [Nút "Tìm tuyến mới" reset route cũ](phase-03-new-route-reset.md) | Todo | P0 |
| 04 | [UI/UX Redesign (skill `ui-ux-designer`)](phase-04-ui-ux-redesign.md) | Todo | P1 |

## Dependencies
- Phase 01 → Phase 04: Phase 04 sẽ restyle các nút mới từ Phase 01/02/03, nên 04 chạy sau cùng.
- Phase 02, 03 độc lập, có thể làm song song với 01.
- Không đụng backend (`metro_app/`, `server.py`) → không rủi ro breaking API.

## Key Files
- `web/index.html` — thêm nút Set Start, Set Goal, Hide Stations, Find New Route.
- `web/app.js` — state machine mới: `pointSelection: "start" | "goal" | null`; hàm `clearRoute()`; layer `stationLabelLayer` toggle.
- `web/styles.css` — redesign tokens, grid, buttons, responsive.

## Success Criteria (tổng thể)
- Người dùng chọn start/goal chủ động bằng nút, không còn auto-alternate.
- Có checkbox/nút ẩn được các trạm phụ/nhãn.
- Nút "Tìm tuyến mới" xoá sạch route + selection trước đó.
- UI nhìn hiện đại: spacing nhất quán, typography rõ, responsive < 1024px.
- Tất cả 12 test backend trong `tests/test_algorithms.py` vẫn pass (không bị ảnh hưởng).
- Smoke test thủ công 4 scenario: station-mode, map-mode, blocked-lines, new-route.

## Rollout
Sau khi 4 phase xong → chạy `python app.py` → kiểm thử thủ công trên browser → commit theo conventional commits (`feat(web):`, `style(web):`).
