"""council 估值 → ValuationData。

主源:官方 Rates24_SnapshotReval(AGOL FeatureServer)。取 LCV/LLV 为最新一轮(2024 reval)。
取不到 → 全 "N/A"(不猜区域均值)。CV 是 rating 值,非市场卖价(收支里当锚点)。
"""
from datetime import datetime, timezone
from . import _arcgis
from contracts.site import ValuationData

SERVICE = ("https://services1.arcgis.com/n4yPwebTjJCmXB6W/arcgis/rest/services"
           "/AGOL_RateAccountInfo1_gdb/FeatureServer")
SOURCE = "council Rates24_SnapshotReval"


def _date(ms):
    if not ms:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date().isoformat()


def fetch(lon, lat):
    j = _arcgis.query(SERVICE, 0, lon=lon, lat=lat, return_geometry=False,
                      out_fields="CV,LV,LCV,LLV,VALUATIONDATE,LATESTVALUATIONDATE", f="geojson")
    feats = j.get("features", [])
    if not feats:
        return ValuationData()        # 默认全 "N/A"
    p = feats[0].get("properties", {})
    return ValuationData(
        cv=p.get("CV", "N/A"), lv=p.get("LV", "N/A"),
        latest_cv=p.get("LCV", "N/A"), latest_lv=p.get("LLV", "N/A"),
        valuation_date=_date(p.get("VALUATIONDATE")),
        latest_valuation_date=_date(p.get("LATESTVALUATIONDATE")))
