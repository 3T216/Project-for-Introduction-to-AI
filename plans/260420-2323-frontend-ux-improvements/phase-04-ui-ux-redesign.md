# Phase 04 — UI/UX Redesign (Dùng Agent `ui-ux-designer`)

## Context Links
- CSS hiện tại: [web/styles.css](../../web/styles.css) (~10 KB)
- HTML layout: [web/index.html](../../web/index.html) — `page-shell compact-shell` với `layout compact-layout`
- Leaflet CSS: `https://unpkg.com/leaflet@1.9.4/dist/leaflet.css`

## Overview
- **Priority:** P1
- **Status:** Todo
- **Mô tả:** Redesign visual layer: design tokens, typography scale, spacing rhythm, button hierarchy, responsive behavior. Chạy **sau** Phase 01/02/03 vì những phase đó thêm element mới cần style.
- **Công cụ:** Delegate cho agent `ui-ux-designer` để lấy audit + design tokens + CSS mới; không redesign thủ công.

## Key Insights
- Layout hiện tại 3 section dọc: `control-panel` (sidebar trái), `visual-panel` (map giữa), `results-panel` (dưới). Giữ cấu trúc, chỉ refine.
- Style đang dùng màu ấm "cream" (nền `#fffdf7`, accent `#d05a2d`). Có thể giữ palette metro hoặc chuyển sang neutral-dark hơn (tuỳ agent đề xuất).
- Vấn đề cần giải quyết:
  - Button hierarchy không rõ (primary vs secondary vs compact).
  - Spacing không nhất quán (mix `px` và không có scale).
  - Responsive: < 1024px chắc chắn bị tràn — cần stack layout.
  - Results card khá đặc, path list dài khó đọc.
  - Segmented controls (mode-toggle) nhỏ.
- Không dùng framework (Tailwind/Bootstrap) — giữ vanilla CSS với custom properties để đơn giản.

## Requirements

### Functional (visual-only, không đổi behaviour)
- Design tokens thành CSS custom properties trong `:root`.
- Typography scale: ít nhất 4 size (h1, h2, body, caption).
- Spacing scale: 4/8/12/16/24/32 (hoặc rem equivalents).
- Color palette: semantic (primary, accent, danger, muted, surface, surface-2).
- Button variants: primary, secondary, ghost, icon-only, danger.
- Layout responsive breakpoints: desktop (≥1280), tablet (768-1279), mobile (<768).
- Map toolbar có đủ chỗ cho: legend, map-hint, segmented visibility control (từ Phase 02).

### Non-functional
- Bundle size CSS không tăng quá 2x (giữ ~20 KB).
- Không thêm dependency external (giữ vanilla, không Tailwind/Bootstrap).
- Dark mode không bắt buộc (YAGNI) — chỉ cần tokens-ready để sau dễ thêm.

## Architecture

### Delegate cho `ui-ux-designer`
**Prompt template** khi spawn agent:
```
Task: Redesign CSS của web/styles.css cho Metro Thượng Hải app.
Work context: g:/TTMT/Project-for-Introduction-to-AI-001/Project-for-Introduction-to-AI
Input files:
  - web/index.html (đọc cấu trúc)
  - web/styles.css (audit hiện tại)
  - plans/260420-2323-frontend-ux-improvements/phase-01..03.md (elements mới)

Yêu cầu:
  1. Audit UI hiện tại, list điểm yếu.
  2. Đề xuất design tokens (colors, spacing, typography, radius, shadow).
  3. Viết lại styles.css với tokens + component classes.
  4. Style các element mới từ Phase 01 (.point-picker), Phase 02 (.station-visibility-control), Phase 03 (#new-route-button).
  5. Responsive đến 360px.
  6. KHÔNG sửa JS/HTML structure logic — chỉ class names nếu cần thêm (phải báo lại để update HTML).
  7. Output: file styles.css mới + changelog ngắn.

Constraints:
  - Vanilla CSS, không framework.
  - Giữ palette metro-like (có thể refine), không đổi tone drastically.
  - Tối ưu cho Leaflet map: không ảnh hưởng `.leaflet-container`.
  - Size < 25KB.
```

### Pattern components cần có
- `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-danger`
- `.panel`, `.panel-title`, `.card`
- `.chip`, `.chip-line`, `.chip-blocked`
- `.segmented-control` (dùng cho mode-toggle + station-visibility-control)
- `.point-picker` (từ Phase 01)
- `.metric`, `.metric-label`, `.metric-value`
- `.form-field`, `.form-field-label`

## Related Code Files

### Modify
- `web/styles.css` — rewrite (có backup git diff).
- `web/index.html` — chỉ thêm/đổi class nếu agent yêu cầu (vd. thay `.toggle` → `.segmented-btn`).

### Create / Delete
- Không.

## Implementation Steps

1. Commit Phase 01/02/03 trước để có clean baseline.
2. Spawn agent `ui-ux-designer` với prompt ở trên.
3. Agent trả về:
   - Audit report (viết vào `plans/260420-2323-frontend-ux-improvements/ui-audit-report.md`).
   - CSS mới → ghi đè `web/styles.css`.
   - Danh sách class names đổi → apply vào `web/index.html`.
4. Chạy `python app.py`, kiểm tra visually trên 3 viewport (1440, 1024, 375).
5. Nếu có issue → iterate với agent (max 2 vòng).
6. Screenshot before/after đính vào PR description.

## Todo List
- [ ] Merge Phase 01/02/03 trước.
- [ ] Spawn `ui-ux-designer` với prompt đầy đủ context.
- [ ] Apply CSS mới từ agent.
- [ ] Apply class name changes vào HTML.
- [ ] Test 3 viewport (desktop / tablet / mobile).
- [ ] Test interaction: hover, focus, active states đầy đủ.
- [ ] Verify Leaflet map không bị break (tiles load, controls hiện).
- [ ] Screenshot before/after.

## Success Criteria
- Design tokens được define trong `:root`.
- Typography consistent (không còn random font-size inline).
- Button hierarchy rõ: primary action nổi bật, secondary nhẹ nhàng.
- Responsive: không horizontal scroll ở 375px.
- Accessibility: contrast AA cho text chính, focus ring rõ ràng.
- Leaflet controls (zoom, attribution) không bị style đè gây vỡ.

## Risk Assessment
- **Risk:** Agent viết CSS overlap/conflict với Leaflet's `.leaflet-*` classes.
  - **Mitigation:** Prompt explicit: không đụng selector bắt đầu `.leaflet-`.
- **Risk:** Class name changes làm JS selectors vỡ (vd. `.toggle` trong `app.js` L12-13).
  - **Mitigation:** Khi apply class đổi, grep `app.js` tìm tất cả selectors cũ → đổi đồng bộ.
- **Risk:** Agent output quá dài, bundle > 25KB.
  - **Mitigation:** Nếu vượt, request compact pass loại utility classes không dùng.

## Security Considerations
- CSS không có security concern trực tiếp. Nhưng nếu agent thêm external fonts (Google Fonts) → phải whitelist CSP; tránh inline SVG chứa script.

## Next Steps
- Sau Phase 04: commit `style(web): redesign UI with design tokens`.
- Optional: Phase 05 (không trong scope hiện tại) — thêm dark mode, i18n, keyboard shortcuts.
