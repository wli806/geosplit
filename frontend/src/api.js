// 后端调用封装(L5 → L4)。改地址只改这里。
const BASE = "http://localhost:8001";

async function j(url) {
  const r = await fetch(url, { cache: "no-store" });
  return r.json();
}

export const getSite = (address) =>
  j(`${BASE}/site?address=${encodeURIComponent(address)}&_=${Date.now()}`);

export const getLayers = () => j(`${BASE}/layers`);

export const getLayer = (id, bbox) =>
  j(`${BASE}/layers/${id}?bbox=${bbox.join(",")}`);
