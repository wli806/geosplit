"""L3:退界包络(EnvelopeResult)→ 前端可画的 2D 负载。用户驱动,不走 REGISTRY/bbox 那套。"""
from contracts.layers import LayerPayload2D

STYLE = {"color": "#1b5e20", "weight": 2, "fillColor": "#66bb6a", "fillOpacity": 0.4}


def to_payload(result):
    """EnvelopeResult → LayerPayload2D(dict)。geometry 为 None 时 data 传空 FeatureCollection。"""
    if result.geometry is None:
        data = {"type": "FeatureCollection", "features": []}
    else:
        data = {"type": "FeatureCollection",
                "features": [{"type": "Feature", "geometry": result.geometry,
                              "properties": {"area_m2": result.area_m2}}]}
    return LayerPayload2D(id="envelope", kind="geojson", data=data, style=STYLE).to_dict()
