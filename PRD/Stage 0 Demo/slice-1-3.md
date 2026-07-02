# PRD — Slice 1-3:Scheme 选择与拓扑模板求解架构

- 日期:2026-06-21 ｜ 状态:**算法草稿(待负责人确认后进入施工 PRD)**
- 架构总纲:`../../Records/项目进展与决策.md`(第 8 节);上一片见 `slice-1-2c.md`。
- 测试地块:11 Malmo Place, Massey;优先验证 `front lot + short-edge frontage + side driveway row + narrow unit`。

## 0. 一句话目标

把现有的 `lot -> driveway -> sublots -> platforms -> HIRB envelope` 引擎,升级成可以生成多个可行布局方案的 **facts + strategy registry + scheme/layout 两层策略** 架构。

本 slice 先不追求从任意地块自动创造最优设计,而是建立一套可扩展的"已知开发套路匹配系统":

```
地块公开约束 SiteFacts
  -> 命中多个 SchemeStrategy
  -> 每个 Scheme 生成 development cells / driveway / orientation tags
  -> 兼容的 LayoutStrategy 填 OLS / footprint / outlook
  -> 统一 Checks 校验
  -> 输出 4-5 个可用或 near-valid 通解
```

核心产品目标是 **多给可用解**,不是寻找数学意义上的全局最优解。

---

## A. 背景与当前状态

当前代码已经完成:

- 地址取数、地块边界、zone、面积。
- 沿真实长边选 left/right 车道,切出恒定 3.5m accessway。
- 沿长轴按 N 分 development/subdivision segments。
- 对每段按边退界,得到可用建筑范围 `platforms`。
- 基于地形和 HIRB 生成 3D 可建包络,并保存 `ctx.envelope_planes`。

当前抽象仍偏向:

```
先分地 -> 每块退界 -> 看最大可建范围
```

下一步不能简单变成"在平台里放一个房子矩形"。真实 layout 里,房子、OLS、outlook、停车、车道、景观是互相抢空间的一组对象。尤其:

- OLS 是 required void,不是房子放完以后剩下的空地。
- Outlook space 是从窗位派生的 required void,不能随便压到邻地或别户 required space。
- subdivision lot line 往往应在建筑/OLS/车道关系明确后再整理,不应过早把 legal lot 切死。

因此下一阶段的核心对象应从 `sublot` 升级为 `development cell` 和 `UnitCell`。

---

## B. 关键设计结论

### B1. 不采用二叉树式方案选择

不建议把方案选择写成:

```
if short_edge_frontage:
  if east_high_west_low:
    if neighbour_driveway_left:
      use A
```

原因:

- 条件不是严格互斥。一个地块可以同时具备短边临街、邻居车道、公园边、横坡、北向好等多个特征。
- 很多条件只是同一策略的参数,不是新策略。例如 east high/west low 与 west high/east low 可能只是 `driveway_side = low_side` 的镜像。
- 树结构顺序太强,后续会产生大量重复分支。
- 产品目标是输出多个候选方案,不是只命中唯一叶子节点。

### B2. 采用 SiteFacts + Strategy Registry

先把地块分析成公共事实 `SiteFacts`,所有策略读取同一套 facts,各自判断适用性并打分。

```
facts = classify_site(ctx)

for strategy in scheme_strategies:
    if strategy.applicable(facts):
        candidate = strategy.generate(ctx, facts)
        candidate.score = strategy.score(ctx, facts)

return top candidates
```

同一块地可以命中多个策略:

- `SideDrivewayRowNarrow`
- `FrontBackDuplex`
- `StreetFacingTerrace`
- `CentralDrivewayPair`
- `CornerDualFrontage`
- `RearCourtCluster`

MVP 只实现第一个,但 registry 和数据结构要从第一天支持多策略。

### B3. SchemeStrategy 与 LayoutStrategy 分两层

两层策略可以组合,但不能任意乱接。必须通过清楚的输入输出合同衔接。

```
SchemeStrategy:
  决定车道、户数、development cells、每个 cell 的 access/private/living edge tags。

LayoutStrategy:
  在每个 cell 里放 OLS、building footprint、outlook、parking/garage、entry。
```

不是所有 layout 都能接所有 scheme。通过 `cell_type` 和几何条件判断兼容性。

例如:

```
SideDrivewayRowScheme
  -> cell_type = narrow_row_cell
  -> access_edge = driveway side
  -> private_edge = opposite side

NarrowRowMinimumOLSLayout
  accepts narrow_row_cell
  requires clear_width between 4.0m and 6.0m
```

以后宽地块可以输出 `wide_cell`,由另一个 layout strategy 处理。

---

## C. SiteFacts: 地块公开约束

`SiteFacts` 是所有策略共享的公共语言。分类时尽量保留数值,不要过早只变成枚举。

### C1. Frontage / Access

```
frontage_type:
  short_edge_frontage
  long_edge_frontage
  corner_site
  rear_site / battleaxe

frontage_width_m
road_edges[]
possible_driveway_edges[]
existing_crossing, optional
neighbour_driveway_edges[]
```

说明:

- `rear_site / battleaxe` 在 v1 标记为 future branch,暂不生成方案。
- 邻居车道可作为 access/privacy/visual openness 的软加分,但不能默认当作合法 outlook space。

### C2. Shape

```
area_m2
frontage_width_m
average_depth_m
depth_width_ratio
regularity_score
taper_direction
long_axis_angle
short_axis_angle
```

典型标签:

```
long_narrow
wide_shallow
regular_rectangle
wedge / irregular
```

标签供快速筛选,数值供策略精确判断。

### C3. Slope / Terrain

```
average_gradient
max_gradient
high_edge
low_edge
fall_direction_relative_to_street
crossfall_direction
ols_slope_ok_edges[]
driveway_slope_score_by_edge
```

策略使用方式:

- 车道优先靠低侧或土方较小侧。
- 太陡的地块先输出 `requires_manual_assessment` 或命中 future split-level strategy。
- OLS 需要可用、较平、可直接从 living/kitchen/dining 到达。

### C4. Orientation / Sun

```
north_vector
northish_edges[]
south_edges[]
best_ols_edges[]
living_orientation_preferences[]
```

说明:

- OLS 优先 north / northwest / private side。
- 如果当前策略导致 OLS forced south-facing,则策略降分或 fail。

### C5. Edge Context

```
edge_context:
  road
  residential_neighbour
  neighbour_driveway
  public_open_space
  school / reserve
  stream / no-build
```

说明:

- public street / public open space 可作为 outlook 的潜在借用空间。
- 邻接大型公共开放空间或商业等是否影响 HIRB,以后按正式规则接入;v1 不自动放宽,只记录 bonus / planner flag。

### C6. Planning

```
zone
max_building_coverage_pct
max_impervious_pct
min_landscaped_pct
yards_m
hirb_edges
max_height_m
outdoor_living_space rules
outlook rules
```

来源仍由 `zones.json` 和规则登记维护。

---

## D. Strategy 分类

### D1. SchemeStrategy

SchemeStrategy 负责大布局,输出 development-level 几何。

职责:

- 选择户数范围。
- 选择 driveway side / access pattern。
- 生成 development cells。
- 给每个 cell 标注 access/private/living candidate edges。
- 给后续 layout strategy 留出清楚输入。

输出合同:

```
SchemeCandidate:
  id
  strategy_id
  params
  score_precheck
  reasons[]
  driveway_polygon
  cells[]
  assumptions[]
  warnings[]

Cell:
  idx
  cell_type
  polygon
  platform_polygon, optional later
  access_edge
  private_edge
  preferred_living_edge
  possible_ols_edges[]
  possible_outlook_edges[]
  possible_parking_edges[]
  clear_width_m
  clear_depth_m
```

首批 SchemeStrategy:

| ID | 名称 | 状态 | 说明 |
|---|---|---|---|
| `side_driveway_row_narrow` | 窄户 side driveway row | v1 实装 | 11 Malmo 优先路线 |
| `front_back_pair` | 前后排/duplex | future | 短边临街但宽度/深度不同 |
| `street_facing_terrace` | 长边临街联排 | future | long-edge frontage |
| `central_driveway_pair` | 中央车道两侧排布 | future | 较宽地块 |
| `corner_dual_frontage` | 角地双临街 | future | corner site |
| `rear_site_battleaxe` | 后座地 | future/manual | 先标记,不做 |

### D2. LayoutStrategy

LayoutStrategy 负责每个 dwelling cell 内部的 compound blocks。

职责:

- 放 OLS。
- 放 building footprint。
- 定 living edge。
- 派生 outlook spaces。
- 放 parking/garage/entry。
- 计算 residual landscape / impervious。

输出合同:

```
UnitLayout:
  cell_idx
  layout_strategy_id
  building_footprint
  outdoor_living_space
  living_edge
  living_outlook
  bedroom_outlooks[]
  parking_or_garage
  entry_path
  residual_landscape
  metrics
  failures[]
  warnings[]
```

首批 LayoutStrategy:

| ID | 名称 | 状态 | 说明 |
|---|---|---|---|
| `narrow_row_minimum_ols` | 窄户 minimum OLS 布局 | v1 实装 | 只处理 clear width 4-6m |
| `wide_cell_split_space` | 宽户分区布局 | future | >6m 宽不强行用窄户逻辑 |
| `front_yard_ols` | 前院 OLS | future | 仅无更好选择时 |
| `courtyard_ols` | 内院 OLS | future | cluster/terrace |

### D3. Check

Check 仍维持现有原则:只读、无序、纯谓词。

首批 layout 相关 checks:

```
R-OLS:
  area >= 20m2
  min dimension >= 4m
  direct access from living/kitchen/dining
  separate from driveway / turning bay
  slope ok
  not south-facing, or planner flag

R-OUTLOOK:
  living 6x4
  principal bedroom 3x3
  other habitable 1x1
  no building obstruction
  no overlap with other dwelling required outlook/OLS
  does not project into adjacent private site unless rule permits

R-HIRB-FIT:
  building footprint at modeled height fits envelope_planes

R-COV / R-IMP / R-LAND:
  coverage, impervious, landscaped area
```

---

## E. SideDrivewayRowNarrow v1

### E1. 适用条件

`side_driveway_row_narrow` 是第一条要打通的路线。

适用:

```
frontage_type = short_edge_frontage
not corner_site
not rear_site
depth_width_ratio >= 1.8
side driveway possible on left or right
development cell clear width between 4.0m and 6.0m
private/OLS side not obviously unusable
slope not beyond v1 threshold
zone = MHU, for MVP
```

不适用:

```
unit clear width < 4.0m
unit clear width > 6.0m
long-edge frontage
corner site
rear/battleaxe site
steep or complex slope requiring split-level logic
OLS forced south-facing with no alternative
```

重要边界:

- 如果 cell 宽度大于 6m,不要自动给更大的 OLS。
- 宽 cell 应交给另一个 future strategy,例如 `wide_cell_split_space`。
- v1 是"反推模板":先定义一个已知可用窄户解法,再判断地块是否能套住它。

### E2. Scheme 生成

候选:

```
n = 3, 4, 5, 6
driveway_side = left / right
parking_mode = garage / parking_pad / none, optional
storeys = 2, optional 3 later
```

预筛:

```
cell_clear_width in [4.0, 6.0]
cell_clear_depth enough for building + OLS
driveway side feasible
OLS side feasible
```

对于 11 Malmo,已知当前 N=4 时每户 platform 约:

```
clear width: about 7.7m platform x-direction currently,
platform depth: about 12.1-12.5m from driveway to far side
```

注意:这里的 "clear width" 在具体实现时必须统一定义:

- 若 unit 沿 x 方向切分,`cell_clear_width` = 每户沿街/沿长轴的宽度。
- `cell_clear_depth` = 从 driveway 内侧到 private edge 的深度。
- OLS 的 width/depth 应按该 cell 的 local access-private 坐标系计算,不要直接套全局 x/y 名字。

### E3. Unit 内部固定空间关系

Side driveway row 的 v1 空间关系:

```
driveway | garage/entry | building body | OLS/private yard
```

每户 edge tags:

```
access_edge = driveway side
private_edge = opposite side
preferred_living_edge = private_edge
parking_edge = access_edge
OLS edge = private_edge
living_outlook = from living edge outward, preferably over OLS
```

---

## F. NarrowRowMinimumOLS 算法

### F1. OLS 是 minimum viable OLS

本系统是开发 feasibility / yield generator,不是景观最大化工具。

原则:

```
满足最低合规要求
尽量保留可售建筑面积
生成多个合规通解
```

因此 OLS 不应因为地块宽就自动变大。对于 v1 窄户模板:

```
if clear_width < 4.0m:
  fail

if clear_width > 6.0m:
  current layout strategy not applicable
  pass to future wide-cell strategy

ols_width = min(clear_width, 5.0m)
ols_depth = max(4.0m, 20m2 / ols_width)

require:
  ols_width >= 4.0m
  ols_depth >= 4.0m
  ols_area >= 20m2
```

候选尺寸:

```
4.0 x 5.0 = 20m2
4.5 x 4.5 = 20.25m2
5.0 x 4.0 = 20m2
```

选择逻辑:

```
4.0m <= clear_width < 4.4m:
  use 4.0 x 5.0

4.4m <= clear_width < 5.2m:
  use clear_width x max(4.0, 20 / clear_width)

5.2m <= clear_width <= 6.0m:
  use 5.0 x 4.0 or a 5.0m-wide slice within the cell
```

### F2. OLS 放置优先级

```
1. private edge, if also north/northwest-ish
2. private edge even if neutral orientation
3. rear/courtyard edge
4. front edge only if no better option
5. south-facing -> fail or low-score planner flag
```

Side driveway row v1 默认:

```
OLS placed against private_edge
OLS outside driveway/turning
OLS directly adjacent to living facade
```

### F3. Building footprint 放置

OLS 放完后,剩余区域再放 building footprint。

顺序:

```
1. admissible = platform ∩ HIRB height-fit polygon
2. reserved_voids = OLS + driveway + turning/parking exclusion
3. buildable_for_footprint = admissible - reserved_voids
4. choose footprint size from unit type
5. place footprint between access_edge and OLS
6. living facade touches OLS side
7. garage/entry facade touches access side, if parking mode requires
```

v1 unit type 可先用简单参数:

```
unit_type = compact_2bed / compact_3bed / 3bed_garage
storeys = 2
target_gfa_m2
target_footprint_m2 = target_gfa / storeys
```

暂不做完整房间平面,只要求 living edge 和 bedroom outlook 有合理 facade candidate。

### F4. Outlook 派生

Outlook 不作为先验最大化目标,但必须生成 required rectangles 做校验。

```
living_outlook:
  6m depth x 4m width
  projected from living facade
  prefer overlap with OLS / public street / public open space

principal_bedroom_outlook:
  3m x 3m

other_habitable_outlook:
  1m x 1m
```

v1 可以先精算 living outlook,bedroom outlook 以 `warning / future detailed room layout` 标注,但数据结构要预留。

---

## G. Pipeline 建议

在现有 pipeline 上增加两个概念层:

```
0. Site
   fetch site, terrain, zone

1. Classify
   classify_site(ctx) -> ctx.site_facts

2. Scheme Generate
   strategy registry -> ctx.scheme_candidates

3. For each SchemeCandidate:
   arrange driveway/cells
   calculate platforms
   calculate HIRB envelope
   run compatible layout strategy
   run checks
   score

4. Return top N schemes
```

由于现有代码现在是单 `Context` 跑到底,施工时可分两步演进:

### Step 1: 单方案结构化

先新增字段:

```
ctx.site_facts
ctx.scheme
ctx.cells
ctx.unit_layouts
```

仍只跑一个 selected scheme,前端只显示一个结果。

### Step 2: 多方案 runner

再引入:

```
SchemeRunner
run_many(site, params) -> SchemeResult[]
```

每个 scheme 拥有自己的 Context clone,避免候选之间互相污染。

---

## H. 数据结构草案

```python
SiteFacts = {
    "frontage_type": "short_edge_frontage",
    "shape": {
        "area_m2": 672.0,
        "frontage_width_m": 16.8,
        "average_depth_m": 40.0,
        "depth_width_ratio": 2.38,
        "regularity_score": 0.9,
    },
    "slope": {
        "average_gradient": 0.03,
        "high_edge": "west",
        "low_edge": "east",
        "fall_direction_relative_to_street": "crossfall",
    },
    "orientation": {
        "northish_edges": ["..."],
        "best_ols_edges": ["private_edge"],
    },
    "edge_context": {
        "road_edges": ["front"],
        "neighbour_driveway_edges": ["right"],
        "public_open_space_edges": [],
    },
}
```

```python
SchemeCandidate = {
    "id": "side_driveway_row_narrow:right:n4",
    "strategy_id": "side_driveway_row_narrow",
    "params": {"n": 4, "driveway_side": "right", "storeys": 2},
    "score_precheck": 72,
    "reasons": ["short-edge frontage", "long narrow parcel", "cell width in range"],
    "warnings": [],
    "cells": [...],
}
```

```python
UnitLayout = {
    "cell_idx": 1,
    "layout_strategy_id": "narrow_row_minimum_ols",
    "building_footprint": "...polygon...",
    "outdoor_living_space": "...polygon...",
    "living_outlook": "...polygon...",
    "parking_or_garage": "...polygon or null...",
    "metrics": {
        "ols_area_m2": 20.0,
        "footprint_area_m2": 58.0,
        "gfa_m2": 116.0,
    },
    "failures": [],
    "warnings": [],
}
```

---

## I. Scoring 原则

评分只用于排序,不能替代硬校验。

硬 fail:

```
building outside admissible area
OLS < 20m2 or min dimension < 4m
OLS overlaps driveway/turning
coverage exceeds limit
impervious exceeds limit
landscape below limit
living outlook impossible
driveway impossible
```

软评分:

```
more valid dwellings
higher total GFA
minimum OLS achieved with less wasted area
OLS north/private orientation
driveway on low side / less earthwork
neighbour driveway alignment
regular building footprint
lower planning risk
```

输出要保留解释:

```
why_selected[]
why_rejected[]
near_misses[]
```

---

## J. 本 slice IN / OUT

### IN

- 明确 SiteFacts 分类体系。
- 明确 Strategy Registry 架构。
- 明确 SchemeStrategy / LayoutStrategy 的职责和合同。
- 明确 v1 要打通的路线:

```
side_driveway_row_narrow
  + narrow_row_minimum_ols
```

- 明确 OLS minimum viable 算法。
- 明确后续施工的数据结构和 pipeline 插入点。

### OUT

- 不实现所有模板。
- 不做 rear site / corner site / long-edge frontage。
- 不做宽户型 >6m 的复杂布局。
- 不做完整户内 room-level floor plan。
- 不做正式 swept path。
- 不做 HIRB relaxation for public open space 的自动规则,仅预留 facts。
- 不做多方案前端 UI,仅后端结构先支持。

---

## K. 验收标准

施工后的 slice 1-3 至少应达到:

1. 输入 11 Malmo Place,系统能生成 `SiteFacts`,并在调试输出中解释 frontage/shape/slope/access 判断。
2. Strategy registry 能返回至少一个 `SchemeCandidate`: `side_driveway_row_narrow`。
3. 对 N=4 或 N=5,能生成 cells,并给每个 cell 标注 access/private/living candidate edges。
4. `narrow_row_minimum_ols` 能为每个可兼容 cell 放置 minimum OLS。
5. 生成 building footprint 初版,并输出 2D 图层:
   - `footprints`
   - `outdoor_living`
   - `living_outlook`
   - `cells`
6. 如果 cell 宽度 `<4m` 或 `>6m`,该 layout strategy 明确返回 not applicable,而不是硬塞。
7. 输出 scheme-level reasons/warnings/failures,用于后续前端展示。

---

## L. 待确认问题

1. `cell_clear_width` 在 side driveway row 中的正式定义:沿长轴分户宽度,还是垂直车道方向的 usable depth?实现前必须统一命名为 `cell_frontage_width` / `cell_depth_from_access`。
2. OLS "不可 south-facing" 在合规判定中是硬 fail 还是 warning?需 planner/设计师确认。
3. Living outlook 是否 v1 必须完全精算,还是先精算 principal living,bedroom outlook 作为 warning。
4. 车库/车位在 MHU v1 是否作为必需项,还是按 `parking_mode` 生成多个 scheme。
5. Public open space / school / reserve edge 对 HIRB 和 outlook 的精确适用规则,后续需按 AUP 正文和 planner 确认。

