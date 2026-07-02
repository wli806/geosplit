"""退界包络(yard setback envelope):纯几何计算,无 HTTP 无渲染。

算法:每条边按角色往地块内侧偏移对应距离(90° 垂直量),
所有偏移线在地块内侧的半平面求交集 → 剩下的区域就是可建范围。
对任意多边形(含凹多边形、双 front 角地)都成立——每条边独立算半平面,顺序不影响交集结果。

数值来源:Records/AUP-MHU规则数值.md(H5.6.8,前 2.5 / 侧 1 / 后 1,90° 量)。
坐标运算须在米制坐标系下做,这里用 NZTM2000(EPSG:2193);GeoJSON 输入输出统一 4326。
"""
from pyproj import Transformer
from shapely.geometry import Polygon, mapping

from contracts.analysis import EnvelopeResult

YARD_M = {"front": 2.5, "back": 1.0, "side": 1.0}   # H5.6.8

_TO_NZTM = Transformer.from_crs("EPSG:4326", "EPSG:2193", always_xy=True)
_TO_WGS84 = Transformer.from_crs("EPSG:2193", "EPSG:4326", always_xy=True)


def _project(coords):
    return [_TO_NZTM.transform(x, y) for x, y in coords]


def _unproject(coords):
    return [_TO_WGS84.transform(x, y) for x, y in coords]


def _halfplane(p1, p2, distance, ccw_sign, reach):
    """边 p1→p2 往内偏移 distance 后的半平面(一个覆盖内侧的大多边形)。
    ccw_sign:整个环是逆时针(+1)还是顺时针(-1),决定"内侧"是左手边还是右手边。
    reach:延伸长度,须盖过地块本身,保证凹角处半平面依然完整覆盖内侧。
    """
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = (dx ** 2 + dy ** 2) ** 0.5
    if length == 0:
        return None
    ux, uy = dx / length, dy / length
    # 左手法向(逆时针环下指向内侧);环是顺时针则取反
    nx, ny = -uy * ccw_sign, ux * ccw_sign

    a = (p1[0] - ux * reach, p1[1] - uy * reach)
    b = (p2[0] + ux * reach, p2[1] + uy * reach)
    a_off = (a[0] + nx * distance, a[1] + ny * distance)
    b_off = (b[0] + nx * distance, b[1] + ny * distance)
    a_far = (a_off[0] + nx * reach, a_off[1] + ny * reach)
    b_far = (b_off[0] + nx * reach, b_off[1] + ny * reach)
    return Polygon([a_off, b_off, b_far, a_far])


def compute_envelope(geometry, edge_roles):
    """地块 GeoJSON(4326)+ 每条边的角色 → EnvelopeResult。

    edge_roles[i] 对应外环第 i 个点到第 i+1 个点这条边(闭合环,首尾点相同)。
    角色数量必须等于边数,且都在 YARD_M 里 —— 否则返回 area_m2=0、geometry=None(调用方判空)。
    """
    ring = geometry["coordinates"][0]
    n_edges = len(ring) - 1
    if len(edge_roles) != n_edges:
        return EnvelopeResult(geometry=None, area_m2=0, edge_roles=edge_roles)
    if any(r not in YARD_M for r in edge_roles):
        return EnvelopeResult(geometry=None, area_m2=0, edge_roles=edge_roles)

    proj_ring = _project(ring)
    site = Polygon(proj_ring)
    if not site.is_valid or site.area == 0:
        return EnvelopeResult(geometry=None, area_m2=0, edge_roles=edge_roles)

    ccw_sign = 1 if site.exterior.is_ccw else -1
    reach = ((site.bounds[2] - site.bounds[0]) ** 2 +
             (site.bounds[3] - site.bounds[1]) ** 2) ** 0.5 * 2 + 10

    result = site
    for i in range(n_edges):
        hp = _halfplane(proj_ring[i], proj_ring[i + 1], YARD_M[edge_roles[i]], ccw_sign, reach)
        if hp is None:
            continue
        result = result.intersection(hp)
        if result.is_empty:
            return EnvelopeResult(geometry=None, area_m2=0, edge_roles=edge_roles)

    area_m2 = round(result.area, 1)
    # 反投影回 4326(逐环逐点转换,保留 Polygon/MultiPolygon 两种可能)
    if result.geom_type == "Polygon":
        ext = _unproject(list(result.exterior.coords))
        wgs_geom = mapping(Polygon(ext))
    else:  # MultiPolygon(退界后被切成不相连的几块)
        polys = [Polygon(_unproject(list(p.exterior.coords))) for p in result.geoms]
        wgs_geom = {"type": "MultiPolygon",
                    "coordinates": [mapping(p)["coordinates"] for p in polys]}

    return EnvelopeResult(geometry=wgs_geom, area_m2=area_m2, edge_roles=edge_roles)
