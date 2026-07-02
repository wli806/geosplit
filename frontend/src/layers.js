// 模式感知图层列表:由后端 /layers 注册表驱动(加图层=后端加一行,这里不改)。
import { getLayers, getLayer } from "./api.js";
import { addOverlay, removeOverlay } from "./map2d.js";

let specs = [];
let curBbox = null;
const cache = {};   // id -> geojson payload

const swatch = (st) => {
  const c = st.fillColor || st.color || "#999";
  const op = st.fillOpacity != null ? st.fillOpacity : (st.fill === false ? 0 : 0.6);
  return `background:${op ? c : "transparent"};border-color:${st.color || c}`;
};

export async function buildLayerList(mode = "2d") {
  if (!specs.length) specs = (await getLayers()).layers;
  const visible = specs.filter((s) => s.modes.includes(mode));
  const groups = {};
  visible.forEach((s) => (groups[s.group] ||= []).push(s));

  let html = "";
  for (const g of Object.keys(groups)) {
    html += `<div class="grp">${g}</div>`;
    for (const s of groups[g]) {
      html += `<label class="lyr"><input type="checkbox" data-id="${s.id}">
        <span class="sw" style="${swatch(s.style)}"></span>
        <span class="nm">${s.name}</span><span class="note" data-note="${s.id}"></span></label>`;
    }
  }
  const box = document.getElementById("layerlist");
  box.innerHTML = html;
  box.querySelectorAll("input[data-id]").forEach((cb) =>
    cb.addEventListener("change", () => toggle(cb.dataset.id, cb.checked)));
}

export function setBbox(bbox) {
  curBbox = bbox;
  // bbox 变了,清掉已加载缓存,让重新勾选时按新范围取
  for (const k of Object.keys(cache)) delete cache[k];
}

// 范围很大的层(命中也多在屏幕外),提示缩小可见
const BIG_LAYERS = new Set(["schoolzones", "zoning", "flood"]);

function setNote(id, txt) {
  const el = document.querySelector(`[data-note="${id}"]`);
  if (el) el.textContent = txt;
}

async function toggle(id, on) {
  if (!on) { removeOverlay(id); setNote(id, ""); return; }
  if (!curBbox) { setNote(id, "先查询地址"); return; }
  const spec = specs.find((s) => s.id === id);
  setNote(id, "…");
  if (!cache[id]) cache[id] = await getLayer(id, curBbox);
  const data = (cache[id] || {}).data || {};
  if (data.error) { setNote(id, "✗ 出错"); return; }
  const n = (data.features || []).length;
  if (!n) { setNote(id, "无命中"); return; }       // 0 命中是有效结果(如该地无洪泛)
  addOverlay(id, data, spec.style);
  setNote(id, BIG_LAYERS.has(id) ? `✓${n} 缩小可见` : `✓${n}`);
}
