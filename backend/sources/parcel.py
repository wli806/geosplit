"""LINZ 地块 → ParcelData。"""
from . import _arcgis
from contracts.site import ParcelData

LINZ = "https://services.arcgis.com/xdsHIIxuCWByZiCB/arcgis/rest/services"
SERVICE = f"{LINZ}/LINZ_NZ_Primary_Parcels/FeatureServer"
SOURCE = "LINZ Primary Parcels"


def fetch(lon, lat):
    """点查命中地块 → ParcelData 或 None。"""
    j = _arcgis.query(SERVICE, 0, lon=lon, lat=lat,
                      out_fields="appellation,survey_area,titles", f="geojson")
    feats = j.get("features", [])
    if not feats:
        return None
    ft = feats[0]
    p = ft.get("properties", {})
    return ParcelData(geometry=ft.get("geometry"),
                      area_m2=p.get("survey_area"),
                      appellation=p.get("appellation"),
                      titles=p.get("titles"))
