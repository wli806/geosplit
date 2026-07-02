# 奥克兰地块可行性 — GIS 公开数据接口手册

> 用途:记录所有已验证可用的公开数据接口、查询方法、解码方式。
> 下次会话直接读这份文档即可恢复全部上下文。
> 最后验证日期:2026-06-16(以 31 Malmo Place, Massey 实测）

---

## 0. 一句话原理

奥克兰 Council 的 **GeoMaps 网页底层就是 Esri ArcGIS REST 服务**。
网页上能看到的图层 = 背后一定有一个 `.../MapServer` 或 `.../FeatureServer` 接口。
返回的是**标准 JSON / GeoJSON**(不是加密格式),用任何语言 `JSON.parse` 即可。
不需要 relab —— relab 的分区、Watercare 约束等数据就是从这些同样的公开源抓的。

---

## 1. 两台核心服务器

### A. 奥克兰 Council
```
根目录: https://mapspublic.aklc.govt.nz/arcgis/rest/services
```
有多个 ArcGIS 实例,数据分布在不同实例:
- `arcgis`  —— 主实例,最全(LiveMaps、Contours、Applications…)
- `arcgis2` —— LiveMaps2 等
- `arcgis3` —— NonCouncil(UnitaryPlanZones / UnitaryPlanManagementLayers）
- ⚠️ `arcgis3/.../OpenData` 文件夹**需要 token**(返回 499 Token Required），不要用，改用上面的等价图层。

### B. LINZ（土地信息局，地块/产权权威源）
```
根目录: https://services.arcgis.com/xdsHIIxuCWByZiCB/arcgis/rest/services
```

---

## 2. 怎么"发现"一个图层的接口（核心方法）

### 步骤 1：列出某个文件夹下的所有服务
在任意服务目录 URL 后加 `?f=json`：
```
https://mapspublic.aklc.govt.nz/arcgis/rest/services/LiveMaps?f=json
```
返回的 `services[]` 数组里每个 `{name, type}` 就是一个服务。

### 步骤 2：列出某个服务下的所有子图层（sublayers）
在服务 URL 后加 `?f=json`：
```
https://mapspublic.aklc.govt.nz/arcgis/rest/services/LiveMaps/GeologyandGeotechnical/MapServer?f=json
```
返回的 `layers[]` 里每个 `{id, name, minScale}` 就是网页上你看到的那些勾选项（如 Landslides、Liquefaction）。
**关键字段 `minScale`**：>0 表示只有放大到一定比例才在地图上渲染 —— 但**查询接口不受它限制**（见下）。

### 步骤 3：查询数据
两种方式：

**(a) `query` —— 推荐，最可靠，无视 minScale**
按点查（这块地命中什么）：
```
.../MapServer/<图层id>/query
   ?geometry=<lon>,<lat>
   &geometryType=esriGeometryPoint
   &inSR=4326
   &spatialRel=esriSpatialRelIntersects
   &outFields=*
   &returnGeometry=true&outSR=4326
   &f=json     (或 f=geojson 直接拿 GeoJSON)
```
按范围查（附近所有管线等），把 geometry 换成包围盒：
```
   &geometry=<minLon>,<minLat>,<maxLon>,<maxLat>
   &geometryType=esriGeometryEnvelope
```

**(b) `identify` —— 一次查整个服务所有图层，但受 minScale/比例尺约束、服务器慢易超时**
```
.../MapServer/identify
   ?geometry=<lon>,<lat>&geometryType=esriGeometryPoint&sr=4326
   &tolerance=5&mapExtent=<minLon,minLat,maxLon,maxLat>
   &imageDisplay=800,600,96&layers=all&returnGeometry=false&f=json
```
> 教训：第一次查雨水管用 identify 返回 0，因为管线图层设了 minScale；改用 `query` 立刻拿到 26 根管。
> **能用 query 就别用 identify。**

---

## 3. 已验证可用的图层目录

### Council — `arcgis/rest/services/LiveMaps/` （MapServer，网页主数据）
| 服务名 | 内容 |
|---|---|
| `stormwater` | 雨水管网（见下方子图层）|
| `UndergroundServices` | Watercare 供排水**容量约束区** |
| `GeologyandGeotechnical` | 地质岩土（见下方子图层）|
| `CatchmentsAndHydrology` | 集水区 / 水文 / 洪水 |
| `PropertyInformation` | 物业信息 |
| `DevelopmentRestrictions` | 开发限制 |
| `DevelopmentContributions` | 开发贡献费 |
| `Planning` | 规划 |
| `ClimateImpact` / `Predicted_Urban_Heat_Island_Effect` | 气候 / 热岛 |
| `StatutoryBoundaries` / `AucklandCouncilBoundaries` | 法定边界 |

### Council — `arcgis/rest/services/` 根级（MapServer）
| 服务名 | 内容 |
|---|---|
| `Contours2024` / `Contours2016NZVD2016` / `Contours` | **等高线 / 地形（坡度）** |
| `Landbase` | 地形底图 |
| `Address` | 地址 |

### Council — Revaluation 2024（ArcGIS Online，CV/RV）

官方 Revaluation 2024 web map:
```
https://www.arcgis.com/home/item.html?id=7dd3170e715d44eebc9fb9f369d91e27
```

底层可 query 的估值图层:
```
https://services1.arcgis.com/n4yPwebTjJCmXB6W/arcgis/rest/services/AGOL_RateAccountInfo1_gdb/FeatureServer/0
```

用途：按点/地块查 Auckland Council rating valuation（CV/RV），包含地址、legal description、title、rate account、capital value、land value。

重点字段:
| 字段 | 含义 |
|---|---|
| `FORMATTEDADDRESS` | Council 格式化地址 |
| `LEGAL` | 法定描述 |
| `CT` | Record of Title |
| `RATEACCOUNTNUM` | Rate account number |
| `VALUATIONREF` | Valuation number |
| `CV` / `LV` | 2024/25 rates 使用的 Capital Value / Land Value（样例为 2021-06-01 估值）|
| `VALUATIONDATE` | `CV` / `LV` 的估值日期 |
| `LCV` / `LLV` | 最新 Capital Value / Land Value（2024 revaluation）|
| `LATESTVALUATIONDATE` | 最新估值日期（2024 revaluation 为 2024-05-01）|
| `AREALABEL` | 土地面积文本 |

注意：
- 2025-06-10 公开的 Auckland 2024 revaluation 基准日是 **2024-05-01**，用于 2025/26 rates。
- 系统里要把 `LCV` / `LLV` 当作当前最新 CV/RV；`CV` / `LV` 是上一轮 rates 当前值/2024-25 rates 值。
- 这个图层返回 polygon，可直接用地块中心点或地址点 `Intersects` 查询。
- ⚠️ **CV 是 rating valuation(批量估值),不是市场成交价**。收支平衡里只能当"参考锚点",售价应另用市场 $/㎡ 或 CV×市场系数(用户可调),别把 CV 当卖价。
- ⚠️ **商用授权待确认**:数据按地块是公开的,但嵌进"收费产品"是否被 council/AGOL 的 open-data 许可覆盖,需向 council 确认一次(已实测 2026-06-22:服务名 `Rates24_SnapshotReval`,可用)。

### Council — `arcgis3/rest/services/NonCouncil/` （MapServer，Unitary Plan）
| 服务名 | 内容 |
|---|---|
| `UnitaryPlanZones` | **基础分区 Zone**（如 Mixed Housing Urban）|
| `UnitaryPlanManagementLayers` | 覆盖层 Overlays / Precincts / Designations |
| `UnitaryPlanAppealsandModifications` | 上诉与修改 |
| `LAWA` / `LINZBuildingConsent` | 水质 / 建筑许可 |

### `stormwater` 服务子图层（重点）
| id | 名称 |
|---|---|
| 0 | Stormwater Network |
| 3 | Stormwater Manhole And Chamber（检查井）|
| 5 | Stormwater Catchpit（雨水口）|
| **16** | **Stormwater Pipe（管道，带管径/管底标高/材质/安装年份）** |
| 18 | Stormwater Connection（接驳）|
| 16/24 | 管道 / 废弃管道 |

### `GeologyandGeotechnical` 服务子图层（重点）
| id | 名称 |
|---|---|
| 0 | Areas Susceptible to Coastal Instability and Erosion (ASCIE) |
| 6/7/8 | Liquefaction Vulnerability（液化易发性，A/B 级评估）|
| 9 | Geological Maps（栅格，不支持属性 query）|
| 16-19 | GNS 地质单元 / 地质图 1:50k / 1:250k |
| 20 | Landslides（滑坡）|
| 24/25/26 | Landslide Inventory 点/线/面 |
| 21/22/23 | 滑坡易发性 2025（浅层/大型）|

### LINZ — `services.arcgis.com/xdsHIIxuCWByZiCB/.../`（FeatureServer）
| 服务名/图层 | 内容 |
|---|---|
| `LINZ_NZ_Primary_Parcels/FeatureServer/0` | **地块**：appellation（法定描述）、titles、survey_area（面积 m²）、几何边界 |
| `LINZ_NZ_Property_Titles/FeatureServer/0` | **产权**：title_no、type（Freehold 等）、estate_description |
| `LINZ_NZ_Property_Boundaries` / `LINZ_NZ_Building_Outlines` / `LINZ_NZ_Addresses` | 物业边界 / 建筑轮廓 / 地址 |

### Ministry of Education / Education Counts — School enrolment zones

公开 ArcGIS FeatureServer:
```
https://services.arcgis.com/XTtANUDT8Va4DLwI/arcgis/rest/services/NZ_School_Zone_boundaries/FeatureServer/0
```

用途：按地址点/地块中心点查询命中的 school enrolment home zones。

重点字段:
| 字段 | 含义 |
|---|---|
| `School_ID` | MoE school id |
| `School_name` | 学校名称 |
| `Institution_type` | 学校类型，如 Full Primary / Secondary / Contributing |
| `Office` | MoE regional office |
| `Approval_date` | zone approval date，Unix ms |
| `Effective_date` | zone effective date，Unix ms |

补充学校详情 API（Education Counts / data.govt.nz DataStore）:
```
https://catalogue.data.govt.nz/api/3/action/datastore_search_sql
resource id: 4b292323-9fcc-41f8-814b-3c7b19cf14b3
```

可按 `School_Id` 补学校地址、电话、网址、authority、co-ed status、经纬度等。

注意：
- Education Counts 明确说明：地图边界与正式文字描述冲突时，以 written description 为准；入学确认应联系学校。
- 官方下载的 MapInfo home zone polygons 精度不高，说明不应用于与 DCDB 等高精度边界做严格空间叠加。产品里应标为“school zone indication / 请向学校确认”。
- 不是所有学校都有 enrolment zone；点查询 0 命中不代表附近没有学校，只代表没有命中 home zone polygon。

---

## 3b. 底图与影像源(basemap / 航拍)—— 2026-06-22 研究+实测

> 网页地图的底图(街道/地形)与航拍影像从哪来,**测试版 vs 正式版**分列。
> ⭐ 关键结论:**LINZ Basemaps 一家同时提供街道底图 + 航拍,免费、CC BY 4.0 可商用** → NZ 商业产品基本不需要 Carto/Mapbox/Esri 付费底图。

### 推荐:LINZ Basemaps(街道 + 航拍,正式版首选)
- **同时有**:矢量地形底图(`topographic` / `topolite` / `labels`)+ 航拍栅格(`aerial`,奥克兰城区 ~0.075m)。
- 端点(栅格 XYZ):
  ```
  https://basemaps.linz.govt.nz/v1/tiles/{tileset}/{tileMatrixSet}/{z}/{x}/{y}.{webp|png|jpeg}?api={key}
  例: .../tiles/aerial/WebMercatorQuad/{z}/{x}/{y}.webp?api={key}
  ```
  矢量样式 JSON:`.../v1/styles/{style}.json?api={key}`;WMTS:`.../v1/tiles/{tileset}/{tileMatrixSet}/WMTSCapabilities.xml?api={key}`
  tileMatrixSet:`WebMercatorQuad`(EPSG:3857,给 Leaflet/Cesium/deck.gl)或 `NZTM2000Quad`(2193)。
- **Key**:Standard Access 免注册(限 1000 瓦片/分、100万/月,够开发);正式版用**免费 Developer key**(site 限定、合理无限用),**邮件 basemaps@linz.govt.nz** 申请(非自助)。文档里 `d01...` 是公共 demo key,**别用于生产**。
- **授权**:**CC BY 4.0,商用可**,须手动加署名:`© LINZ CC BY 4.0 © Imagery Basemap contributors`。
- **整块航拍 GeoTIFF 下载**:LDS 图层 **121752**「Auckland 0.075m Urban Aerial Photos (2024-2025)」,NZTM RGB;或 AWS 开放桶 `s3://nz-imagery`(`--no-sign-request`,免 key)。CC BY 4.0。→ 3D 把航拍贴到 DSM 面时用本地下载更方便。

### council GeoMaps 自有底图/航拍(公开,已实测)
> ⚠️ **更正旧认知**:`mapspublic.aklc.govt.nz/arcgis` 的 **`Raster`、`Basemap` 文件夹是公开的(无需 token)**。之前的 499 是**另一台主机**(`tiles.arcgis.com/.../n4yPwebTjJCmXB6W`,标 SECURE)和 `arcgis3/.../OpenData`,不是这台。
- **航拍(当前)**:`.../Raster/AerialPhotography20242025/MapServer` —— **0.075m,奥克兰最新最清**(对奥克兰比 LINZ 更新)。NZTM(2193),缓存。
- **历史航拍(未来功能预留,现在不做)**:同 `Raster/` 文件夹下有**各年代历史航拍**,可做"地块今昔对比":
  `AerialPhotography{1940s, 1950s, 1960s, 1970s, 1980s, 1990s, 1999OuterIsland, 20002005, 20062009, 20102011, 20152016, 2017, 20192020, 2022, 20242025, 2024WestAuckland}/MapServer`(均 `?f=image` export 取图)。
  → **MVP 不做;以后想加历史影像再谈、并确认授权。当前底图/航拍一律走 LINZ。**
- **底图**:`.../Basemap/{AerialBasemap, TopoBasemap, GreyCanvasBasemap, TerrainBasemap}/MapServer`;`.../Landbase/MapServer`(44 层矢量,**自带地块红线 + 路名 + 海岸线**)。
- **取瓦片**:用 `…/MapServer/export?bbox=...&f=image`(其 NZTM 缓存索引不匹配,`tile/{z}/{y}/{x}` 会 404,用 export 稳)。
- ⚠️ **授权不明**:版权写 "Auckland Council & Aerial Surveys Ltd",无明确 reuse 许可;**商用前向 council GIS(gis@aklc.govt.nz)确认**。→ 正式版影像优先 LINZ(授权明确),council 作"更清航拍"可选叠加。

### 其它(基本不需要)
- **Carto**(Stage 0 用的街道底图):免费 CDN **不含商用授权**(LICENSE 明示仅企业/非营利);无航拍。→ 正式版**不用**。
- **MapTiler** 商用最低 $25/月;**Mapbox** 5万 loads/月免费但**房地产类可能需单独商用授权**(问销售);**Esri World Imagery** 开放端点商用违反 ToS,正式需 ArcGIS 账号。→ 除非要其特定风格/全球覆盖,否则不需要。

### 用法结论
| 用途 | 测试版 | 正式版 |
|---|---|---|
| 街道/地形底图 | LINZ `topolite/topographic`(demo key)/ Carto(临时) | **LINZ topographic**(Developer key)/ council Landbase·TopoBasemap |
| 航拍 | LINZ `aerial`(demo key)/ Esri World Imagery | **LINZ aerial**(Developer key,授权明确);council 0.075m 作可选更清叠加(待授权确认) |
| 3D 贴图用航拍 | — | LINZ GeoTIFF(LDS 121752 / `s3://nz-imagery`)本地下载 |

---

## 4. 数据解码注意事项

0. ⚠️ **格式坑(2026-06 实测)**：Council 旧服务器 `mapspublic.aklc.govt.nz/arcgis*`（ArcGIS 10.81）的 MapServer **不支持 `f=geojson`**（返回二进制/报错），必须用 **`f=json`（Esri JSON）然后前端自己转 GeoJSON**。转换:point `{x,y}`→`[x,y]`；polyline `{paths}`→坐标即 paths；polygon `{rings}`→坐标即 rings；`attributes`→`properties`；Leaflet 用 `[lat,lon]=[y,x]` 需调换。LINZ 新 FeatureServer 则支持 geojson。参考 `F:\万一呢\map-demo\index.html` 的 `addEsri()`。
1. **坐标系**：原生为 NZTM2000（EPSG:2193，单位米）。请求时加 `outSR=4326` 让服务器直接转成经纬度，前端 Leaflet/Mapbox 可直接用，省去自己投影。
2. **结构**：`features[].attributes`(属性键值对) + `features[].geometry`(几何：point=x,y；polyline=paths；polygon=rings)。
3. **日期**：是 **Unix 毫秒时间戳**（如 `issue_date=118886400000`），需 /1000 转。
4. **标高/管底**：单位米，基准 NZVD（如 `SW_INVERT_LEVEL_DOWNSTREAM_M`、`SW_COVER_LEVEL_M`）。
5. **面积**：LINZ `survey_area`（法定丈量面积）与 `calc_area`(GIS 计算)略有差异，报告以 survey_area 为准。
6. **0 命中 = 该地不在该图层范围**（如液化区返回 0 = 此地无液化风险），是有效结果不是错误。
7. **地理编码（地址→坐标）**：测试期用 Nominatim（OSM）免费；生产建议用 LINZ Addresses 图层或 Council Address 服务保证与红线一致。

---

## 5. 实测样例 —— 31 Malmo Place, Massey, Auckland
坐标:lon 174.6071181, lat -36.8409585

| 维度 | 结果 | 来源 |
|---|---|---|
| 地块 | Lot 15 DP 69721 | LINZ Primary Parcels |
| 产权 | NA25C/905, Freehold | LINZ Property Titles |
| 面积 | **984 m²** | LINZ |
| 分区 | **Residential – Mixed Housing Urban Zone (MHU)** | Council UnitaryPlanZones |
| 雨水管理区 | Massey, Flow 2 | UnitaryPlanManagementLayers |
| 雨水管网 | 周边 80m 内 26 管 + 12 井 + 24 接驳（带管径 225mm、管底标高、安装年份）| LiveMaps/stormwater |
| 污水容量约束 | Watercare Waitakere, Wastewater 容量约束 2035–2040 | LiveMaps/UndergroundServices |
| 液化 | 0 命中 = **无液化风险** | LiveMaps/GeologyandGeotechnical |

---

## 6. 数据空白（公开接口拿不到的）
- **房屋上市 / 成交价 / 历史交易价**：没有发现“每个地块、公开、可批量/API”的官方成交价接口。NZ 的 sale price / DVR bulk 数据长期由 QV/CoreLogic/Valocity/Headway 等商业渠道或 council 商业授权控制；公开数据请求记录里也明确说明 bulk DVR/valuation data 可商业授权、通常不开放。LINZ 有 `NZ Properties: National District Valuation Roll`，但主表是 Restricted Access/或仅开放 subset，不等于完整逐房成交历史。MVP 不需要。
- **精确地下管线 as-built 图纸 / Watercare 详细管网几何**：受限，需走 beforeUdig 或向 Watercare 申请。公开接口只到"容量约束区"层级 + Council 自管的 stormwater 管网。
- **学区 / 收入统计**:来自 Stats NZ Census + 教育部 school zones（另一批公开数据，免费）。

---

## 7. PowerShell 快速测试模板
```powershell
$ua = @{ "User-Agent" = "Mozilla/5.0 Chrome/124" }
$lon = 174.6071181; $lat = -36.8409585
$svc = "https://mapspublic.aklc.govt.nz/arcgis/rest/services/LiveMaps/stormwater/MapServer"
# 列子图层
(Invoke-RestMethod -Headers $ua -Uri "$svc`?f=json").layers | % { "$($_.id): $($_.name)" }
# 按点查图层16
$uri = "$svc/16/query?geometry=$lon,$lat&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=false&f=json"
(Invoke-RestMethod -Headers $ua -Uri $uri).features
```

### 查 CV/RV（Revaluation 2024）
```powershell
$ua = @{ "User-Agent" = "Mozilla/5.0 Chrome/124" }
$lon = 174.6071181; $lat = -36.8409585
$fields = "RATEACCOUNTNUM,PROPERTYID,VALUATIONREF,RATESASSESSMENTNUM,FORMATTEDADDRESS,LEGAL,CV,LV,VALUATIONDATE,LCV,LLV,LATESTVALUATIONDATE,CT,AREALABEL"
$svc = "https://services1.arcgis.com/n4yPwebTjJCmXB6W/arcgis/rest/services/AGOL_RateAccountInfo1_gdb/FeatureServer/0"
$uri = "$svc/query?geometry=$lon,$lat&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=$fields&returnGeometry=false&f=json"
(Invoke-RestMethod -Headers $ua -Uri $uri).features.attributes
```

31 Malmo Place 实测返回:
```json
{
  "FORMATTEDADDRESS": "31 Malmo Place\rMassey\rAuckland 0614",
  "LEGAL": "LOT 15 DP 69721",
  "CT": "NA25C/905",
  "CV": 1150000,
  "LV": 900000,
  "VALUATIONDATE": 1622505600000,
  "LCV": 980000,
  "LLV": 680000,
  "LATESTVALUATIONDATE": 1714521600000,
  "AREALABEL": "984 M2"
}
```

### 查 school enrolment zones + 学校详情
```powershell
$ua = @{ "User-Agent" = "Mozilla/5.0 Chrome/124" }
$lon = 174.6071181; $lat = -36.8409585
$fields = "School_ID,School_name,Institution_type,Office,Approval_date,Effective_date"
$svc = "https://services.arcgis.com/XTtANUDT8Va4DLwI/arcgis/rest/services/NZ_School_Zone_boundaries/FeatureServer/0"
$uri = "$svc/query?geometry=$lon,$lat&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=$fields&returnGeometry=false&f=json"
$zones = (Invoke-RestMethod -Headers $ua -Uri $uri).features.attributes
$zones

# 用 School_ID 去 Education Counts Schools Directory 补详情
$ids = ($zones | % { "'$($_.School_ID)'" }) -join ","
$sql = "SELECT ""School_Id"",""Org_Name"",""Org_Type"",""Authority"",""CoEd_Status"",""Add1_Line1"",""Add1_Suburb"",""Add1_City"",""Telephone"",""Email"",""URL"",""Latitude"",""Longitude"" FROM ""4b292323-9fcc-41f8-814b-3c7b19cf14b3"" WHERE ""School_Id"" IN ($ids)"
$dirUri = "https://catalogue.data.govt.nz/api/3/action/datastore_search_sql?sql=" + [uri]::EscapeDataString($sql)
(Invoke-RestMethod -Uri $dirUri).result.records
```

31 Malmo Place 实测命中:
```json
[
  {"School_ID":1363,"School_name":"Massey Primary School","Institution_type":"Full Primary"},
  {"School_ID":43,"School_name":"Massey High School","Institution_type":"Secondary"},
  {"School_ID":1643,"School_name":"St Paul's School (Massey)","Institution_type":"Contributing"}
]
```
