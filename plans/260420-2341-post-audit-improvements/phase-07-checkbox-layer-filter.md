# Phase 07 — Checkbox Layer Filter (Thay Segmented Control)

## Context Links
- Code hiện tại: [web/index.html#L125-L129](../../web/index.html#L125) — `.station-visibility-control`
- JS: [web/app.js](../../web/app.js) — `applyStationVisibility(mode)`, `renderBaseNetwork`
- Plan cũ: [plans/260420-2323-frontend-ux-improvements/phase-02-station-visibility-filter.md](../260420-2323-frontend-ux-improvements/phase-02-station-visibility-filter.md) (sẽ bị deprecate bởi phase này)

## Overview
- **Priority:** P1
- **Status:** Todo
- **Mô tả:** Thay `.station-visibility-control` (3 nút: Tất cả / Chỉ chấm / Ẩn) bằng **bảng checkbox** cho phép:
  - Tick/bỏ tick hiển thị **trạm** (1 checkbox)
  - Tick/bỏ tick hiển thị **từng tuyến** (1 checkbox/tuyến, ~20 tuyến)
  - Master checkbox "Tất cả tuyến" bật/tắt cả 20
- **Phân biệt:** checkbox này **chỉ ảnh hưởng visual** (hide/show layer). Nó **không liên quan** đến panel "Tuyến bị cấm" (vẫn giữ nguyên — đó là ràng buộc tìm đường).

## Key Insights
- 20 tuyến × 1 checkbox = 20 ô. Cần layout hợp lý: grid 2-3 cột, mỗi hàng compact.
- State visual riêng: `state.hiddenLines: Set<string>` (nếu line trong set → ẩn khỏi map). Khác với `state.blockedLines` (ràng buộc tìm đường).
- Khi `hiddenLines` đổi → restyle các polyline (dùng `display:none` hoặc `map.removeLayer`). Với Phase 05 đã cache polyline → chỉ gọi `hide/show` cho line đó.
- Trạm: giữ 1 checkbox "Hiện tất cả trạm" thay cho segmented 3-state. Bỏ mode "Chỉ chấm" vì checkbox lý luận binary (hiện/ẩn).

## Requirements

### Functional
1. Panel mới `.map-filter-panel` trong map-toolbar (thay `.station-visibility-control`):
   - Header: "Hiển thị bản đồ"
   - Row 1: checkbox "Trạm" (mặc định checked).
   - Row 2: checkbox "Tất cả tuyến" (master) + grid 20 checkbox/tuyến.
2. Checkbox line có circle color (giống `.blocked-line-chip`) để dễ nhận.
3. Uncheck "Trạm" → ẩn station layer.
4. Uncheck 1 tuyến → polyline của tuyến đó biến mất khỏi map.
5. Uncheck "Tất cả tuyến" master → toàn bộ line bị ẩn; check lại → hiện lại.
6. Route đang highlight (`state.routeLayer`) **không bị ảnh hưởng** bởi filter này.

### Non-functional
- Panel gọn, không chiếm quá ~140px cao.
- Có thể collapse/expand (nếu chiếm nhiều chỗ) — nice-to-have, không bắt buộc.

## Architecture

### State
```js
state.hiddenLines = new Set();        // lines ẩn visual
state.showStations = true;            // boolean
```

### HTML (thay `.station-visibility-control`)
```html
<div class="map-filter-panel">
  <p class="selection-caption">Hiển thị bản đồ</p>
  <label class="filter-row">
    <input type="checkbox" id="show-stations" checked />
    <span>Trạm</span>
  </label>
  <label class="filter-row filter-master">
    <input type="checkbox" id="show-all-lines" checked />
    <span>Tất cả tuyến</span>
  </label>
  <div id="line-filter-grid" class="line-filter-grid">
    <!-- rendered by JS: 1 label+checkbox per line -->
  </div>
</div>
```

### JS
```js
function renderLineFilter() {
  els.lineFilterGrid.innerHTML = state.lines.map(line => `
    <label class="filter-row filter-line">
      <input type="checkbox" data-line="${escapeHtml(line)}"
             ${state.hiddenLines.has(line) ? "" : "checked"} />
      <span class="line-dot" style="background:${state.lineColors.get(line)}"></span>
      <span>${escapeHtml(line)}</span>
    </label>
  `).join("");
}

function onLineFilterChange(e) {
  const line = e.target.dataset.line;
  if (!line) return;
  if (e.target.checked) state.hiddenLines.delete(line);
  else state.hiddenLines.add(line);
  applyLineVisibility();
}

function applyLineVisibility() {
  // Nếu Phase 05 đã xong: iterate state.edgePolylines, set display theo line
  state.edgePolylines?.forEach(({ bgLine, fgLine, edge }) => {
    const hidden = state.hiddenLines.has(edge.line);
    const op = hidden ? "removeFrom" : "addTo";
    // fallback if Phase 05 chưa làm: dùng setStyle opacity 0 + interactive false
    if (hidden) {
      bgLine.setStyle({ opacity: 0 });
      fgLine.setStyle({ opacity: 0 });
    } else {
      bgLine.setStyle({ opacity: 0.88 });
      fgLine.setStyle({ opacity: 0.82 });
    }
  });
}

function onShowStationsChange(e) {
  state.showStations = e.target.checked;
  if (e.target.checked) state.stationLayer.addTo(state.map);
  else state.map.removeLayer(state.stationLayer);
}

function onShowAllLinesChange(e) {
  if (e.target.checked) {
    state.hiddenLines.clear();
  } else {
    state.lines.forEach(l => state.hiddenLines.add(l));
  }
  renderLineFilter();
  applyLineVisibility();
}
```

## Related Code Files

### Modify
- `web/index.html`: thay `.station-visibility-control` block bằng `.map-filter-panel` markup.
- `web/app.js`:
  - Xoá `state.stationVisibility`, giữ `state.stationMarkers` (vẫn cần).
  - Thêm `state.hiddenLines`, `state.showStations`.
  - Xoá `applyStationVisibility` (3-state), thay bằng:
    - `onShowStationsChange`
    - `onLineFilterChange`, `onShowAllLinesChange`
    - `renderLineFilter`, `applyLineVisibility`
  - Gọi `renderLineFilter()` trong `init()` sau khi có `state.lines`.
- `web/styles.css`: thêm styles cho `.map-filter-panel`, `.filter-row`, `.line-filter-grid`, `.line-dot`.

### Create / Delete
- Không file.

### CSS additions (khoảng 40 dòng)
```css
.map-filter-panel {
  display: grid;
  gap: var(--space-2);
  padding: var(--space-3);
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  min-width: 220px;
  max-width: 320px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--fs-sm);
  cursor: pointer;
}

.filter-row input[type="checkbox"] { accent-color: var(--color-primary); }

.filter-master {
  font-weight: var(--fw-semibold);
  padding-bottom: var(--space-2);
  border-bottom: 1px dashed var(--color-border);
}

.line-filter-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-1) var(--space-2);
  max-height: 160px;
  overflow-y: auto;
}

.line-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}
```

## Implementation Steps

1. Xoá markup `.station-visibility-control` trong `index.html`, thay bằng `.map-filter-panel`.
2. Thêm state mới + xoá state cũ (`stationVisibility`).
3. Viết 5 function JS ở §Architecture.
4. Gắn event listener: delegated trên `.line-filter-grid` cho change.
5. Thêm CSS block trên.
6. Test: uncheck Line 2 → tất cả polyline Line 2 biến mất; check → xuất hiện lại. Master checkbox bật/tắt tất cả.
7. Verify route highlight không bị ẩn.

## Todo List
- [ ] HTML: thay segmented → `.map-filter-panel`.
- [ ] JS: state `hiddenLines`, `showStations`.
- [ ] JS: `renderLineFilter`, `applyLineVisibility`, handlers.
- [ ] CSS: panel + grid + line-dot.
- [ ] Smoke test 4 case: uncheck line / uncheck stations / master off / master on.

## Success Criteria
- 20 checkbox tuyến hiện đủ, màu chấm match legend.
- Uncheck 1 tuyến → line biến mất, các tuyến khác còn.
- Master checkbox hoạt động 2 chiều.
- Route active không bị ẩn dù uncheck line của nó.
- Panel không gây overflow toolbar.

## Risk Assessment
- **Risk:** 20 checkbox làm toolbar cao → chiếm không gian map.
  - **Mitigation:** `max-height: 160px; overflow-y: auto` cho grid; panel collapsible nếu cần.
- **Risk:** User bối rối giữa "Tuyến bị cấm" (pathfind) vs "Hiển thị tuyến" (visual).
  - **Mitigation:** Caption rõ: "Hiển thị bản đồ" vs "Ràng buộc tìm đường". Document trong README (Phase 06).
- **Risk:** Conflict với Phase 05 — nếu Phase 05 dùng `setStyle`, Phase 07 cũng cần tương thích.
  - **Mitigation:** Làm Phase 07 **sau** Phase 05; dùng chung `state.edgePolylines`.

## Security Considerations
- Không có.

## Next Steps
- Phase 08 (layout fix) sau hoặc song song.
- Deprecate Phase 02 của plan `260420-2323-frontend-ux-improvements` (segmented control sẽ bị thay).
