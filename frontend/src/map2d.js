// Leaflet 2D 地图模块:底图切换、画地块、按 LayerSpec 加/去图层。
const map = L.map("map", { zoomControl: true }).setView([-36.842, 174.606], 17);

const STREET = L.tileLayer(
  "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png",
  { maxZoom: 20, attribution: "© CARTO © OpenStreetMap" });
const AERIAL = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  { maxZoom: 20, attribution: "© Esri World Imagery (开发用)" });
STREET.addTo(map);

export function setBasemap(which) {
  if (which === "aerial") { map.removeLayer(STREET); AERIAL.addTo(map); }
  else { map.removeLayer(AERIAL); STREET.addTo(map); }
}

let parcelLayer = null;
export function drawParcel(geometry) {
  if (parcelLayer) map.removeLayer(parcelLayer);
  if (!geometry) return;
  parcelLayer = L.geoJSON({ type: "Feature", geometry },
    { style: { color: "#ff5722", weight: 3, fill: false } }).addTo(map);
  map.fitBounds(parcelLayer.getBounds().pad(0.8));
}

// bbox(地块外扩 50m)→ [minlon,minlat,maxlon,maxlat]
export function bboxOf(geometry, bufferM = 50) {
  let minx = 180, miny = 90, maxx = -180, maxy = -90;
  const walk = (c) => {
    if (typeof c[0] === "number") {
      minx = Math.min(minx, c[0]); maxx = Math.max(maxx, c[0]);
      miny = Math.min(miny, c[1]); maxy = Math.max(maxy, c[1]);
    } else c.forEach(walk);
  };
  walk(geometry.coordinates);
  const dLat = bufferM / 110540, dLon = bufferM / (111320 * Math.cos((miny + maxy) / 2 * Math.PI / 180));
  return [minx - dLon, miny - dLat, maxx + dLon, maxy + dLat];
}

const overlays = {};   // id -> L.layer
export function addOverlay(id, geojson, style) {
  removeOverlay(id);
  overlays[id] = L.geoJSON(geojson, {
    style: () => style,
    pointToLayer: (f, ll) => L.circleMarker(ll, { radius: 4, ...style }),
  }).addTo(map);
}
export function removeOverlay(id) {
  if (overlays[id]) { map.removeLayer(overlays[id]); delete overlays[id]; }
}

// 地块边线:拆成每条边独立可点(退界角色选择用)。
// 每条边画两条线:可见的细线(vis)+ 叠在上面看不见但很粗的判定线(hit,opacity 接近 0 但仍可点击)——
// 边短/边多时(比如十七边形)光靠细线的像素宽度很难点中,hit 线把可点范围放大到 20px。
export const UNASSIGNED = "#333";
const HILITE = "#ffca28";
let edgeLayers = [];   // [{ vis, hit, color }]

export function drawEdges(geometry, { onClick, onHover } = {}) {
  clearEdges();
  const ring = geometry.coordinates[0];
  for (let i = 0; i < ring.length - 1; i++) {
    const latlngs = [[ring[i][1], ring[i][0]], [ring[i + 1][1], ring[i + 1][0]]];
    const vis = L.polyline(latlngs, { color: UNASSIGNED, weight: 5, opacity: 0.9 }).addTo(map);
    const hit = L.polyline(latlngs, { color: "#000", weight: 20, opacity: 0.02 }).addTo(map);
    hit.on("click", () => onClick && onClick(i));
    hit.on("mouseover", () => onHover && onHover(i, true));
    hit.on("mouseout", () => onHover && onHover(i, false));
    edgeLayers.push({ vis, hit, color: UNASSIGNED });
  }
}

export function styleEdge(i, color) {
  const e = edgeLayers[i];
  if (!e) return;
  e.color = color;
  e.vis.setStyle({ color });
}

// 悬停高亮(地图上悬停边、或悬停侧栏列表项时互相联动)。
export function highlightEdge(i, on) {
  const e = edgeLayers[i];
  if (!e) return;
  if (on) e.vis.setStyle({ color: HILITE, weight: 8 });
  else e.vis.setStyle({ color: e.color, weight: 5 });
}

export function clearEdges() {
  edgeLayers.forEach(({ vis, hit }) => { map.removeLayer(vis); map.removeLayer(hit); });
  edgeLayers = [];
}
