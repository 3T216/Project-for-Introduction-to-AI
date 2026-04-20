# Phase 01 — Refactor Map Click Mode: 2 Nút Set Start / Set Goal

## Context Links
- Code hiện tại: [web/app.js#L568-L612](../../web/app.js#L568-L612) (hàm `onMapClick`)
- UI hiện tại: [web/index.html#L88-L103](../../web/index.html#L88-L103) (`map-mode-panel`)

## Overview
- **Priority:** P0
- **Status:** Todo
- **Mô tả:** Hiện tại khi ở chế độ click map, mỗi click tự động alternate start → goal → start. Gây nhầm: người dùng muốn chỉnh riêng 1 điểm thường xoá cả 2. Thay bằng **2 nút tường minh** "📍 Đặt điểm đi" và "🎯 Đặt điểm đến"; user bấm nút → vào mode chọn điểm đó → click map → chốt điểm → thoát mode.

## Key Insights
- State hiện tại `state.startPoint` và `state.goalPoint` đủ dùng, chỉ cần thêm `state.pointSelectionTarget: "start" | "goal" | null` thay cho logic auto-alternate.
- Khi `pointSelectionTarget === "start"`, click map cập nhật `state.startPoint`; tương tự goal.
- Phải cho user biết đang ở mode nào (highlight nút active, đổi cursor bản đồ sang `crosshair`).

## Requirements

### Functional
- 2 nút trong `map-mode-panel`: "Đặt điểm đi" và "Đặt điểm đến".
- Bấm 1 nút → active state → click map đặt điểm tương ứng → tự động thoát mode chọn.
- Bấm lại cùng nút khi đang active → cancel mode.
- Khi chưa active nút nào, click map không có tác dụng (không auto-alternate).
- Giữ nút "Xoá điểm" và nút Submit "Tìm đường từ điểm đã chọn".

### Non-functional
- Feedback rõ: nút đang active đổi màu, `map-hint` text đổi theo mode, con trỏ map đổi `cursor: crosshair`.
- Không regression: chế độ "Chọn ga thủ công" (`station` mode) không bị ảnh hưởng.

## Architecture

### State mới
```js
state.pointSelectionTarget = null;  // "start" | "goal" | null
```

### Flow
```
User click "Đặt điểm đi"
  → state.pointSelectionTarget = "start"
  → button "Đặt điểm đi" có class .active
  → map hint: "Click trên map để chọn điểm đi"
  → map container class: .selecting-point
User click map
  → nếu pointSelectionTarget = null: bỏ qua
  → nếu "start": set state.startPoint, fetch nearest, render marker
  → reset pointSelectionTarget = null, bỏ .active
```

## Related Code Files

### Modify
- `web/index.html`:
  - Bỏ 2 `selection-card` "Bước 1/Bước 2" (L89-98).
  - Thêm 2 nút `#set-start-button`, `#set-goal-button` + 2 ô summary hiển thị kết quả chọn.
- `web/app.js`:
  - Thêm `state.pointSelectionTarget`.
  - Refactor `onMapClick` (L568-612) để kiểm tra `pointSelectionTarget` thay cho logic `!startPoint || (startPoint && goalPoint)`.
  - Thêm hàm `togglePointSelection(target)`.
  - Thêm event listener cho 2 nút mới.
- `web/styles.css`:
  - Style `.set-point-button.active { background: var(--accent); color: #fff }`.
  - `.network-map.selecting-point { cursor: crosshair }`.

### Create / Delete
- Không tạo file mới, không xoá file.

## Implementation Steps

1. Sửa `index.html` trong `#map-mode-panel`: thay 2 selection-card bằng markup:
   ```html
   <div class="point-picker-row">
     <button type="button" id="set-start-button" class="point-picker">
       <span class="pin-dot pin-start"></span>
       <div>
         <strong>Điểm đi</strong>
         <p id="start-point-summary">Chưa có điểm đi.</p>
       </div>
     </button>
     <button type="button" id="set-goal-button" class="point-picker">
       <span class="pin-dot pin-goal"></span>
       <div>
         <strong>Điểm đến</strong>
         <p id="goal-point-summary">Chưa có điểm đến.</p>
       </div>
     </button>
   </div>
   ```
2. Trong `app.js` thêm `els.setStartButton`, `els.setGoalButton`.
3. Thêm `state.pointSelectionTarget = null`.
4. Viết hàm:
   ```js
   function togglePointSelection(target) {
     state.pointSelectionTarget = state.pointSelectionTarget === target ? null : target;
     els.setStartButton.classList.toggle("active", state.pointSelectionTarget === "start");
     els.setGoalButton.classList.toggle("active", state.pointSelectionTarget === "goal");
     els.networkMap.classList.toggle("selecting-point", !!state.pointSelectionTarget);
     updateMapHint();
   }
   ```
5. Sửa `onMapClick`: return sớm nếu `!state.pointSelectionTarget`; nhánh start/goal chạy theo target; sau khi xong → `state.pointSelectionTarget = null; togglePointSelection(null);`.
6. Gắn listener 2 nút → `togglePointSelection("start" | "goal")`.
7. Cập nhật `setMode("station")`: clear `pointSelectionTarget` để thoát sạch.
8. Chạy `python app.py`, test: click nút Start → click map → marker S xuất hiện → nút bỏ active → click map không làm gì nữa.

## Todo List
- [ ] HTML: Thay selection-card bằng 2 nút point-picker.
- [ ] JS: Thêm `state.pointSelectionTarget`.
- [ ] JS: Viết `togglePointSelection(target)`.
- [ ] JS: Refactor `onMapClick` theo target.
- [ ] JS: Gắn listener 2 nút + clear khi đổi mode.
- [ ] CSS: Style `.point-picker`, `.active`, `.selecting-point` cursor.
- [ ] Test thủ công: chọn start → chỉnh goal riêng → chỉnh start riêng.

## Success Criteria
- Người dùng chọn từng điểm độc lập, không còn auto-overwrite khi click lần 3.
- Active state của nút rõ ràng (màu/border).
- Con trỏ map đổi `crosshair` khi đang ở mode chọn.
- Bấm lại nút đang active → huỷ mode.

## Risk Assessment
- **Risk:** Quên clear `pointSelectionTarget` khi `setMode("station")` → user chuyển tab vẫn trong selection mode.
  - **Mitigation:** Gọi `togglePointSelection(null)` đầu hàm `setMode`.
- **Risk:** Race condition với `fetchJson` nearest-station (nếu user bấm nhanh 2 lần).
  - **Mitigation:** Check `state.startPoint?.lat === point.lat` trước khi apply response (đã có pattern ở L599).

## Security Considerations
- Không phát sinh input mới → không có rủi ro XSS mới.

## Next Steps
- Phase 04 sẽ restyle nút `.point-picker` cho đẹp.
