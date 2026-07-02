"""通用 ArcGIS 查询(层内私有工具)。点/包围盒查询 + Esri JSON → GeoJSON。

各类型源(parcel/valuation/school)与展示叠加层(flood/contours…)都复用它。
坑:council 旧服务器(mapspublic /arcgis*)的 MapServer 不支持 f=geojson,要用 f=json 再自己转;
    LINZ / AGOL(services*.arcgis.com)支持 f=geojson。
"""
import requests
from . import _cache

UA = {"User-Agent": "feasibility-mvp/2.0 (peter@donutbrowser.ai)"}


def query(service_url, layer_id, *, lon=None, lat=None, bbox=None,
          out_fields="*", return_geometry=True, where=None,
          f="geojson", timeout=60, cache=True):
    """查某图层 → 统一返回 GeoJSON FeatureCollection(dict)。
    点查:给 lon/lat;范围查:给 bbox=(minlon,minlat,maxlon,maxlat)。
    """
    url = f"{service_url}/{layer_id}/query"
    params = {"outFields": out_fields, "returnGeometry": str(return_geometry).lower(),
              "outSR": 4326, "f": f, "spatialRel": "esriSpatialRelIntersects"}
    if where:
        params["where"] = where
    elif bbox is not None:
        params["geometry"] = ",".join(str(c) for c in bbox)
        params["geometryType"] = "esriGeometryEnvelope"
        params["inSR"] = 4326
    else:
        params["geometry"] = f"{lon},{lat}"
        params["geometryType"] = "esriGeometryPoint"
        params["inSR"] = 4326

    key = f"arcgis:{url}:{sorted(params.items(), key=lambda kv: kv[0])}"
    if cache:
        c = _cache.get(key)
        if c is not None:
            return c

    r = requests.get(url, params=params, headers=UA, timeout=timeout)
    j = r.json()
    if "features" not in j and "error" in j:
        return {"type": "FeatureCollection", "features": [], "error": j.get("error")}
    if f == "json":
        j = esri_to_geojson(j)
    if cache and "features" in j:
        _cache.put(key, j)
    return j


def esri_to_geojson(j):
    """Esri JSON → GeoJSON(point / polyline / polygon)。"""
    feats = []
    for ef in j.get("features", []):
        g = ef.get("geometry") or {}
        geom = None
        if "x" in g:
            geom = {"type": "Point", "coordinates": [g["x"], g["y"]]}
        elif "paths" in g:
            geom = {"type": "MultiLineString", "coordinates": g["paths"]}
        elif "rings" in g:
            geom = {"type": "Polygon", "coordinates": g["rings"]}
        feats.append({"type": "Feature", "geometry": geom,
                      "properties": ef.get("attributes", {})})
    return {"type": "FeatureCollection", "features": feats}
