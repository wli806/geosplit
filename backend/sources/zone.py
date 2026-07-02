"""council 分区 → ZoneData。UnitaryPlanZones 在 arcgis3,用 identify 点查 ZONE。"""
import requests
from contracts.site import ZoneData
from . import _cache

COUNCIL3 = "https://mapspublic.aklc.govt.nz/arcgis3/rest/services"
UA = {"User-Agent": "feasibility-mvp/2.0 (peter@donutbrowser.ai)"}
SOURCE = "council UnitaryPlanZones"


def fetch(lon, lat):
    key = f"zone:{lon:.6f},{lat:.6f}"
    c = _cache.get(key)
    if c is not None:
        return ZoneData(**c)
    d = 0.002
    r = requests.get(f"{COUNCIL3}/NonCouncil/UnitaryPlanZones/MapServer/identify",
                     params={"geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint",
                             "sr": 4326, "tolerance": 3,
                             "mapExtent": f"{lon-d},{lat-d},{lon+d},{lat+d}",
                             "imageDisplay": "800,600,96", "layers": "all",
                             "returnGeometry": "false", "f": "json"},
                     headers=UA, timeout=60)
    res = r.json().get("results", [])
    zone = res[0]["attributes"].get("ZONE") if res else None
    out = {"zone": zone, "geometry": None}
    _cache.put(key, out)
    return ZoneData(**out)
