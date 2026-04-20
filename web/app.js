const els = {
  startStation: document.querySelector("#start-station"),
  goalStation: document.querySelector("#goal-station"),
  stationOptions: document.querySelector("#station-options"),
  algorithmSelect: document.querySelector("#algorithm-select"),
  routeForm: document.querySelector("#route-form"),
  swapButton: document.querySelector("#swap-button"),
  statusMessage: document.querySelector("#status-message"),
  resultsGrid: document.querySelector("#results-grid"),
  resultTemplate: document.querySelector("#result-template"),
  networkMap: document.querySelector("#network-map"),
  stationModeButton: document.querySelector("#station-mode-button"),
  mapModeButton: document.querySelector("#map-mode-button"),
  stationModePanel: document.querySelector("#station-mode-panel"),
  mapModePanel: document.querySelector("#map-mode-panel"),
  lineLegend: document.querySelector("#line-legend"),
  blockedLinesList: document.querySelector("#blocked-lines-list"),
  clearBlockedLinesButton: document.querySelector("#clear-blocked-lines-button"),
  blockedSegmentStart: document.querySelector("#blocked-segment-start"),
  blockedSegmentGoal: document.querySelector("#blocked-segment-goal"),
  addBlockedSegmentButton: document.querySelector("#add-blocked-segment-button"),
  clearBlockedSegmentsButton: document.querySelector("#clear-blocked-segments-button"),
  blockedSegmentsList: document.querySelector("#blocked-segments-list"),
  mapHint: document.querySelector("#map-hint"),
  startPointSummary: document.querySelector("#start-point-summary"),
  goalPointSummary: document.querySelector("#goal-point-summary"),
  resetPointsButton: document.querySelector("#reset-points-button"),
  selectionSummaryCard: document.querySelector("#selection-summary-card"),
};

const linePalette = [
  "#d05a2d",
  "#0f6a73",
  "#d6aa2d",
  "#52489c",
  "#3e885b",
  "#db5461",
  "#287271",
  "#7c5c2f",
  "#2f4858",
  "#bf4e30",
  "#4b3f72",
  "#1d7874",
];

const algorithmLabels = {
  ucs: "Uniform Cost Search",
  greedy: "Greedy Best-First Search",
  astar: "A* Search",
};

const state = {
  stations: [],
  edges: [],
  stationByName: new Map(),
  lineColors: new Map(),
  lines: [],
  algorithms: [],
  blockedLines: new Set(),
  blockedSegments: new Set(),
  networkBounds: null,
  mode: "station",
  startPoint: null,
  goalPoint: null,
  startNearest: null,
  goalNearest: null,
  pointSelection: null,
  map: null,
  baseEdgeLayer: null,
  stationLayer: null,
  routeLayer: null,
  selectionLayer: null,
};

async function init() {
  initMap();

  try {
    const network = await fetchJson("/api/network");
    state.stations = network.stations;
    state.edges = network.edges;
    state.stationByName = new Map(network.stations.map((station) => [station.name, station]));
    state.networkBounds = L.latLngBounds(network.stations.map((station) => [station.lat, station.lon]));
    state.lines = network.lines ?? [];
    state.algorithms = network.algorithms ?? ["ucs", "greedy", "astar"];

    prepareLineColors(network.edges);
    renderLegend();
    renderBlockedLines();
    renderBlockedSegments();
    renderAlgorithmOptions();
    renderStationOptions(network.stations);
    renderBaseNetwork();
    fitMapToNetwork();
    setMode("station");

    els.statusMessage.textContent = "Dữ liệu mạng đã sẵn sàng. Chọn ga hoặc click trên map.";
  } catch (error) {
    els.statusMessage.textContent = `Không tải được dữ liệu mạng: ${error.message}`;
  }
}

function initMap() {
  state.map = L.map(els.networkMap, {
    zoomControl: true,
    preferCanvas: true,
    minZoom: 10,
    maxBoundsViscosity: 1.0,
    worldCopyJump: false,
  }).setView([31.2304, 121.4737], 11);

  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
    noWrap: true,
  }).addTo(state.map);

  state.map.createPane("metroBasePane");
  state.map.getPane("metroBasePane").style.zIndex = "430";
  state.map.createPane("metroStationPane");
  state.map.getPane("metroStationPane").style.zIndex = "450";
  state.map.createPane("metroRoutePane");
  state.map.getPane("metroRoutePane").style.zIndex = "470";
  state.map.createPane("metroSelectionPane");
  state.map.getPane("metroSelectionPane").style.zIndex = "480";

  state.baseEdgeLayer = L.layerGroup().addTo(state.map);
  state.stationLayer = L.layerGroup().addTo(state.map);
  state.routeLayer = L.layerGroup().addTo(state.map);
  state.selectionLayer = L.layerGroup().addTo(state.map);

  state.map.on("click", onMapClick);
}

function prepareLineColors(edges) {
  const lines = [...new Set(edges.map((edge) => edge.line))].sort();
  lines.forEach((line, index) => {
    state.lineColors.set(line, linePalette[index % linePalette.length]);
  });
}

function renderAlgorithmOptions() {
  els.algorithmSelect.innerHTML = state.algorithms
    .map(
      (algorithm) =>
        `<option value="${escapeHtml(algorithm)}">${escapeHtml(algorithmLabels[algorithm] ?? algorithm)}</option>`,
    )
    .join("");
  els.algorithmSelect.value = "astar";
}

function renderLegend() {
  const preview = [...state.lineColors.keys()].slice(0, 14);
  const extra = Math.max(0, state.lineColors.size - preview.length);

  els.lineLegend.innerHTML = preview
    .map(
      (line) => `
        <span class="legend-item ${state.blockedLines.has(line) ? "blocked" : ""}">
          <i style="background:${state.lineColors.get(line)}"></i>
          ${escapeHtml(line)}
        </span>
      `,
    )
    .join("");

  if (extra > 0) {
    els.lineLegend.insertAdjacentHTML("beforeend", `<span class="legend-item legend-more">+${extra} tuyến nữa</span>`);
  }
}

function renderBlockedLines() {
  els.blockedLinesList.innerHTML = state.lines
    .map(
      (line) => `
        <label class="blocked-line-option">
          <input type="checkbox" value="${escapeHtml(line)}" ${state.blockedLines.has(line) ? "checked" : ""} />
          <span class="blocked-line-chip" style="--line-color:${state.lineColors.get(line) ?? "#777"}">
            ${escapeHtml(line)}
          </span>
        </label>
      `,
    )
    .join("");
}

function segmentKey(stationA, stationB) {
  return [stationA, stationB].sort().join("|||");
}

function parseSegmentKey(key) {
  return key.split("|||");
}

function renderBlockedSegments() {
  if (!state.blockedSegments.size) {
    els.blockedSegmentsList.innerHTML = `<p class="empty-chip">Chưa có đoạn bị cấm.</p>`;
    return;
  }

  els.blockedSegmentsList.innerHTML = [...state.blockedSegments]
    .sort()
    .map((key) => {
      const [source, target] = parseSegmentKey(key);
      return `
        <button type="button" class="segment-chip" data-segment-key="${escapeHtml(key)}">
          ${escapeHtml(source)} - ${escapeHtml(target)}
          <span>×</span>
        </button>
      `;
    })
    .join("");
}

function renderStationOptions(stations) {
  els.stationOptions.innerHTML = stations
    .map((station) => `<option value="${escapeHtml(station.name)}"></option>`)
    .join("");

  if (stations.some((station) => station.name === "Hongqiao Railway Station")) {
    els.startStation.value = "Hongqiao Railway Station";
  }
  if (stations.some((station) => station.name === "Century Avenue")) {
    els.goalStation.value = "Century Avenue";
  }
}

function renderBaseNetwork() {
  state.baseEdgeLayer.clearLayers();
  state.stationLayer.clearLayers();

  state.edges.forEach((edge) => {
    const source = state.stationByName.get(edge.source);
    const target = state.stationByName.get(edge.target);
    if (!source || !target) {
      return;
    }

    const blocked = state.blockedLines.has(edge.line);
    const blockedSegment = state.blockedSegments.has(segmentKey(edge.source, edge.target));
    const latLngs = [
      [source.lat, source.lon],
      [target.lat, target.lon],
    ];

    L.polyline(latLngs, {
      color: blocked || blockedSegment ? "rgba(255,255,255,0.25)" : "rgba(255,255,255,0.92)",
      weight: blocked || blockedSegment ? 5 : 7,
      opacity: blocked || blockedSegment ? 0.12 : 0.88,
      dashArray: blocked || blockedSegment ? "7 8" : null,
      interactive: false,
      pane: "metroBasePane",
    }).addTo(state.baseEdgeLayer);

    L.polyline(latLngs, {
      color: state.lineColors.get(edge.line) ?? "#666",
      weight: blocked || blockedSegment ? 2.6 : 4.2,
      opacity: blocked || blockedSegment ? 0.16 : 0.82,
      dashArray: blocked || blockedSegment ? "7 8" : null,
      interactive: false,
      pane: "metroBasePane",
    }).addTo(state.baseEdgeLayer);
  });

  state.stations.forEach((station) => {
    L.circleMarker([station.lat, station.lon], {
      radius: 4,
      weight: 1.4,
      color: "#16303d",
      fillColor: "#fffdf7",
      fillOpacity: 0.95,
      pane: "metroStationPane",
    })
      .bindTooltip(station.name, { direction: "top", offset: [0, -4] })
      .addTo(state.stationLayer);
  });
}

function fitMapToNetwork() {
  if (!state.networkBounds?.isValid()) {
    return;
  }

  const bounds = state.networkBounds.pad(0.12);
  state.map.setMaxBounds(bounds);
  state.map.fitBounds(bounds, { animate: false });
}

function renderSelectionLayer() {
  state.selectionLayer.clearLayers();

  if (state.startPoint) {
    createPointMarker(state.startPoint, "S", "start").addTo(state.selectionLayer);
  }
  if (state.goalPoint) {
    createPointMarker(state.goalPoint, "G", "goal").addTo(state.selectionLayer);
  }
  if (state.startPoint && state.startNearest) {
    drawConnector(state.startPoint, state.startNearest, "start");
  }
  if (state.goalPoint && state.goalNearest) {
    drawConnector(state.goalPoint, state.goalNearest, "goal");
  }
}

function createPointMarker(point, label, kind) {
  return L.marker([point.lat, point.lon], {
    pane: "metroSelectionPane",
    icon: L.divIcon({
      className: "point-pin-wrapper",
      html: `<div class="point-pin point-pin-${kind}">${label}</div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 14],
    }),
  });
}

function drawConnector(point, nearestStation, kind) {
  const station = state.stationByName.get(nearestStation.name) ?? nearestStation;
  L.polyline(
    [
      [point.lat, point.lon],
      [station.lat, station.lon],
    ],
    {
      color: kind === "start" ? "#d05a2d" : "#0f6a73",
      dashArray: "8 8",
      weight: 3,
      opacity: 0.9,
      pane: "metroSelectionPane",
    },
  ).addTo(state.selectionLayer);

  const midpoint = [(point.lat + station.lat) / 2, (point.lon + station.lon) / 2];
  L.marker(midpoint, {
    pane: "metroSelectionPane",
    icon: L.divIcon({
      className: "connector-chip-wrapper",
      html: `<div class="connector-chip">${nearestStation.distance_km.toFixed(2)} km tới ${escapeHtml(nearestStation.name)}</div>`,
    }),
    interactive: false,
  }).addTo(state.selectionLayer);
}

function highlightPath(result) {
  state.routeLayer.clearLayers();

  const pathLatLngs = [];
  for (let index = 0; index < result.line_sequence.length; index += 1) {
    const source = state.stationByName.get(result.path[index]);
    const target = state.stationByName.get(result.path[index + 1]);
    const line = result.line_sequence[index];
    if (!source || !target) {
      continue;
    }

    pathLatLngs.push([source.lat, source.lon]);

    const latLngs = [
      [source.lat, source.lon],
      [target.lat, target.lon],
    ];

    L.polyline(latLngs, {
      color: "rgba(255,255,255,0.96)",
      weight: 12,
      opacity: 0.95,
      pane: "metroRoutePane",
    }).addTo(state.routeLayer);

    L.polyline(latLngs, {
      color: state.lineColors.get(line) ?? "#111",
      weight: 7.2,
      opacity: 1,
      pane: "metroRoutePane",
    }).addTo(state.routeLayer);
  }

  const lastStation = state.stationByName.get(result.path.at(-1));
  if (lastStation) {
    pathLatLngs.push([lastStation.lat, lastStation.lon]);
  }

  result.path.forEach((stationName, index) => {
    const station = state.stationByName.get(stationName);
    if (!station) {
      return;
    }

    L.circleMarker([station.lat, station.lon], {
      radius: index === 0 || index === result.path.length - 1 ? 8 : 5.5,
      weight: 2,
      color: "#ffffff",
      fillColor: index === 0 ? "#d05a2d" : index === result.path.length - 1 ? "#0f6a73" : "#1f2a32",
      fillOpacity: 0.95,
      pane: "metroRoutePane",
    })
      .bindTooltip(station.name, { permanent: index === 0 || index === result.path.length - 1, direction: "top" })
      .addTo(state.routeLayer);
  });

  const bounds = L.latLngBounds(pathLatLngs);
  if (state.startPoint) {
    bounds.extend([state.startPoint.lat, state.startPoint.lon]);
  }
  if (state.goalPoint) {
    bounds.extend([state.goalPoint.lat, state.goalPoint.lon]);
  }
  if (bounds.isValid()) {
    state.map.fitBounds(bounds.pad(0.22));
  }
}

function renderResults(payload) {
  els.resultsGrid.innerHTML = "";
  els.statusMessage.textContent = `Lộ trình từ ${payload.start} đến ${payload.goal}`;

  state.pointSelection = payload.point_selection ?? null;
  state.startNearest = payload.point_selection?.start_station ?? null;
  state.goalNearest = payload.point_selection?.goal_station ?? null;

  renderSelectionSummary(payload.point_selection ?? null);
  renderSelectionLayer();
  renderLegend();

  const result = payload.results[0];
  const fragment = els.resultTemplate.content.cloneNode(true);
  fragment.querySelector(".algorithm-name").textContent = result.algorithm;
  fragment.querySelector(".route-title").textContent = `${result.path[0]} -> ${result.path.at(-1)}`;
  fragment.querySelector(".chip").textContent = `${result.path.length} ga`;

  const metrics = [
    ["Chi phí", `${result.total_cost.toFixed(2)} phút`],
    ["Quãng đường", `${result.total_distance_km.toFixed(2)} km`],
    ["Mở rộng", `${result.explored_nodes} nút`],
  ];

  fragment.querySelector(".metrics").innerHTML = metrics
    .map(
      ([label, value]) => `
        <div class="metric">
          <span class="metric-label">${label}</span>
          <strong class="metric-value">${value}</strong>
        </div>
      `,
    )
    .join("");

  fragment.querySelector(".path-box").innerHTML = `
    <p class="path-caption">Lộ trình</p>
    <div class="path-route">${escapeHtml(result.path.join(" -> "))}</div>
  `;

  fragment.querySelector(".segment-box").innerHTML = `
    <p class="segment-caption">Chuyển tuyến</p>
    <ul class="segment-list">
      ${result.segments.map((segment) => `<li>${escapeHtml(segment)}</li>`).join("")}
    </ul>
  `;

  if (payload.blocked_lines?.length) {
    fragment.querySelector(".segment-box").insertAdjacentHTML(
      "beforeend",
      `<p class="blocked-note">Cấm tuyến: ${escapeHtml(payload.blocked_lines.join(", "))}</p>`,
    );
  }

  if (payload.blocked_segments?.length) {
    const segmentText = payload.blocked_segments
      .map((segment) => `${segment.source} - ${segment.target}`)
      .join(", ");
    fragment.querySelector(".segment-box").insertAdjacentHTML(
      "beforeend",
      `<p class="blocked-note">Cấm đoạn: ${escapeHtml(segmentText)}</p>`,
    );
  }

  els.resultsGrid.appendChild(fragment);
  highlightPath(result);
}

function renderSelectionSummary(selection) {
  if (!selection) {
    els.selectionSummaryCard.classList.add("hidden");
    els.selectionSummaryCard.innerHTML = "";
    return;
  }

  els.selectionSummaryCard.classList.remove("hidden");
  els.selectionSummaryCard.innerHTML = `
    <div class="selection-summary-grid">
      <div>
        <p class="selection-caption">Điểm đi</p>
        <strong>${escapeHtml(selection.start_station.name)}</strong>
        <p class="selection-summary">Ga gần nhất, cách ${selection.start_station.distance_km.toFixed(2)} km</p>
      </div>
      <div>
        <p class="selection-caption">Điểm đến</p>
        <strong>${escapeHtml(selection.goal_station.name)}</strong>
        <p class="selection-summary">Ga gần nhất, cách ${selection.goal_station.distance_km.toFixed(2)} km</p>
      </div>
    </div>
  `;
}

function resetPointSelection() {
  state.startPoint = null;
  state.goalPoint = null;
  state.startNearest = null;
  state.goalNearest = null;
  state.pointSelection = null;
  els.startPointSummary.textContent = "Chưa có điểm bắt đầu.";
  els.goalPointSummary.textContent = "Chưa có điểm đích.";
  els.selectionSummaryCard.classList.add("hidden");
  els.selectionSummaryCard.innerHTML = "";
  renderSelectionLayer();
}

function addBlockedSegment() {
  const source = els.blockedSegmentStart.value.trim();
  const target = els.blockedSegmentGoal.value.trim();

  if (!source || !target) {
    els.statusMessage.textContent = "Hãy nhập đủ 2 ga cho đoạn bị cấm.";
    return;
  }
  if (source === target) {
    els.statusMessage.textContent = "Đoạn bị cấm phải gồm 2 ga khác nhau.";
    return;
  }
  if (!state.stationByName.has(source) || !state.stationByName.has(target)) {
    els.statusMessage.textContent = "Tên ga trong đoạn bị cấm không hợp lệ.";
    return;
  }

  state.blockedSegments.add(segmentKey(source, target));
  els.blockedSegmentStart.value = "";
  els.blockedSegmentGoal.value = "";
  renderBlockedSegments();
  renderBaseNetwork();
  els.statusMessage.textContent = "Đã thêm đoạn bị cấm.";
}

function removeBlockedSegment(key) {
  state.blockedSegments.delete(key);
  renderBlockedSegments();
  renderBaseNetwork();
}

function clearBlockedSegments() {
  state.blockedSegments.clear();
  renderBlockedSegments();
  renderBaseNetwork();
}

function setMode(mode) {
  state.mode = mode;
  const stationMode = mode === "station";
  els.stationModeButton.classList.toggle("active", stationMode);
  els.mapModeButton.classList.toggle("active", !stationMode);
  els.stationModePanel.classList.toggle("hidden", !stationMode);
  els.mapModePanel.classList.toggle("hidden", stationMode);
  els.mapHint.textContent = stationMode
    ? "Chế độ hiện tại: chọn ga thủ công."
    : "Click lần 1 để đặt điểm bắt đầu, click lần 2 để đặt điểm đích trên bản đồ.";
}

async function onMapClick(event) {
  if (state.mode !== "map") {
    return;
  }

  const point = {
    lat: Number(event.latlng.lat.toFixed(6)),
    lon: Number(event.latlng.lng.toFixed(6)),
  };

  let target = "goal";
  if (!state.startPoint || (state.startPoint && state.goalPoint)) {
    target = "start";
    state.startPoint = point;
    state.goalPoint = null;
    state.startNearest = null;
    state.goalNearest = null;
    state.pointSelection = null;
    els.startPointSummary.textContent = "Đang tìm ga gần nhất cho điểm đi...";
    els.goalPointSummary.textContent = "Chưa có điểm đích.";
  } else {
    state.goalPoint = point;
    state.goalNearest = null;
    state.pointSelection = null;
    els.goalPointSummary.textContent = "Đang tìm ga gần nhất cho điểm đích...";
  }

  renderSelectionLayer();

  try {
    const nearest = await fetchJson(`/api/nearest-station?lat=${point.lat}&lon=${point.lon}`);
    if (target === "start" && state.startPoint?.lat === point.lat && state.startPoint?.lon === point.lon) {
      state.startNearest = nearest.station;
      els.startPointSummary.textContent = pointSummary(point, nearest.station);
    }
    if (target === "goal" && state.goalPoint?.lat === point.lat && state.goalPoint?.lon === point.lon) {
      state.goalNearest = nearest.station;
      els.goalPointSummary.textContent = pointSummary(point, nearest.station);
    }
    renderSelectionLayer();
    els.statusMessage.textContent = "Đã cập nhật điểm trên map.";
  } catch (error) {
    els.statusMessage.textContent = error.message;
  }
}

function pointSummary(point, station) {
  return `Lat ${point.lat.toFixed(5)}, Lon ${point.lon.toFixed(5)}. Ga gần nhất: ${station.name} (${station.distance_km.toFixed(2)} km)`;
}

function blockedLinesQueryString() {
  if (!state.blockedLines.size) {
    return "";
  }
  return [...state.blockedLines]
    .map((line) => `&blocked_lines=${encodeURIComponent(line)}`)
    .join("");
}

function blockedSegmentsQueryString() {
  if (!state.blockedSegments.size) {
    return "";
  }
  return [...state.blockedSegments]
    .map((key) => {
      const [source, target] = parseSegmentKey(key);
      return `&blocked_segments=${encodeURIComponent(`${source}|||${target}`)}`;
    })
    .join("");
}

function selectedAlgorithmQueryString() {
  return `&algorithm=${encodeURIComponent(els.algorithmSelect.value)}`;
}

async function onSubmit(event) {
  event.preventDefault();

  const algorithmQuery = selectedAlgorithmQueryString();
  const blockedLinesQuery = blockedLinesQueryString();
  const blockedSegmentsQuery = blockedSegmentsQueryString();

  if (state.mode === "station") {
    const start = els.startStation.value.trim();
    const goal = els.goalStation.value.trim();
    if (!start || !goal) {
      els.statusMessage.textContent = "Bạn cần chọn đủ 2 ga.";
      return;
    }

    state.pointSelection = null;
    state.startNearest = null;
    state.goalNearest = null;
    renderSelectionSummary(null);
    renderSelectionLayer();

    els.statusMessage.textContent = "Đang tính toán lộ trình...";
    try {
      const payload = await fetchJson(
        `/api/routes?start=${encodeURIComponent(start)}&goal=${encodeURIComponent(goal)}${algorithmQuery}${blockedLinesQuery}${blockedSegmentsQuery}`,
      );
      renderResults(payload);
    } catch (error) {
      els.statusMessage.textContent = error.message;
    }
    return;
  }

  if (!state.startPoint || !state.goalPoint) {
    els.statusMessage.textContent = "Hãy click lên map để chọn đủ điểm đi và điểm đến.";
    return;
  }

  els.statusMessage.textContent = "Đang tìm ga gần nhất và tính lộ trình...";
  try {
    const payload = await fetchJson(
      `/api/routes-by-points?start_lat=${state.startPoint.lat}&start_lon=${state.startPoint.lon}&goal_lat=${state.goalPoint.lat}&goal_lon=${state.goalPoint.lon}${algorithmQuery}${blockedLinesQuery}${blockedSegmentsQuery}`,
    );
    renderResults(payload);
  } catch (error) {
    els.statusMessage.textContent = error.message;
  }
}

function onSwap() {
  const start = els.startStation.value;
  els.startStation.value = els.goalStation.value;
  els.goalStation.value = start;
}

function onBlockedLinesChange(event) {
  if (!event.target.matches("input[type='checkbox']")) {
    return;
  }

  const line = event.target.value;
  if (event.target.checked) {
    state.blockedLines.add(line);
  } else {
    state.blockedLines.delete(line);
  }
  renderLegend();
  renderBaseNetwork();
}

function clearBlockedLines() {
  state.blockedLines.clear();
  renderBlockedLines();
  renderLegend();
  renderBaseNetwork();
}

function onBlockedSegmentsClick(event) {
  const button = event.target.closest("[data-segment-key]");
  if (!button) {
    return;
  }
  removeBlockedSegment(button.dataset.segmentKey);
}

async function fetchJson(url) {
  const response = await fetch(url);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "Request failed");
  }
  return payload;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

els.routeForm.addEventListener("submit", onSubmit);
els.swapButton.addEventListener("click", onSwap);
els.stationModeButton.addEventListener("click", () => setMode("station"));
els.mapModeButton.addEventListener("click", () => setMode("map"));
els.resetPointsButton.addEventListener("click", resetPointSelection);
els.blockedLinesList.addEventListener("change", onBlockedLinesChange);
els.clearBlockedLinesButton.addEventListener("click", clearBlockedLines);
els.addBlockedSegmentButton.addEventListener("click", addBlockedSegment);
els.clearBlockedSegmentsButton.addEventListener("click", clearBlockedSegments);
els.blockedSegmentsList.addEventListener("click", onBlockedSegmentsClick);

init();
