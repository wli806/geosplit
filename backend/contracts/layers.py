"""跨层数据契约:图层注册表的数据形状。

LayerSpec = 一个可显示图层的声明(GeoMap 式列表的一项)。
modes 声明它支持哪些视图模式(本阶段只有 "2d";3D 引入后加 "3d")。
展示叠加层(洪水/等高线/未来管线…)= 在 render 注册表写一行 LayerSpec,走通用 _arcgis 取数。
"""
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class LayerSpec:
    id: str
    name: str
    group: str                 # 左侧列表按 group 分组
    modes: list                # ["2d"] / ["3d"] / ["2d","3d"]
    kind: str                  # "geojson"(矢量)| "basemap"(底图)
    source: dict = field(default_factory=dict)   # {service, layer_id, f}（arcgis 图层）
    style: dict = field(default_factory=dict)     # 前端样式

    def public(self):
        """给前端的清单项(不暴露内部 source 细节)。"""
        return {"id": self.id, "name": self.name, "group": self.group,
                "modes": self.modes, "kind": self.kind, "style": self.style}


@dataclass
class LayerPayload2D:
    id: str
    kind: str                  # "geojson"
    data: Any                  # GeoJSON FeatureCollection
    style: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
