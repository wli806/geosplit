"""L4 瘦路由(FastAPI)。只做:解析请求 → 调 domain/render → 返回 JSON 契约。

跑法:双击 start.bat(起本服务 :8001 + 前端 :5501),或手动
     py -m uvicorn api.app:app --port 8001 --app-dir backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from domain.site import assemble_site
from domain.envelope import compute_envelope
from render import layers as render_layers
from render import envelope as render_envelope

app = FastAPI(title="Subdivision Feasibility — backend (V2)")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/ping")
def ping():
    return {"ok": True, "msg": "backend alive"}


@app.get("/site")
def site(address: str):
    """地址 → SiteModel(parcel/zone/valuation/school,每项带溯源)。"""
    sm = assemble_site(address)
    if sm is None:
        return {"error": "address not found"}
    return sm.to_dict()


@app.get("/layers")
def layers():
    """图层注册表清单 → 前端建左侧 GeoMap 式列表。"""
    return {"layers": render_layers.list_specs()}


@app.get("/layers/{layer_id}")
def layer(layer_id: str, bbox: str):
    """某图层在 bbox 内的 2D 负载。bbox='minlon,minlat,maxlon,maxlat'。"""
    try:
        b = [float(x) for x in bbox.split(",")]
        assert len(b) == 4
    except Exception:
        return {"error": "bbox 需为 'minlon,minlat,maxlon,maxlat'"}
    payload = render_layers.get_payload(layer_id, b)
    if payload is None:
        return {"error": f"unknown layer: {layer_id}"}
    return payload


class EnvelopeRequest(BaseModel):
    geometry: dict     # 地块 GeoJSON Polygon(前端已有,来自 /site 的 parcel.value.geometry)
    edge_roles: list    # 按外环边顺序,每条边 "front" | "back" | "side"


@app.post("/envelope")
def envelope(req: EnvelopeRequest):
    """地块多边形 + 每条边角色(用户在地图上点选)→ 退界后可建范围 + 面积。"""
    result = compute_envelope(req.geometry, req.edge_roles)
    if result.geometry is None:
        return {"error": "边数与角色数量不匹配,或退界后无剩余空间", "edge_roles": result.edge_roles}
    return render_envelope.to_payload(result)
