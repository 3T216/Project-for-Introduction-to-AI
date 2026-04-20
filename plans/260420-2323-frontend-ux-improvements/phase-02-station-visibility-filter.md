# Phase 02 — Nút Ẩn/Hiện Trạm (Station Visibility Toggle)

## Context Links
- Code render trạm: [web/app.js#L265-L276](../../web/app.js#L265-L276) — `state.stationLayer`
- Legend/toolbar: [web/index.html#L115-L121](../../web/index.html#L115-L121)

## Overview
- **Priority:** P1
- **Status:** Todo
- **Mô tả:** Map hiện có 411 trạm. Các trạm nhỏ/ngoại ô (Xuying Road, Panlong Road, v.v.) làm rối khi zoom rộng. Thêm **toggle 3 mức** hiển thị trạm:
  - `all` — hiện tất cả (mặc định)
  - `labels-only` — chỉ hiện chấm, **không** hiện tooltip/name
  - `hidden` — ẩn hoàn toàn lớp trạm (vẫn giữ đường tuyến màu)

## Key Insights
- Lớp `state.stationLayer` hiện tại vẽ `L.circleMarker` + `bindTooltip`. Có 2 cách:
  - **A (đơn giản — chọn):** thêm/xoá `state.stationLayer` khỏi map; với mode `labels-only` dùng `unbindTooltip()` trên từng marker.
  - **B (phức tạp):** giữ danh sách trạm "major" và filter. Không làm vì dataset OSM không có thuộc tính major/minor đáng tin cậy → YAGNI.
- Trạm của route đang highlight nằm ở `state.routeLayer` (riêng), nên không bị ảnh hưởng khi ẩn `stationLayer`.
- Dùng segmented control 3 nút trong map-toolbar bên cạnh legend.

## Requirements

### Functional
- Segmented control 3 nút: "Tất cả ga", "Chỉ chấm", "Ẩn ga".
- Mặc định: "Tất cả ga".
- Chuyển mode → map cập nhật ngay, không reload.
- Route đang highlight **không** bị ẩn khi toggle (route có layer riêng).

### Non-functional
- Không ảnh hưởng performance: 411 markers không re-create khi toggle, chỉ ẩn/hiện.

## Architecture

### State
```js
state.stationVisibility = "all"; // "all" | "dots" | "hidden"
```

### Implementation
- Lưu reference markers để toggle tooltip:
  ```js
  state.stationMarkers = [];  // populate in renderBaseNetwork
  ```
- Hàm `applyStationVisibility()`:
  - `hidden` → `state.map.removeLayer(state.stationLayer)`
  - `dots`/`all` → ensure added, rồi `stationMarkers.forEach(m => m.unbindTooltip() | m.bindTooltip(name))`.

## Related Code Files

### Modify
- `web/index.html`: trong `.map-toolbar` (sau `#line-legend`) thêm:
  ```html
  <div class="station-visibility-control" role="group" aria-label="Hiển thị ga">
    <button type="button" data-visibility="all" class="visibility-toggle active">Tất cả</button>
    <button type="button" data-visibility="dots" class="visibility-toggle">Chỉ chấm</button>
    <button type="button" data-visibility="hidden" class="visibility-toggle">Ẩn</button>
  </div>
  ```
- `web/app.js`:
  - Thêm `state.stationVisibility`, `state.stationMarkers = []`.
  - Sửa `renderBaseNetwork` (L265-276): `const marker = L.circleMarker(...); state.stationMarkers.push(marker); marker.addTo(state.stationLayer);`.
  - Thêm hàm `applyStationVisibility(mode)`.
  - Listener click trên `.station-visibility-control`.
- `web/styles.css`: style segmented control.

### Create / Delete
- Không.

## Implementation Steps

1. Thêm HTML segmented control vào `map-toolbar`.
2. Thêm `state.stationMarkers = []`, `state.stationVisibility = "all"`.
3. Trong `renderBaseNetwork`, clear `state.stationMarkers = []` đầu function, push mỗi marker sau khi tạo.
4. Viết:
   ```js
   function applyStationVisibility(mode) {
     state.stationVisibility = mode;
     if (mode === "hidden") {
       state.map.removeLayer(state.stationLayer);
     } else {
       if (!state.map.hasLayer(state.stationLayer)) state.stationLayer.addTo(state.map);
       state.stationMarkers.forEach((marker) => {
         marker.unbindTooltip();
         if (mode === "all") marker.bindTooltip(marker._stationName, { direction: "top", offset: [0, -4] });
       });
     }
     document.querySelectorAll(".visibility-toggle").forEach((btn) =>
       btn.classList.toggle("active", btn.dataset.visibility === mode)
     );
   }
   ```
   → cần lưu `marker._stationName = station.name` khi tạo.
5. Delegate click listener trên container `.station-visibility-control` gọi `applyStationVisibility(btn.dataset.visibility)`.
6. Gọi `applyStationVisibility("all")` cuối `init()` để sync UI.
7. Test: toggle 3 mode, kiểm tra route vẫn hiện khi "Ẩn ga".

## Todo List
- [ ] HTML: Thêm segmented control trong map-toolbar.
- [ ] JS: Thêm state `stationVisibility`, `stationMarkers`.
- [ ] JS: Gắn ref marker trong `renderBaseNetwork`.
- [ ] JS: Viết `applyStationVisibility`.
- [ ] JS: Listener click segmented control.
- [ ] CSS: Style `.station-visibility-control` + `.visibility-toggle.active`.
- [ ] Test: toggle, kiểm tra route không bị ẩn.

## Success Criteria
- 3 mode hoạt động đúng.
- Route đã highlight vẫn giữ khi ẩn trạm.
- Không re-render toàn bộ network khi toggle (performance OK).

## Risk Assessment
- **Risk:** Clear `stationMarkers` không đúng lúc khi re-render (vd. khi add blocked segment → gọi `renderBaseNetwork`).
  - **Mitigation:** Luôn `state.stationMarkers = []` ở đầu `renderBaseNetwork`.
- **Risk:** Khi `stationLayer` bị remove khỏi map, add mới blocked segment sẽ không làm trạm hiện lại vì `renderBaseNetwork` clear rồi re-populate layer nhưng layer không ở map.
  - **Mitigation:** Sau mỗi `renderBaseNetwork`, gọi `applyStationVisibility(state.stationVisibility)` để re-apply.

## Security Considerations
- Không có input user mới → không rủi ro.

## Next Steps
- Phase 04 polish style segmented control.
