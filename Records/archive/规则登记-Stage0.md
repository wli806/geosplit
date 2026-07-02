# 规则登记(Rule Registry + Backlog)

> 每条合规/计算规则一条记录。做着一条想到另一条,就在这里加个 stub(状态=未来),不打断当前工作。
> **规则即数据**:引擎遍历这张表,加规则=加一行,引擎循环不改。
> 数值/条款以 **planner + 负责人** 为权威,未确认的标"待 planner"。

## 规则单元 schema
```
ID / 名称 / 来源章节·条款 / 适用条件(zone, activity, overlay) /
用到的数据字段(见数据字典) / 通过条件(公式) / 阈值 / 结论分级(✅/❌/⚠️) /
状态(待规划|进行中|完成|未来想法) / 备注
```

## 状态图例
🔵待规划 ｜ 🟡进行中 ｜ ✅完成 ｜ 💡未来想法

---

## MHU · fee simple · urban subdivision（MVP 目标范围）

| ID | 名称 | 来源(待核) | 用到的数据 | 状态 | 备注 |
|---|---|---|---|---|---|
| R-ELIG | 资格门(zone/overlay/物理门槛) | H5 / E38 | zone, overlays, area, frontage | 🔵 | 出 GO/FLAG/STOP |
| R-MINLOT | 最小净地块面积 | E38 | net area | 🔵 | **待 planner**:围开发情形是否不卡 |
| R-FRONT | 最小临街宽 / 形状可容建筑 | E38 | frontage, shape | 🔵 | 原型选择也用 |
| R-YARD | 退界(前/侧/后) | H5 | 边界, 朝向 | 🔵 | 角地分情况(见收集箱) |
| R-HIRB | 日照斜面 HIRB | H5 | 边界, DTM, 高度基准 | 🔵 | **待 planner**:ground level 怎么定;MVP 用距离限高近似 |
| R-HGT | 最大高度 | H5 | 高度基准 | 🔵 | |
| R-COV | 建筑覆盖率 | H5 | 包络面积 | 🔵 | |
| R-IMP | 不透水率 | E | 面积 | 🔵 | |
| R-OLS | 户外生活空间 | H5 | 户型模板(窗/客厅) | 🔵 | 与内部布局耦合→用参数化模板 |
| R-OUTLOOK | Outlook space | H5 | 户型模板(窗位) | 🔵 | 从居室窗投射,不与邻户重叠 |
| R-PARK | 停车 / 回车 | E27 | 户型, access | 🔵 | |
| R-ACCESS | Access/车道 宽度+坡度+长度上限 | E27 | DTM(坡度), 几何 | 🔵 | rear site 的 access leg |
| R-SW | 雨水接驳可行性 | E36 | 最近公共管+管底, 最低点 | 🔵 | 不行则⚠️需工程 |
| R-PATHWAY | subdivision-around-development 路径 | E38 | — | 🔵 | **待 planner** |

## ✅ 已确认数值（来源:ADM《Unitary Plan 101》Easy Guide v6 2018 + H5;核对日 2026-06-20）
> 这份 ADM 官方易读版印证了 zones.json 全部数值,作为权威来源存档(原文件 `F:\Chrome Download\UNITARY PLAN_101.pdf`)。

| 标准 | MHU 值 | 关键细节 |
|---|---|---|
| 建筑高度 | 11m(+1m 屋顶) | 从 ground level(动土前现状地面)量 |
| HIRB | 45° recession,自边界上方 **3m** | **仅侧界+后界,临街不算** |
| 建筑覆盖率 | **45%** of net site | footprint;含>750mm 悬挑/檐、附属建筑;不含露天泳池/pergola/露天 deck |
| 不透水 | **60%** of site | 屋顶+铺装+车道+压实;草地/花园/透水铺装/slatted deck 不算 |
| 景观 | **35%** of net site | **须含一半前院**;可含<1.5m 宽小径;最多 25% 可为铺装(≤650mm 砖)/<1m 高露天 deck |
| 退界 | 前 2.5 / 侧 1 / 后 1 | 90° 量;yard 内须无建筑 |
| **net site area** | 毛地 − road widening − entrance strip − **legal right of way − access site** | **车道/ROW 不进任一户分母**(p2) |
| OLS(地面) | ≥20㎡、每边≥4m | **不可朝南**;须从客厅/餐厅/厨房直接进出;**须与车道/回车分开**;须无建筑(pool/eaves/pergola/deck 例外) |
| OLS(楼上主客厅) | 2 房+ = 8㎡;1 房/studio = 5㎡ | |
| Outlook | 主客厅 6×4;主卧 3×3;其它居室 1×1 | 从窗中心量;须无建筑遮挡;**不得与别户 outlook 重叠** |
| **Daylight**(新,未建模) | 同地块两栋间距 ≥ 相邻墙高一半 | p8 |
| 车辆进出 | 每 25m 临街宽 1 个 crossing;距邻地 2m;crossing 口 2.75–3m;户内车道最小 2.5m | 我们用 3.5m(多户共享 ROW,E27,待 planner) |
| 停车 | 部分 zone 不要求 on-site;部分要求每户 1 个 | 见 Transport 章;MVP 先不做 |

**产能预估启发式(非法定)**:GFA_total ≈ net×覆盖% ×(1+上层系数);上层系数 urban 0.8 / suburban 0.7;层高 3.0m。真实上层缩小由 HIRB admissible(h) 精算。

## 分割原型目录（archetype catalog,供"生成"阶段 = 放置模板库)

| ID | 原型 | 适用场地特征 | 状态 |
|---|---|---|---|
| P-SIDE | 沿街并排分块 | 宽面窄进 | 🔵 |
| P-REAR | 前 1-2 块 + 后排带 ROW(rear site) | 窄面深进 | 🔵 |
| P-TERRACE | 私路 + 一排联排 | 又深又宽 | 🔵 |
| P-CORNER | 双临街 | 角地 | 💡 |

## 未来想法 / 待归类
- 💡 (示例) 不同 typology(2 层 vs 3 层)各算一套产能与利润场景做对比。
