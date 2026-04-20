# Phase 09 — Collapsible Map Filter Popover

## Context Links
- Phase 07 hiện tại: [phase-07-checkbox-layer-filter.md](phase-07-checkbox-layer-filter.md) — bảng checkbox đang inline trong map-toolbar, chiếm quá nhiều chỗ.
- Screenshot user báo: 20 checkbox đè lên map, bị cắt.
- Code cần sửa: [web/index.html#L126-L137](../../web/index.html#L126), [web/app.js](../../web/app.js) `renderLineFilter`, [web/styles.css](../../web/styles.css) `.map-filter-panel`.

## Overview
- **Priority:** P0 (UX blocker)
- **Status:** Todo
- **Mô tả:** Gói `.map-filter-panel` hiện tại (Phase 07) thành **popover collapse** — default chỉ hiện 1 nút nhỏ trên map-toolbar; click → dropdown floating với toàn bộ checkbox. Pattern chuẩn layer-selector của Google Maps / Leaflet.

## Key Insights
- Default state: panel ẨN. User click icon → hiện full.
- Popover **absolute-positioned** relative to toolbar → không ảnh hưởng layout map.
- Có max-height + scroll cho grid 20 line để không overflow viewport.
- Đóng bằng: click ra ngoài, Esc, hoặc click lại nút.
- Đồng bộ `aria-expanded` cho accessibility.

## Requirements

### Functional
1. 1 nút `.filter-toggle-btn` trong `.map-toolbar` với icon + label "Hiển thị".
2. Click nút → dropdown `.filter-dropdown` hiện (position absolute).
3. Dropdown chứa: checkbox "Trạm", master "Tất cả tuyến", grid 20 line checkbox — **y nguyên nội dung Phase 07**, chỉ đổi wrapper.
4. Đóng popover khi:
   - Click ngoài dropdown.
   - Phím Esc.
   - Click lại nút toggle.
5. Toggle state visual: nút đổi class `.open` khi mở (border nhấn mạnh).
6. `aria-expanded="true|false"` + `aria-controls="filter-dropdown"` cho accessibility.
7. Dropdown max-height ~340px, scroll-y nếu vượt.

### Non-functional
- Không chồng lên Leaflet zoom control (z-index cân nhắc).
- Responsive: mobile popover fit viewport (max-width 90vw).
- Không thêm lib mới.

## Architecture

### HTML
```html
<div class="map-toolbar">
  <div class="legend" id="line-legend"></div>
  <div class="map-filter-popover">
    <button type="button" id="filter-toggle" class="filter-toggle-btn"
            aria-expanded="false" aria-controls="filter-dropdown">
      <span class="filter-icon" aria-hidden="true">⚙</span>
      <span>Hiển thị</span>
    </button>
    <div id="filter-dropdown" class="filter-dropdown hidden"
         role="dialog" aria-label="Bộ lọc hiển thị">
      <p class="selection-caption">Hiển thị bản đồ</p>
      <label class="filter-row">
        <input type="checkbox" id="show-stations" checked />
        <span>Trạm</span>
      </label>
      <label class="filter-row filter-master">
        <input type="checkbox" id="show-all-lines" checked />
        <span>Tất cả tuyến</span>
      </label>
      <div id="line-filter-grid" class="line-filter-grid"></div>
    </div>
  </div>
  <div class="map-hint" id="map-hint">...</div>
</div>
```

### JS — thêm vào app.js
```js
function toggleFilterPopover(force) {
  const open = typeof force === "boolean"
    ? force
    : els.filterDropdown.classList.contains("hidden");
  els.filterDropdown.classList.toggle("hidden", !open);
  els.filterToggle.classList.toggle("open", open);
  els.filterToggle.setAttribute("aria-expanded", String(open));
}

// Outside click listener
document.addEventListener("click", (e) => {
  if (els.filterDropdown.classList.contains("hidden")) return;
  if (e.target.closest(".map-filter-popover")) return;
  toggleFilterPopover(false);
});

// Esc close (bổ sung vào keydown listener có sẵn từ Phase 01)
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !els.filterDropdown.classList.contains("hidden")) {
    toggleFilterPopover(false);
    e.preventDefault();
  }
});

els.filterToggle.addEventListener("click", () => toggleFilterPopover());
```

### CSS
```css
.map-filter-popover {
  position: relative;
}

.filter-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: 6px 12px;
  font-size: var(--fs-sm);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  min-height: 32px;
}
.filter-toggle-btn:hover {
  border-color: var(--color-border-strong);
  background: var(--color-surface-2);
}
.filter-toggle-btn.open {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-soft);
}
.filter-icon { font-size: 14px; }

.filter-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  z-index: 1000;
  width: 300px;
  max-width: 90vw;
  max-height: 360px;
  overflow-y: auto;
  padding: var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  display: grid;
  gap: var(--space-2);
}

/* Mobile: full width aligned left instead of right */
@media (max-width: 767px) {
  .filter-dropdown {
    right: auto;
    left: 0;
    width: calc(100vw - var(--space-8));
  }
}
```

## Related Code Files

### Modify
- `web/index.html`: wrap `.map-filter-panel` nội dung trong cấu trúc toggle + dropdown.
- `web/app.js`:
  - Thêm `els.filterToggle`, `els.filterDropdown`.
  - Thêm `toggleFilterPopover()` + event listeners.
  - Xoá `.map-filter-panel` references nếu có inline logic cũ (Phase 07 mã JS vẫn dùng `#show-stations`, `#show-all-lines`, `#line-filter-grid` — giữ nguyên selector, chỉ đổi wrapper).
- `web/styles.css`:
  - **Xoá** styles `.map-filter-panel` (đang inline).
  - **Thêm** styles `.map-filter-popover`, `.filter-toggle-btn`, `.filter-dropdown`.

### Create / Delete
- Không file.

## Implementation Steps

1. Sửa `index.html` theo markup §Architecture.
2. Thêm reference `els.filterToggle`, `els.filterDropdown` vào `els` object.
3. Viết `toggleFilterPopover(force?)` function.
4. Thêm 3 event listener: click toggle, click outside, Esc.
5. Thay `.map-filter-panel` CSS block bằng 3 block mới.
6. Smoke test:
   - Load page → popover ẩn, chỉ thấy nút "Hiển thị".
   - Click nút → popover hiện, Trạm/Tất cả tuyến + 20 line checkbox đầy đủ.
   - Scroll trong popover OK nếu nhiều line.
   - Click nút lại → đóng.
   - Click ra ngoài → đóng.
   - Esc → đóng.
   - Uncheck "Tất cả tuyến" → các tuyến biến mất khỏi map, popover vẫn mở.
7. Viewport mobile (375px): popover fit màn hình.

## Todo List
- [ ] HTML: wrap filter content trong `.map-filter-popover` + `.filter-dropdown`.
- [ ] JS: `els.filterToggle`, `els.filterDropdown`.
- [ ] JS: `toggleFilterPopover()` + 3 event listeners.
- [ ] CSS: thay `.map-filter-panel` bằng popover styles.
- [ ] Smoke test 7 scenario.

## Success Criteria
- Map không bị đè bởi filter panel.
- Nút toggle compact trong toolbar, dễ nhận.
- Dropdown mở → full checkbox UX của Phase 07.
- Keyboard accessible (Esc đóng, Tab focus vào dropdown).
- Mobile responsive.
- 27 tests backend **không regression**.

## Risk Assessment
- **Risk:** z-index conflict với Leaflet zoom control (Leaflet dùng z-index ~400-1000).
  - **Mitigation:** Dropdown z-index 1000; nếu cần cao hơn, dùng 1100.
- **Risk:** Click outside listener bắt click bên trong Leaflet (vd. click map).
  - **Mitigation:** Check `e.target.closest(".map-filter-popover")` → nếu trong popover thì không đóng; click map thì đóng (desired).
- **Risk:** Phase 01 đã có Esc listener cho point-picker.
  - **Mitigation:** Merge logic: Esc → nếu popover mở → đóng popover; elif đang picking → cancel picking.

## Security Considerations
- Không có.

## Next Steps
- Sau Phase 09: xoá phase-07 nếu cần (hoặc note là Phase 09 kế thừa). Phase 07 vẫn giữ lại làm lịch sử quyết định.
