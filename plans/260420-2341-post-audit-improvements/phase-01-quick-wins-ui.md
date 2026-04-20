# Phase 01 — Quick Wins UI/UX

## Context Links
- Audit: `plans/reports/code-reviewer-260420-2341-full-project-audit.md` (items P1#1, P2#8, P2#9, P3#4, P3#11, P3#12)
- CSS sẵn có: [web/styles.css#L629-L666](../../web/styles.css#L629-L666) — `[data-state]` variants

## Overview
- **Priority:** P1
- **Status:** Todo
- **Mô tả:** Gom các fix nhỏ, nhanh, có tác động rõ rệt: kích hoạt CSS chết, 2 phím tắt, xoá dead code, vá bug submit sai mode.

## Key Insights
- CSS `status-message[data-state=...]` đã tồn tại nhưng JS không set → **dead code**. Chỉ cần thêm 1 dòng mỗi call site.
- 2 nút `type="submit"` trong cùng form → Enter có thể submit nhầm mode. Đổi nút của mode **đang ẩn** thành `type="button"` qua JS (hoặc đổi runtime khi `setMode`).
- `renderStationOptions` ghi đè `startStation.value` mỗi lần gọi → nếu network response trễ, input user bị clobber. Chỉ set default khi input đang rỗng.

## Requirements

### Functional
1. `data-state` trên `#status-message` set đúng: `"loading"` khi fetch, `"error"` khi catch, `"success"` khi có route, `"info"` mặc định.
2. Phím `Esc` khi đang pick point → `togglePointSelection(null)`.
3. Phím `Enter` KHÔNG submit form khi đang focus `#blocked-segment-start|goal` (để user nhập đoạn cấm không bị trigger submit).
4. Button submit của mode đang ẩn có `type="button"` runtime (không submit khi Enter).
5. `#new-route-button` cũng bị Esc nếu bạn đang trong picking mode.
6. `renderStationOptions` chỉ set default nếu input rỗng.
7. Xoá class `.visually-hidden` không dùng.
8. Thêm favicon inline data-URI.
9. `aria-pressed="true|false"` cho `.visibility-toggle` và `.point-picker`.

### Non-functional
- Không đổi API, không đổi behavior chính.

## Architecture

### Helper nhỏ
```js
function setStatus(text, state = "info") {
  els.statusMessage.textContent = text;
  els.statusMessage.dataset.state = state;
}
```
Thay tất cả call `els.statusMessage.textContent = ...` → `setStatus(..., state)`.

### Key bindings (global)
```js
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && state.pointSelectionTarget) {
    togglePointSelection(null);
    e.preventDefault();
  }
});
```

### Submit-button swap theo mode
Trong `setMode()`, sau khi toggle panel:
```js
els.stationSubmit.type = stationMode ? "submit" : "button";
els.mapSubmit.type     = stationMode ? "button" : "submit";
```
Cần reference `els.stationSubmit` và `els.mapSubmit` (query `#station-mode-panel button[type='submit']` và `#map-mode-panel button[type='submit']`).

## Related Code Files

### Modify
- `web/app.js`:
  - Thêm `setStatus()`.
  - Thay ~14 call site `statusMessage.textContent = ...`.
  - Keydown listener.
  - Sửa `setMode` để đổi `type`.
  - Sửa `renderStationOptions` — chỉ set khi rỗng.
  - Update `aria-pressed` trong `togglePointSelection` và `applyStationVisibility`.
- `web/index.html`:
  - Thêm `<link rel="icon" href="data:image/svg+xml,...">` (SVG metro icon đơn giản).
  - Thêm `aria-pressed="false"` mặc định vào 2 `.point-picker` và 3 `.visibility-toggle`.
- `web/styles.css`: xoá `.visually-hidden` block (5 dòng).

### Create / Delete
- Không.

## Implementation Steps

1. Viết `setStatus(text, state)` đầu `web/app.js`.
2. Grep tất cả `statusMessage.textContent =` → thay thành `setStatus(text, "loading"|"error"|"success"|"info")` theo context:
   - "Đang tải..." / "Đang tính toán..." → `"loading"`
   - Catch block → `"error"`
   - "Lộ trình từ X đến Y" → `"success"`
   - Default/idle → `"info"`
3. Trong `init()` cuối success: `setStatus("Dữ liệu mạng đã sẵn sàng...", "info")`.
4. Thêm `els.stationSubmit`, `els.mapSubmit` queries.
5. Trong `setMode`, toggle `type` attribute 2 nút.
6. Thêm global keydown listener cho Esc.
7. Sửa `renderStationOptions`: wrap set-default trong `if (!els.startStation.value)`.
8. Trong `togglePointSelection`, set `aria-pressed` cho 2 nút point-picker theo target.
9. Trong `applyStationVisibility`, set `aria-pressed` cho 3 visibility button.
10. Xoá `.visually-hidden` trong CSS.
11. Thêm `<link rel="icon" ...>` SVG trong `<head>`.
12. Smoke test: reload page → data-state loading thấy màu teal, error thấy màu đỏ, success màu xanh.

## Todo List
- [ ] `setStatus()` helper + thay 14 call site.
- [ ] Esc keydown cancel picking.
- [ ] `setMode` toggle submit button type.
- [ ] `renderStationOptions` chỉ set default khi rỗng.
- [ ] `aria-pressed` cho point-picker và visibility-toggle.
- [ ] Xoá `.visually-hidden`.
- [ ] Favicon inline SVG.
- [ ] Test: Esc cancel, Enter trong blocked-segment input không submit form.

## Success Criteria
- `document.querySelector("#status-message").dataset.state` đổi đúng 4 state.
- 404 `/favicon.ico` biến mất trong DevTools Network.
- Enter trong `#blocked-segment-start` KHÔNG submit form.
- Esc khi đang picking → nút bỏ active.
- Screen reader đọc được `aria-pressed` state.

## Risk Assessment
- **Risk:** Esc listener có thể can thiệp modal/dialog khác.
  - **Mitigation:** Chỉ preventDefault khi đang có `pointSelectionTarget`.
- **Risk:** Đổi `type=submit` runtime có thể bị quên ở init.
  - **Mitigation:** Gọi `setMode(state.mode)` sau khi set element refs để sync ngay từ đầu.

## Security Considerations
- Favicon data-URI SVG phải không chứa script (dùng SVG tĩnh).
- `aria-pressed` không có rủi ro XSS.

## Next Steps
- Phase 02, 03, 04, 06 có thể chạy song song.
