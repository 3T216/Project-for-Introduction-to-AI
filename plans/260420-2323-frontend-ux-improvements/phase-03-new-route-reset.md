# Phase 03 — Nút "Tìm Tuyến Mới" (Reset Route Trước Khi Tìm)

## Context Links
- Render route: [web/app.js#L345-L412](../../web/app.js#L345-L412) — `highlightPath`
- Submit form: [web/app.js#L643-L690](../../web/app.js#L643-L690) — `onSubmit`
- Reset hiện có (chỉ reset points map-mode): [web/app.js#L506-L517](../../web/app.js#L506-L517) — `resetPointSelection`

## Overview
- **Priority:** P0
- **Status:** Todo
- **Mô tả:** Hiện tại khi user submit tìm đường lần 2, `highlightPath` gọi `state.routeLayer.clearLayers()` **bên trong** — nghĩa là route cũ chỉ bị xoá khi có route mới thành công. Nếu user muốn **xoá sạch** để quan sát network thuần trước khi search lần mới, không có cách. Thêm nút **"🔄 Tìm tuyến mới"** xoá toàn bộ: route highlight, selection points, kết quả, message — về trạng thái zero.

## Key Insights
- Tách `clearRoute()` khỏi `highlightPath()` để có thể gọi độc lập.
- Reset phải xoá: `state.routeLayer`, `state.selectionLayer`, `state.startPoint/goalPoint/Nearest`, `state.pointSelection`, `els.resultsGrid`, `els.selectionSummaryCard`, `els.statusMessage`, input `#start-station` và `#goal-station` (optional — tuỳ UX mong muốn).
- **Giữ nguyên:** `blockedLines`, `blockedSegments`, algorithm select, station visibility mode, base network. User không muốn mất ràng buộc đã set.

## Requirements

### Functional
- Nút "Tìm tuyến mới" luôn hiển thị ở vị trí dễ thấy (gợi ý: cạnh `statusMessage` hoặc ở đầu `results-panel`).
- Bấm nút → xoá route + selection + kết quả, giữ blocked-lines/segments.
- Sau reset, status message đổi thành: "Sẵn sàng tìm tuyến mới. Chọn ga hoặc click map."
- Map `fitBounds` về `state.networkBounds` ban đầu.

### Non-functional
- Không làm mất dữ liệu user đã nhập vào inputs (giữ lại `#start-station`, `#goal-station` text) — chỉ clear point-picker map và kết quả.

## Architecture

### Hàm mới
```js
function clearRouteAndSelection() {
  state.routeLayer.clearLayers();
  resetPointSelection();                // đã có
  state.pointSelection = null;
  els.resultsGrid.innerHTML = "";
  els.selectionSummaryCard.classList.add("hidden");
  els.selectionSummaryCard.innerHTML = "";
  els.statusMessage.textContent = "Sẵn sàng tìm tuyến mới. Chọn ga hoặc click map.";
  if (state.networkBounds?.isValid()) {
    state.map.fitBounds(state.networkBounds.pad(0.12));
  }
}
```

### Vị trí nút trong HTML
Thêm vào đầu `#results-panel` hoặc toolbar phụ:
```html
<button type="button" id="new-route-button" class="ghost-accent">
  Tìm tuyến mới
</button>
```

## Related Code Files

### Modify
- `web/index.html`: thêm nút `#new-route-button` trong `.results-panel .panel-title` hoặc trong `control-panel` dưới `statusMessage`.
- `web/app.js`:
  - Thêm `els.newRouteButton`.
  - Viết `clearRouteAndSelection()`.
  - Listener `els.newRouteButton.addEventListener("click", clearRouteAndSelection);`.
- `web/styles.css`: style `.ghost-accent` hoặc reuse `.secondary`.

### Create / Delete
- Không.

## Implementation Steps

1. Thêm markup nút trong `index.html` (chọn vị trí dưới `#status-message` trong control-panel để luôn thấy).
2. Thêm `els.newRouteButton = document.querySelector("#new-route-button")`.
3. Viết `clearRouteAndSelection()` như trên.
4. Gắn listener.
5. Kiểm tra `resetPointSelection()` (L506) đã clear point-picker button active state (coordinate với Phase 01: nếu Phase 01 thêm `togglePointSelection(null)` vào flow, `resetPointSelection` nên gọi nó).
6. Test scenario:
   - Tìm đường 1 → thấy route → bấm "Tìm tuyến mới" → map sạch → tìm đường 2 → ok.
   - Set blocked line → bấm "Tìm tuyến mới" → blocked line vẫn còn.
   - Trong map-mode: chọn 2 điểm → tìm đường → bấm nút → points biến mất, inputs station mode vẫn giữ.

## Todo List
- [ ] HTML: Thêm `#new-route-button`.
- [ ] JS: Thêm reference `els.newRouteButton`.
- [ ] JS: Viết `clearRouteAndSelection`.
- [ ] JS: Gắn listener.
- [ ] JS: Verify `resetPointSelection` reset nút point-picker từ Phase 01.
- [ ] CSS: Style nút (ghost/secondary, icon 🔄).
- [ ] Test: 3 scenario đã liệt kê.

## Success Criteria
- Bấm nút → map chỉ còn base network, không còn route/selection.
- Blocked lines/segments/algorithm select không đổi.
- `statusMessage` thông báo đúng.
- Map zoom về toàn mạng.

## Risk Assessment
- **Risk:** `resetPointSelection` cũ (L506) không biết về state của Phase 01 (`pointSelectionTarget`).
  - **Mitigation:** Phase 01 đã plan thêm `togglePointSelection(null)` vào cuối `resetPointSelection` — coordinate khi implement.
- **Risk:** `fitBounds` về full network gây khó chịu nếu user đang zoom chi tiết. → chấp nhận, đó là ý nghĩa "reset".

## Security Considerations
- Không có.

## Next Steps
- Phase 04 sẽ chọn vị trí/style nút cuối cùng cho đẹp.
