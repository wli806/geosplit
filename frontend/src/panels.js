// 信息面板:逐字段显示值 + 来源标注(溯源)。
const fmtMoney = (v) => (typeof v === "number" ? "$" + v.toLocaleString() : v);

function row(k, v) { return `<div class="kv"><span class="k">${k}</span><span class="v">${v ?? "—"}</span></div>`; }
function srcLine(f) { return `<div class="src">来源:${f.source}${f.is_local ? " · 本地" : ""} · ${(f.fetched_at || "").replace("T", " ").replace("+00:00", "Z")}</div>`; }

export function renderInfo(site) {
  const p = site.parcel.value || {};
  const z = site.zone.value || {};
  const val = site.valuation.value || {};
  const sc = (site.schools.value || {}).schools || [];

  let html = "";
  // 地块
  html += `<div class="card"><h2>地块</h2>
    ${row("面积", (p.area_m2 ?? "—") + " ㎡")}
    ${row("法定描述", p.appellation)}
    ${row("产权 title", p.titles)}
    ${row("分区", z.zone)}
    ${srcLine(site.parcel)}</div>`;
  // 估值
  html += `<div class="card"><h2>估值 CV</h2>
    ${row("最新 CV (2024)", fmtMoney(val.latest_cv))}
    ${row("最新土地价 LV", fmtMoney(val.latest_lv))}
    ${row("估值基准日", val.latest_valuation_date)}
    ${row("上轮 CV", fmtMoney(val.cv))}
    <div class="warn">CV 是政府 rating 估值,非市场成交价;收支测算里只作锚点。</div>
    ${srcLine(site.valuation)}</div>`;
  // 学校
  const list = sc.length
    ? sc.map((s) => row(s.name, s.type)).join("")
    : `<div class="kv"><span class="k">命中校区</span><span class="v">无</span></div>`;
  html += `<div class="card"><h2>学校校区</h2>${list}
    <div class="warn">校区边界为 indication,精度有限;请向学校确认入学资格。</div>
    ${srcLine(site.schools)}</div>`;

  document.getElementById("info").innerHTML = html;
}
