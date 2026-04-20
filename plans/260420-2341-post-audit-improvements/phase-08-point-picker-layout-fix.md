# Phase 08 — Sửa Layout Bug: "Điểm Đến" Bị Che Khuất Sau Khi Chọn "Điểm Đi"

## Context Links
- Screenshot user báo: chỉ thấy card "Điểm đi" với summary dài, thiếu card "Điểm đến".
- HTML hiện tại: [web/index.html#L88-L109](../../web/index.html#L88) — `.point-picker-row` với 2 button.
- CSS: [web/styles.css](../../web/styles.css) — `.point-picker-row { grid-template-columns: 1fr 1fr }`; mobile `@media (max-width: 767px)` stack 1 col.

## Overview
- **Priority:** P0 (UX blocker)
- **Status:** Todo
- **Mô tả:** Sau khi user chọn "Điểm đi" thành công, summary text dài (`"Lat 31.09681, Lon 121.08881. Ga gần nhất: Zhujiajiao (4.32 km)"`) làm card "Điểm đi" phình to → card "Điểm đến" bị đẩy xuống dưới/cạnh khó thấy, có thể overflow hoặc trùng với element khác, khiến user không click được.

## Key Insights
- Summary dài = 2-3 dòng text. CSS có `-webkit-line-clamp: 2` nhưng Safari-prefixed → Firefox có thể không clamp.
- Grid `1fr 1fr` khi content 2 cell khác height sẽ stretch theo cell cao nhất. Nếu 1 cell có 2 dòng summary và 1 cell có "Chưa có điểm đến" 1 dòng, grid vẫn 2 cột equal-height → OK.
- Nhưng ở **tablet/narrow** (`@media max-width: 767px`), stack 1 col → Điểm đến xuống dưới Điểm đi → cách submit button 1 step scroll → dễ tưởng "biến mất".
- User expectation: **luôn thấy cả 2 card, độc lập nhau**, không phải scroll/search.

## Requirements

### Functional
1. Sau khi chọn Điểm đi, card Điểm đến **luôn visible** và **có thể click ngay**.
2. Summary text dài bị clamp 1 dòng với ellipsis, không làm card phình height.
3. Card giữ height cố định hoặc min-height đủ lớn để 2 card cùng cao đều nhau.
4. Ở mobile (< 768px), 2 card vẫn stack nhưng mỗi card height cố định → Điểm đến dưới Điểm đi nhưng gần ngay — không cần scroll lớn.
5. Nút submit "Tìm đường từ điểm đã chọn" **chỉ enable** khi cả 2 điểm đã chọn; disabled nếu thiếu → visual cue user biết cần chọn đủ.

### Non-functional
- Không vỡ existing Phase 01 active state (ring orange).
- Không tăng overflow.

## Architecture

### Giải pháp 1 (recommended): Truncate summary + tooltip đầy đủ
- Summary ngắn gọn trong card: chỉ show tên ga + distance ("Zhujiajiao · 4.32 km").
- Lat/Lon đầy đủ lưu trong `title` attribute → hover xem.
- Card có `min-height: 72px`, `max-height: 72px` → equal height guaranteed.

### Giải pháp 2 (alternative): Move summary ra ngoài button
- 2 button `.point-picker` nhỏ gọn (chỉ label + pin dot).
- Summary text hiển thị trong 1 block riêng bên dưới, list-style 2 dòng.
- Gọn hơn nhưng phải đụng structure HTML nhiều.

**Chọn giải pháp 1**: ít thay đổi, giữ component cohesion.

### Text template mới
```js
function pointSummary(point, station) {
  // Ngắn gọn cho card
  return `${station.name} · ${station.distance_km.toFixed(2)} km`;
}
function pointSummaryFull(point, station) {
  // Full cho title tooltip
  return `Lat ${point.lat.toFixed(5)}, Lon ${point.lon.toFixed(5)} — Ga gần nhất: ${station.name} (${station.distance_km.toFixed(2)} km)`;
}
```
Set cả 2: `el.textContent = short; el.title = full;`

### Submit button disabled logic
```js
function updatePointSubmitState() {
  els.mapSubmit.disabled = !(state.startPoint && state.goalPoint);
}
```
Gọi trong `onMapClick` sau khi set point, và trong `resetPointSelection`, `clearRouteAndSelection`.

## Related Code Files

### Modify
- `web/app.js`:
  - Rút gọn `pointSummary()` — bỏ lat/lon khỏi text hiển thị.
  - Thêm hàm `pointSummaryFull()` cho tooltip.
  - Trong `onMapClick`, set `summary.textContent = short; summary.title = full`.
  - Thêm `updatePointSubmitState()` + gọi ở đúng chỗ.
- `web/styles.css`:
  - `.point-picker { min-height: 72px; }` (đã có 68, tăng lên 72).
  - `.point-picker p { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; -webkit-line-clamp: 1; }` (đổi từ 2 → 1).
- `web/index.html`:
  - Không đổi structure; optional: thêm `disabled` attribute mặc định cho submit map-mode button → removed khi đủ 2 điểm.

### Create / Delete
- Không.

## Implementation Steps

1. Đọc `onMapClick` để xác định nơi set summary.
2. Sửa `pointSummary` thành short form.
3. Thêm `pointSummaryFull`, set cả `textContent` + `title`.
4. Thêm `updatePointSubmitState()`, gọi sau mỗi update `startPoint`/`goalPoint` và trong reset.
5. Cập nhật CSS: line-clamp 1 + ellipsis + min-height 72.
6. Smoke test:
   - Chọn Điểm đi → card Điểm đi text 1 dòng ngắn → card Điểm đến vẫn equal height cạnh bên → click được.
   - Submit button disabled khi thiếu goal.
   - Hover card Điểm đi → tooltip hiển thị full lat/lon.

## Todo List
- [ ] `pointSummary` rút gọn.
- [ ] `pointSummaryFull` cho title.
- [ ] Set `title` attribute trong `onMapClick`.
- [ ] `updatePointSubmitState()` + gọi ở 4 site (2 set start/goal, reset, clearRouteAndSelection).
- [ ] CSS: `-webkit-line-clamp: 1`, `white-space: nowrap`, `text-overflow: ellipsis`.
- [ ] CSS: `.point-picker { min-height: 72px; }`.
- [ ] Smoke test: narrow viewport 768px → 2 card stack vertical nhưng equal height.

## Success Criteria
- Với viewport 1280+, 2 card luôn side-by-side, equal height.
- Với viewport < 768px, 2 card stack, mỗi card ngắn gọn.
- Summary text 1 dòng, có ellipsis nếu tràn.
- Tooltip hover hiển thị full lat/lon.
- Submit button disabled rõ ràng (opacity 0.5 cursor not-allowed) khi thiếu điểm.
- Screenshot user báo không còn tái hiện được.

## Risk Assessment
- **Risk:** Ellipsis làm user không thấy tên ga dài (vd. "Site of the First CPC National Congress·South Huangpi Road").
  - **Mitigation:** Tooltip full + responsive: tăng min-width card nếu có không gian.
- **Risk:** Submit button disabled làm user không biết phải làm gì.
  - **Mitigation:** Map-hint text + caption "Chọn đủ 2 điểm trước khi tìm đường" khi disabled.

## Security Considerations
- `title` attribute không XSS (browser escape tự động).

## Next Steps
- Phase 08 chạy sau Phase 01 (vì Phase 01 đã có setStatus + aria-pressed liên quan).
- Deploy thử trên 3 viewport (1440, 1024, 768) để verify.
