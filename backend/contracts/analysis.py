"""跨层数据契约:退界包络(yard setback envelope)的数据形状。

铁律:这里只放【跨层】数据结构;模块内部私有类型就地定义,不进 contracts。
"""
from dataclasses import dataclass
from typing import Optional

EdgeRole = str   # "front" | "back" | "side"(枚举不强类型化,domain 层校验取值)


@dataclass
class EnvelopeResult:
    """退界后的可建范围。geometry 为 None 表示退界后无剩余空间(地块太窄/退界太深)。"""
    geometry: Optional[dict]     # 可建范围 GeoJSON(Polygon 或 MultiPolygon,4326)
    area_m2: float                # 无剩余空间时为 0
    edge_roles: list              # 原样带回用到的角色数组,前端核对用
