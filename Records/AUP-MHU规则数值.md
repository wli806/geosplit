# AUP — MHU 规则数值(权威数据,架构无关)

> 这是 Mixed Housing Urban (MHU) 分区的法定标准数值,**与代码架构无关**,V1/V2 通用。
> 来源:Operative AUP 第 H5 章 + ADM《Unitary Plan 101》Easy Guide v6 (2018);原文存 `refs/`。
> 数值/条款权威 = planner + 负责人;未确认项见 `待确认-planner问题.md`。
> 核对日:2026-06-20。机读副本见 `backend*/.../config/zones.json`。

## 已确认数值(MHU)

| 标准 | MHU 值 | 关键细节 | 条款 |
|---|---|---|---|
| 建筑高度 | 11m(+1m 屋顶) | 从 ground level(动土前现状地面)量 | H5.6.4 |
| HIRB(日照斜面) | 45° recession,自边界上方 **3m** | **仅侧界 + 后界,临街不算** | H5.6.5 |
| 建筑覆盖率 | **45%** of net site | footprint;含 >750mm 悬挑/檐、附属建筑;不含露天泳池/pergola/露天 deck | H5.6.10 |
| 不透水率 | **60%** of site | 屋顶+铺装+车道+压实;草地/花园/透水铺装/slatted deck 不算 | E(地表水) |
| 景观率 | **35%** of net site | **须含一半前院**;可含 <1.5m 宽小径;最多 25% 可为铺装(≤650mm)/<1m 高露天 deck | H5.6.11 |
| 退界 yards | 前 2.5 / 侧 1 / 后 1(m) | 90° 量;yard 内须无建筑 | H5.6.8 |
| **net site area** | 毛地 − road widening − entrance strip − **legal ROW − access site** | **车道/ROW 不进任一户分母**(UP101 p2) | E38.6.2 |
| OLS(地面) | ≥20㎡、每边≥4m | **不可朝南**;须从客厅/餐厅/厨房直接进出;**须与车道/回车分开**;须无建筑(pool/eaves/pergola/deck 例外) | H5.6.14 |
| OLS(楼上主客厅) | 2 房+ = 8㎡;1 房/studio = 5㎡ | | H5.6.14 |
| Outlook space | 主客厅 6×4;主卧 3×3;其它居室 1×1(m) | 从窗中心量;须无建筑遮挡;**不得与别户 outlook 重叠** | H5.6.12 |
| Daylight(未建模) | 同地块两栋间距 ≥ 相邻墙高一半 | UP101 p8 | — |
| 车辆进出 | 每 25m 临街宽 1 个 crossing;距邻地 2m;crossing 口 2.75–3m;户内车道最小 2.5m | 多户共享 ROW 我们用 3.5m(E27,待 planner) | E27 |
| 停车 | 部分 zone 不要求 on-site;部分要求每户 1 个 | 见 Transport 章 | E27 |

## E38 细分要点(urban subdivision)

- **最小净地块面积(空地细分,E38.8.2)**:MHU **300㎡** / MHS 400 / SH 600 / THAB 1200 / Large Lot 4000。
- **Site shape factor(E38.8.1.1)**:每个**空地**子地块须能容纳 **8m×15m** 矩形(THAB 15×20)。
- ⭐ **围绕现有开发的细分(subdivision around existing development,E38.6.1(c) + 活动表 A15/A34)**:**不必满足最小地块/shape factor,作 Restricted Discretionary (RD) consent**。→ 印证"先建后分"路径走得通,只是落到 RD consent。最小地块/shape factor 仅在**空地细分**时卡。
- 净地块面积不含 access/entrance strip(E38.6.2)。
- 每个 site 须有临街(legal road frontage)或经共有通道到路的 access。

## 产能预估启发式(非法定)

- `GFA_total ≈ net × 覆盖% × (1 + 上层系数)`;上层系数 urban 0.8 / suburban 0.7;层高 3.0m。
- ⚠️ 这是粗估;**真实上层缩小由 HIRB admissible(h) 精算**(V2 `domain/subdivision.py` 逐层算可建面积)。
