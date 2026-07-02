"""L3 图层注册表 + 2D 负载。

★ 加一个 GeoMap 图层 = 往 REGISTRY 加一行 LayerSpec(展示叠加层走通用 _arcgis,零额外代码)。
本阶段全部 modes=["2d"];引入 Cesium 后给支持 3D 的层加 "3d" 并补 3D 画法。
"""
from contracts.layers import LayerSpec, LayerPayload2D
from sources import _arcgis

LINZ = "https://services.arcgis.com/xdsHIIxuCWByZiCB/arcgis/rest/services"
COUNCIL = "https://mapspublic.aklc.govt.nz/arcgis/rest/services"
COUNCIL3 = "https://mapspublic.aklc.govt.nz/arcgis3/rest/services"
MOE = "https://services.arcgis.com/XTtANUDT8Va4DLwI/arcgis/rest/services"

REGISTRY = [
    LayerSpec(id="parcels", name="地块", group="基础", modes=["2d"], kind="geojson",
              source={"service": f"{LINZ}/LINZ_NZ_Primary_Parcels/FeatureServer",
                      "layer_id": 0, "f": "geojson"},
              style={"color": "#e53935", "weight": 1.5, "fill": False}),
    LayerSpec(id="zoning", name="分区", group="规划", modes=["2d"], kind="geojson",
              source={"service": f"{COUNCIL3}/NonCouncil/UnitaryPlanZones/MapServer",
                      "layer_id": 1, "f": "json"},
              style={"color": "#8e24aa", "weight": 1, "fillColor": "#ab47bc", "fillOpacity": 0.20}),
    LayerSpec(id="flood", name="洪水区域(Flood Plains)", group="水文", modes=["2d"], kind="geojson",
              source={"service": f"{COUNCIL}/LiveMaps/CatchmentsAndHydrology/MapServer",
                      "layer_id": 14, "f": "json"},
              style={"color": "#1e88e5", "weight": 1, "fillColor": "#42a5f5", "fillOpacity": 0.35}),
    LayerSpec(id="contours", name="等高线(1m)", group="地形", modes=["2d"], kind="geojson",
              source={"service": f"{COUNCIL}/Contours2024/MapServer",
                      "layer_id": 9, "f": "json"},
              style={"color": "#8d6e63", "weight": 0.8}),
    LayerSpec(id="schoolzones", name="学校校区", group="社区", modes=["2d"], kind="geojson",
              source={"service": f"{MOE}/NZ_School_Zone_boundaries/FeatureServer",
                      "layer_id": 0, "f": "geojson"},
              style={"color": "#43a047", "weight": 1.2, "dashArray": "4", "fill": False}),
]

_BY_ID = {s.id: s for s in REGISTRY}


def list_specs():
    """给前端建左侧列表(注册表驱动)。"""
    return [s.public() for s in REGISTRY]


def get_payload(layer_id, bbox):
    """取某图层在 bbox 内的 2D 负载(GeoJSON + 样式)。bbox=(minlon,minlat,maxlon,maxlat)。"""
    spec = _BY_ID.get(layer_id)
    if not spec:
        return None
    src = spec.source
    j = _arcgis.query(src["service"], src["layer_id"], bbox=bbox, f=src.get("f", "geojson"))
    return LayerPayload2D(id=spec.id, kind="geojson", data=j, style=spec.style).to_dict()
