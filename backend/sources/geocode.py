"""地址 → 经纬度。MVP 用 Nominatim(OSM 公用 web API,有限流);做成可插拔,future 换 LINZ/council。"""
import requests
from . import _cache

UA = {"User-Agent": "feasibility-mvp/2.0 (peter@donutbrowser.ai)"}
SOURCE = "Nominatim (OSM)"


def geocode(address):
    """→ (lon, lat) 或 None。"""
    key = f"geocode:{address}"
    c = _cache.get(key)
    if c is not None:
        return tuple(c) if c else None
    r = requests.get("https://nominatim.openstreetmap.org/search",
                     params={"q": f"{address}, Auckland, New Zealand",
                             "format": "json", "limit": 1},
                     headers=UA, timeout=30)
    j = r.json()
    res = [float(j[0]["lon"]), float(j[0]["lat"])] if j else None
    _cache.put(key, res)
    return tuple(res) if res else None
