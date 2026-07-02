"""跨层数据契约:场地信息的数据形状(单一真相源)。纯 stdlib,domain/api 都依赖它。

铁律:这里只放【跨层】数据结构;模块内部私有类型就地定义,不进 contracts。
每个对外字段用 Field 包一层,带来源/取数时间/是否本地 → 前端可标注、可做新鲜度对比。
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class Field:
    """带溯源的值。value 可以是标量,也可以是下面的某个数据结构。"""
    value: Any
    source: str               # 来源,如 "LINZ Primary Parcels" / "council Rates24" / "经验默认"
    fetched_at: str = ""      # ISO 时间(UTC)
    is_local: bool = False    # 是否来自本地硬盘数据(E 盘等)


@dataclass
class ParcelData:
    geometry: Optional[dict]          # GeoJSON geometry(4326)
    area_m2: Optional[float]
    appellation: Optional[str]
    titles: Optional[str]


@dataclass
class ZoneData:
    zone: Optional[str]
    geometry: Optional[dict] = None


@dataclass
class ValuationData:
    """CV = rating valuation,非市场卖价。LCV/LLV 为最新一轮(2024 reval)。取不到 → "N/A"。"""
    cv: Any = "N/A"
    lv: Any = "N/A"
    latest_cv: Any = "N/A"
    latest_lv: Any = "N/A"
    valuation_date: Optional[str] = None
    latest_valuation_date: Optional[str] = None


@dataclass
class SchoolData:
    """命中的校区。边界为 indication,精度不高 → 前端标注"请向学校确认"。"""
    schools: list = field(default_factory=list)   # [{id, name, type, effective_date}]


@dataclass
class SiteModel:
    address: str
    lonlat: Optional[list]    # [lon, lat]
    parcel: Field             # Field(value=ParcelData)
    zone: Field               # Field(value=ZoneData)
    valuation: Field          # Field(value=ValuationData)
    schools: Field            # Field(value=SchoolData)

    def to_dict(self):
        return asdict(self)
