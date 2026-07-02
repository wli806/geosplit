"""MoE 校区 → SchoolData(点 Intersects 命中的学校)。边界为 indication,精度不高。"""
from . import _arcgis
from contracts.site import SchoolData

SERVICE = ("https://services.arcgis.com/XTtANUDT8Va4DLwI/arcgis/rest/services"
           "/NZ_School_Zone_boundaries/FeatureServer")
SOURCE = "MoE School Zones"


def fetch(lon, lat):
    j = _arcgis.query(SERVICE, 0, lon=lon, lat=lat, return_geometry=False,
                      out_fields="School_ID,School_name,Institution_type,Effective_date", f="geojson")
    schools = []
    for ft in j.get("features", []):
        p = ft.get("properties", {})
        schools.append({"id": p.get("School_ID"), "name": p.get("School_name"),
                        "type": p.get("Institution_type"), "effective_date": p.get("Effective_date")})
    return SchoolData(schools=schools)
