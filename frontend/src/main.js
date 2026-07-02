// 编排:查询地址 → 画地块 + 信息面板 + 图层列表(按 bbox)。
import { getSite } from "./api.js";
import { drawParcel, bboxOf, setBasemap } from "./map2d.js";
import { renderInfo } from "./panels.js";
import { buildLayerList, setBbox } from "./layers.js";

const $ = (id) => document.getElementById(id);

async function run() {
  const addr = $("addr").value.trim();
  const btn = $("go"), st = $("status");
  btn.disabled = true; st.textContent = "查询中…";
  try {
    const site = await getSite(addr);
    if (site.error) { st.textContent = "✗ " + site.error; return; }
    const p = site.parcel.value || {};
    st.textContent = `✓ ${(site.zone.value || {}).zone || ""} · ${p.area_m2 ?? "?"} ㎡`;
    renderInfo(site);
    if (p.geometry) {
      drawParcel(p.geometry);
      setBbox(bboxOf(p.geometry, 50));
    }
    await buildLayerList("2d");
  } catch (e) {
    st.textContent = "✗ 调后端失败:" + e.message;
  } finally {
    btn.disabled = false;
  }
}

$("go").addEventListener("click", run);
$("addr").addEventListener("keydown", (e) => { if (e.key === "Enter") run(); });
$("b-street").addEventListener("click", () => { setBasemap("street"); $("b-street").classList.add("on"); $("b-aerial").classList.remove("on"); });
$("b-aerial").addEventListener("click", () => { setBasemap("aerial"); $("b-aerial").classList.add("on"); $("b-street").classList.remove("on"); });

$("attr").innerHTML = "底图:CARTO / Esri(开发用)· 数据:LINZ · Auckland Council · MoE";
run();
