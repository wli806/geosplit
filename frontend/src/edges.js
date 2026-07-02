// 退界包络交互:拆地块边线 → 用户选角色点边(地图点 or 侧栏列表点)→ 全部分类完 → 调后端算可建范围。
import { getEnvelope } from "./api.js";
import { drawEdges, styleEdge, highlightEdge, addOverlay, removeOverlay, UNASSIGNED } from "./map2d.js";

const ROLE_COLOR = { front: "#e53935", back: "#1e88e5", side: "#8d6e63" };

const $ = (id) => document.getElementById(id);

let geometry = null;
let roles = [];
let activeRole = null;

export function initEdges(parcelGeometry) {
  geometry = parcelGeometry;
  const n = geometry.coordinates[0].length - 1;
  roles = new Array(n).fill(null);
  activeRole = null;
  removeOverlay("envelope");
  $("envresult").innerHTML = "";
  $("edgecard").style.display = "block";
  ["r-front", "r-side", "r-back"].forEach((id) => $(id).classList.remove("on"));
  buildList(n);
  updateCount();
  drawEdges(geometry, { onClick: assignEdge, onHover: hoverFromMap });
}

function buildList(n) {
  let html = "";
  for (let i = 0; i < n; i++) {
    html += `<div class="edgeitem" data-i="${i}"><span class="sw" data-sw="${i}"></span>边 ${i + 1}</div>`;
  }
  const box = $("edgelist");
  box.innerHTML = html;
  box.querySelectorAll(".edgeitem").forEach((el) => {
    const i = Number(el.dataset.i);
    el.addEventListener("click", () => assignEdge(i));
    el.addEventListener("mouseenter", () => highlightEdge(i, true));
    el.addEventListener("mouseleave", () => highlightEdge(i, false));
  });
}

// 地图上悬停边 → 侧栏列表项同步高亮(反过来的高亮由 map2d.highlightEdge 处理)。
function hoverFromMap(i, on) {
  highlightEdge(i, on);
  const el = $("edgelist").querySelector(`.edgeitem[data-i="${i}"]`);
  if (el) el.classList.toggle("hi", on);
}

function assignEdge(i) {
  if (!activeRole) { $("edgecount").textContent = "先选上面的角色按钮,再点边"; return; }
  const sw = $("edgelist").querySelector(`[data-sw="${i}"]`);
  if (roles[i] === activeRole) {
    // 同一个角色再点一次 = 选错了,取消这条边的分配
    roles[i] = null;
    styleEdge(i, UNASSIGNED);
    if (sw) sw.style.background = "#fff";
  } else {
    roles[i] = activeRole;
    styleEdge(i, ROLE_COLOR[activeRole]);
    if (sw) sw.style.background = ROLE_COLOR[activeRole];
  }
  updateCount();
}

function updateCount() {
  const done = roles.filter((r) => r).length;
  $("edgecount").textContent = `已选 ${done} / ${roles.length} 条边`;
  $("calcenv").disabled = done !== roles.length;
}

["r-front", "r-side", "r-back"].forEach((id) => {
  $(id).addEventListener("click", () => {
    activeRole = $(id).dataset.role;
    ["r-front", "r-side", "r-back"].forEach((x) => $(x).classList.toggle("on", x === id));
  });
});

$("calcenv").addEventListener("click", async () => {
  const btn = $("calcenv");
  btn.disabled = true;
  $("envresult").textContent = "计算中…";
  try {
    const payload = await getEnvelope(geometry, roles);
    if (payload.error) { $("envresult").textContent = "✗ " + payload.error; return; }
    addOverlay("envelope", payload.data, payload.style);
    const area = payload.data.features[0]?.properties?.area_m2 ?? 0;
    $("envresult").innerHTML = `✓ 退界后可建范围:<b>${area}</b> ㎡`;
  } catch (e) {
    $("envresult").textContent = "✗ 调后端失败:" + e.message;
  } finally {
    btn.disabled = false;
  }
});
