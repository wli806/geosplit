"""组装 SiteModel:geocode → parcel/zone/valuation/school,每项包成带溯源的 Field。

纯计算/编排,不含 HTTP 细节(细节在 sources)、不含渲染(渲染在 render)。
"""
from datetime import datetime, timezone
from contracts.site import SiteModel, Field
from sources import geocode, parcel, zone, valuation, school


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _field(value, source, is_local=False):
    return Field(value=value, source=source, fetched_at=_now(), is_local=is_local)


def assemble_site(address):
    """地址 → SiteModel 或 None(地址解析失败)。"""
    ll = geocode.geocode(address)
    if not ll:
        return None
    lon, lat = ll
    return SiteModel(
        address=address,
        lonlat=[lon, lat],
        parcel=_field(parcel.fetch(lon, lat), parcel.SOURCE),
        zone=_field(zone.fetch(lon, lat), zone.SOURCE),
        valuation=_field(valuation.fetch(lon, lat), valuation.SOURCE),
        schools=_field(school.fetch(lon, lat), school.SOURCE),
    )
