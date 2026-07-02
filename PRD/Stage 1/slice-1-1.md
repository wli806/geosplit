# PRD — Stage 1 / Slice 1-1:场地基础信息总览(2D)

- 日期:2026-06-22 ｜ 状态:**草稿(待负责人确认 → 进入施工)**
- 架构总纲:`../../Records/V2-架构.md`;数据接口:`../../Records/Auckland-GIS-数据接口手册.md`;规则数值:`../../Records/AUP-MHU规则数值.md`
- 测试地块:11 Malmo Place, Massey(MHU,672㎡)

## 0. 一句话目标

输入奥克兰地址 → 在一张 **2D 地图(Leaflet)** 上,把**能查到的场地基础信息全部显示出来**,左侧 GeoMap 式图层列表可勾选,每项数据带**来源标注**。

这一刀是 V2 的**第一根竖切**:跑通 `sources → domain → render → api → frontend` 五层 + **建起 L3 图层注册表**(GeoMap 预览的核心)。**全程 2D,不碰 3D / 包络 / 产能 / 收支。**

## 1. 要显示的信息(= 本刀范围)

| 信息 | 类型 | 来源 | 呈现 |
|---|---|---|---|
| 地块红线 parcel | 矢量多边形 | LINZ Primary Parcels | 地图描边 + 信息面板(面积/legal/title) |
| **CV 估值** | 属性 | council `Rates24_SnapshotReval`(LCV/LLV 最新) | 信息面板(CV/LV/估值日期 + ⚠️非卖价) |
| 分区 zoning | 矢量多边形 | UnitaryPlanZones | 图层(着色 + 标签) |
| 洪水区域 flood | 矢量多边形 | CatchmentsAndHydrology | 图层(蓝色叠加) |
| **学校校区 school zone** | 矢量多边形 + 属性 | MoE `NZ_School_Zone_boundaries` | 信息面板(命中的学校列表)+ 可选校区多边形图层 |
| **等高线 contours** | 矢量线 | council `Contours2024` | 图层(细线 + 高程标注) |
| 航拍图 | 底图 | Esri World Imagery(免 key) | 底图切换(与街道底图二选一) |

> CV 与 school zone 不是纯图层,而是地块属性,显示在信息面板;其余为可勾选图层。
> ⚠️ school zone:边界为 indication,精度不高;面板标注"请向学校确认";0 命中 ≠ 附近无学校(见《接口手册》第 3 节)。
> **DEM/DSM 栅格成像不在 1-1**:2D 地形用等高线;DEM/DSM 面 + draping(地面贴中性底 / 表面贴航拍)挪到引入 Cesium 3D 的那刀。
> **底图来源(详见《接口手册》§3b)**:测试版街道底图用 Carto / LINZ topolite,航拍用 Esri / LINZ aerial(demo key);**正式版统一用 LINZ Basemaps**(街道 + 航拍都有,免费、CC BY 4.0 商用可,Developer key 邮件申请)。council 自有底图(Landbase / 0.075m 航拍,公开,授权待确认)可选叠加。底图源做成可配置。

## 1b. 未来信息图层目录(注册表预案)

> 把**以后要抓的所有信息**先登记在此,让 L3 图层注册表一开始就为它们设计好;**本刀只实装下面标 ✅ 的**,其余加一个 = 注册表填一行(矢量层走 `_arcgis` 通用取数,几乎零成本)。来源见《接口手册》。

**矢量信息图层(ArcGIS):**
| 图层 | 来源 | 状态 |
|---|---|---|
| 地块 parcel | LINZ Primary Parcels | ✅1-1 |
| 分区 zoning | UnitaryPlanZones | ✅1-1 |
| 洪水区域 flood | CatchmentsAndHydrology | ✅1-1 |
| 学校校区 school zone | MoE NZ_School_Zone_boundaries | ✅1-1 |
| 估值 CV/RV(属性) | Rates24_SnapshotReval | ✅1-1 |
| 雨水管网(管/井/雨水口/接驳) | LiveMaps/stormwater 子图层 0/3/5/16/18 | 未来 |
| 供排水容量约束 | LiveMaps/UndergroundServices | 未来 |
| 液化 / ASCIE / 滑坡 / 滑坡易发性 | GeologyandGeotechnical 子图层 | 未来 |
| 覆盖层/特征区/designation/precinct | UnitaryPlanManagementLayers | 未来 |
| 开发限制 | DevelopmentRestrictions | 未来 |
| 开发贡献费 DC | DevelopmentContributions | 未来(经济模块用) |
| 建筑轮廓 | LINZ Building Outlines | 未来 |
| 等高线 contours | council Contours2024 | ✅1-1 |
| 法定边界 | StatutoryBoundaries | 未来 |

**栅格成像图层(本地 raster):**
| 图层 | 来源 | 状态 |
|---|---|---|
| DEM 地形面 + draping(贴中性底) | 本地 1m DEM | 3D 刀 |
| DSM 表面 + draping(贴航拍) | 本地 1m DSM | 3D 刀 |
| nDSM 现状建筑/树高(DSM−DEM) | 本地两套栅格 | 未来 |
| 航拍底图 | Esri Imagery(✅1-1)/ LINZ 航拍(未来,需 key) | 部分 |

**属性/详情(面板,非图层):**
| 项 | 来源 | 状态 |
|---|---|---|
| 学校详情(地址/类型/网址等) | Education Counts datastore | 未来 |

## 1c. 数据存储与读取模型(两种,别混)

- **本地栅格(DEM/DSM)= 分块 tile**(说明用,**1-1 不读栅格,留给 3D 刀**):每个 `.tif` 是一张 1:1000 图幅(约 480m×720m,1m 像元),`.tfw` 记录其地理范围。读法:算 bbox(地块+50m)→ 找出**相交的 tile(可能 1~4 块)**→ 读出拼接 → 裁剪到 bbox。`raster.py` 一次性扫描所有 `.tfw` 建 tile→bbox 索引(缓存),之后按 bbox 命中。
- **远程矢量(地块/分区/洪水/学校/CV/管线…)= ArcGIS 要素服务,不分块**:整层在服务器,按点或 bbox **查询**,只回相交的要素(GeoJSON + 属性)。例:管线 = 按 bbox 查 stormwater → 回那几根管的线 + 管径/管底标高。`_arcgis.py` 封装这套查询。

## 2. 本刀建起的文件(对齐 `V2-架构.md` 目录树)

### contracts/(跨层数据契约 = 数据形状索引)
- `site.py`:
  - `Field{value, source, fetched_at, is_local}` —— 溯源包装,所有 source 字段都用它
  - `ParcelData{geometry, area_m2, appellation, titles}`
  - `ZoneData{zone, geometry}`
  - `ValuationData{cv, lv, latest_cv, latest_lv, valuation_date, latest_valuation_date}`
  - `SchoolData{schools:[{id, name, type, effective_date}]}`(命中的校区,带 indication 提示)
  - `SiteModel{address, lonlat, parcel, zone, valuation, schools}`(每个子字段为 `Field` 或带 `Field` 的结构)
- `layers.py`:
  - `LayerSpec{id, name, group, modes, ...}`(modes 本刀只有 `["2d"]`)
  - `LayerPayload2D{kind: "geojson"|"image", data|image_url, bounds, style}`

### sources/(L1:取数 + 缓存 + 溯源)
**通用工具:**
- `_arcgis.py`:通用 ArcGIS query(点/包围盒查;Esri JSON → GeoJSON;`f=json` 兜底)
- `_cache.py`:磁盘缓存(key 带数据版本;给 TTL)

**类型源(会映射到 contract 字段,各一文件):**
- `geocode.py`:地址 → 经纬度(**Nominatim**,可插拔,future 换 LINZ/council)
- `parcel.py`:LINZ 地块 → `ParcelData`
- `zone.py`:council 分区 → `ZoneData`
- `valuation.py`:council 估值 `Rates24_SnapshotReval`(LCV/LLV 最新;取不到→`"N/A"`)→ `ValuationData`
- `school.py`:MoE 校区(点 Intersects 命中学校)→ `SchoolData`

**展示叠加层(不建专属文件):** 洪水 `CatchmentsAndHydrology`、等高线 `Contours2024` —— 在 L3 注册表写配置 `{服务, 图层id, 样式}`,统一走 `_arcgis` 取原始 GeoJSON 展示。未来 GeoMap 图层(管线/地质…)同此,加一行即可。

> `raster.py`(读 E 盘 DEM/DSM 瓦片)**不在 1-1**,顺延到引入 Cesium 3D 的那刀(配 `domain/terrain`)。

### domain/(L2:纯计算)
- `site.py`:`assemble_site(address) → SiteModel`(调 geocode → parcel/zone/valuation/school,组装 + 填溯源)
> `terrain.py`(DEM/DSM → 地形面)**不在 1-1**,随 `raster.py` 顺延到 3D 那刀。

### render/(L3:领域结果 → 图层负载;★图层注册表)
- `layers.py`:
  - `LayerSpec` 注册表(parcel / zoning / flood / contours / school);展示叠加层在此写 `{服务,图层id,样式}` 配置
  - 每层的 2D 画法:矢量层 → GeoJSON + 样式(线/面/标注)

### api/(L4:瘦路由)
- `GET /site?address=` → SiteModel(含 parcel/zone/valuation + 溯源)
- `GET /layers` → 图层注册表清单(给前端建左侧列表)
- `GET /layers/{id}?bbox=` → 该层负载(GeoJSON 或 PNG+bounds)

### frontend/(L5:Leaflet 2D)
- `index.html` + `src/{api.js, map2d.js, layers.js, panels.js}`
- 地址输入 → 画地块、fit 视野
- **左侧图层列表**(读 `/layers`):勾选开关 + 底图切换(街道 / 航拍)
- **信息面板**:逐字段显示值**和来源标签**(LINZ / council / 经验 / 本地硬盘)

## 3. 施工顺序(刀内分步)

1. **骨架 + 核心信息**:contracts + sources(geocode/parcel/zone/valuation/school)+ domain/site + api(/site)+ 前端(地址输入、画地块、信息面板含 CV/学校 + 来源标注)。
2. **图层注册表 + 展示叠加层**:render/layers 注册表 + api(/layers,/layers/{id})+ 展示层(洪水、等高线)走 `_arcgis` 通用取数 + 前端图层列表(勾选)+ 航拍/街道底图切换。
3. **打磨**:样式、标注、确定性、缓存、残留检查。

## 4. 验收标准

1. 输入 11 Malmo → 地图显示地块红线;信息面板列出面积/legal/title/**CV(LCV)**,每项带来源标签。
2. 左侧列表能勾选:分区、洪水、等高线、学校校区;底图能在街道/航拍间切换。
3. 等高线正确叠在地块范围(细线 + 高程标注),随缩放清晰、不挡底图。
4. `/layers` 返回注册表,前端**完全由注册表驱动**建列表(加一层 = 注册表加一项,前端不改)。
5. 每个 source 返回值都带 `Field` 溯源;前端能显示来源。
6. 同地址同输出(确定性);取数有缓存。
7. 跑通残留检查清单(`V2-架构.md` 第 6 节)。

## 5. 明确不做(OUT)

Cesium 3D 与转场;**DEM/DSM 栅格成像与 draping(挪 3D 刀)**;HIRB 包络;产能/推荐分割;收支平衡;房屋 layout;管网/地质等更多图层(注册表已支持,后续逐个加);flood 的本地全量缓存(本刀按需即查,缓存策略后片);LINZ 航拍 key(先用 Esri Imagery)。

## 6. 决策(已定)

- **取数范围**:地块 bbox 外扩 **50m**。
- **CV 取不到**:写 **"N/A"**(不猜区域均值)。
- **geocode**:Nominatim 起步(公用 web API,有限流),接口可插拔,生产换 LINZ/council 官方地址服务。

## 6b. 已定:2D 地形 = 等高线

- 2D 地形用 **council Contours2024 等高线**(矢量,像 council;不挡底图;可标高程)。**不做** DEM/DSM 平面成像 / 灰度晕渲。
- DEM/DSM 栅格面 + draping(地面贴中性底 / 表面贴航拍)整体放到**引入 Cesium 3D 的那刀**;`raster.py` + `domain/terrain` 一并顺延。
- 等高线来源:1-1 用 council Contours2024(零栅格、最省);以后做 3D 若要与本地 DEM 完全一致,再改成本地 DEM 生成。
