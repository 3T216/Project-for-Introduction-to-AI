# Phase 05 — Performance: Cache Leaflet Polylines Instead of Rebuild

## Context Links
- Audit item: P1 #4 / P2 — `renderBaseNetwork` tái tạo 2000+ polyline mỗi toggle
- File: [web/app.js#L235-L289](../../web/app.js#L235)

## Overview
- **Priority:** P2
- **Status:** Todo
- **Mô tả:** Hiện tại mỗi lần toggle block-line hoặc add/remove blocked-segment, `renderBaseNetwork()` gọi `state.baseEdgeLayer.clearLayers()` rồi tạo lại **toàn bộ** polyline (2 polyline/edge × ~1000 edges = ~2000 object). Refactor sang cache ref, chỉ `setStyle` khi toggle.

## Key Insights
- Edge hiện chỉ có 2 trạng thái visual: normal hoặc blocked. Rule: `blocked = state.blockedLines.has(edge.line) || state.blockedSegments.has(segmentKey(...))`.
- Thay vì clear+rebuild: lưu `state.edgePolylines = Map<string, {bgLine, fgLine, edge}>`. Khi toggle, iterate map và gọi `setStyle` theo trạng thái mới.
- Cùng lúc, `state.stationMarkers` đã cache (Phase 02) — giữ nguyên.
- Điều kiện tiên quyết: blocked state chỉ đổi visual, không đổi topology. Đúng: blocking chỉ ảnh hưởng pathfinding ở backend, frontend vẫn hiển thị graph đầy đủ nhưng mờ.

## Requirements

### Functional
1. `renderBaseNetwork` vẫn chạy đầy đủ **lần đầu** (init).
2. Toggle blocked-line / add-segment / remove-segment → gọi `restyleEdges()` thay vì full rebuild.
3. Visual kết quả không đổi so với hiện tại.

### Non-functional
- Toggle ≥10× nhanh hơn với 411 station dataset (đo bằng DevTools Performance).
- Không tăng memory leak: clearLayers vẫn phải dùng nếu user reload data mạng.

## Architecture

### State
```js
state.edgePolylines = new Map();  // key = edgeKey(source, target, line), value = {bgLine, fgLine, edge}
```

### Helper
```js
function edgeKey(edge) {
  return `${edge.source}|||${edge.target}|||${edge.line}`;
}

function edgeStyle(edge) {
  const blocked = state.blockedLines.has(edge.line)
                || state.blockedSegments.has(segmentKey(edge.source, edge.target));
  return {
    bg: {
      color: blocked ? "rgba(255,255,255,0.25)" : "rgba(255,255,255,0.92)",
      weight: blocked ? 5 : 7,
      opacity: blocked ? 0.12 : 0.88,
      dashArray: blocked ? "7 8" : null,
    },
    fg: {
      color: state.lineColors.get(edge.line) ?? "#666",
      weight: blocked ? 2.6 : 4.2,
      opacity: blocked ? 0.16 : 0.82,
      dashArray: blocked ? "7 8" : null,
    },
  };
}

function restyleEdges() {
  state.edgePolylines.forEach(({ bgLine, fgLine, edge }) => {
    const style = edgeStyle(edge);
    bgLine.setStyle(style.bg);
    fgLine.setStyle(style.fg);
  });
}
```

### `renderBaseNetwork` refactor
- Lần đầu: clear layer, tạo polyline, lưu vào `state.edgePolylines`.
- Lần sau (nếu đã có entries): không gọi `renderBaseNetwork`, chỉ `restyleEdges()`.

### Callers cần thay
Tìm `renderBaseNetwork()` trong app.js:
- `init()` → giữ nguyên (lần đầu).
- `onBlockedLinesChange` → thay `renderBaseNetwork()` bằng `restyleEdges()`.
- `addBlockedSegment`, `removeBlockedSegment`, `clearBlockedSegments` → tương tự.

## Related Code Files

### Modify
- `web/app.js`:
  - Thêm `state.edgePolylines`.
  - Tách `edgeStyle(edge)`, `restyleEdges()`.
  - Refactor `renderBaseNetwork` — lưu polyline vào Map.
  - Thay ~4 call site `renderBaseNetwork()` → `restyleEdges()` khi chỉ toggle blocked state.

### Create / Delete
- Không.

## Implementation Steps

1. Đọc `renderBaseNetwork` hiện tại (L235-289).
2. Extract `edgeStyle(edge)` + `restyleEdges()`.
3. Sửa `renderBaseNetwork`: clear `state.edgePolylines`, push entries.
4. Grep `renderBaseNetwork()` → xác định callers.
5. Đổi callers không đổi topology → `restyleEdges()`.
6. Test:
   - Block line 2 → đường Line 2 mờ, dashed.
   - Unblock → rõ lại.
   - Add segment block → đoạn đó mờ.
   - DevTools Performance: toggle 10× block/unblock, expect < 50ms mỗi lần (so với ~300ms rebuild).

## Todo List
- [ ] Thêm `state.edgePolylines` Map.
- [ ] Viết `edgeStyle(edge)` pure function.
- [ ] Viết `restyleEdges()`.
- [ ] Refactor `renderBaseNetwork` lưu ref vào Map.
- [ ] Thay callers không đổi topology.
- [ ] Smoke test 3 scenario (block line / add segment / remove segment).
- [ ] Performance so sánh (optional, nếu có DevTools).

## Success Criteria
- Toggle blocked-line không tạo polyline mới (kiểm bằng Leaflet `_layers` count).
- Visual không đổi.
- 14 backend tests không bị ảnh hưởng (frontend-only change).

## Risk Assessment
- **Risk:** Memory leak nếu `state.edgePolylines` không clear khi reload data.
  - **Mitigation:** Ở đầu `renderBaseNetwork`, clear `state.edgePolylines.clear()` + `state.baseEdgeLayer.clearLayers()`.
- **Risk:** Phase 02 `applyStationVisibility` phụ thuộc `renderBaseNetwork` có chạy lại.
  - **Mitigation:** Verify: Phase 02 call `applyStationVisibility` trong `renderBaseNetwork`. Sau refactor, `restyleEdges` không chạm station layer → cần gọi `applyStationVisibility(state.stationVisibility)` cả trong `restyleEdges` để giữ sync (hoặc bỏ qua vì visibility không đổi khi toggle line).

## Security Considerations
- Không có.

## Next Steps
- Phase cuối. Sau đây: smoke test toàn bộ.
