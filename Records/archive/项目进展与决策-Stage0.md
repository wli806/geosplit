# 项目进展与决策 — 奥克兰地块分割可行性 MVP

> 这是项目的"状态 + 决策"记录(技术接口细节见同目录《Auckland-GIS-数据接口手册.md》)。
> 每次会话开始,先读这两份即可恢复全部上下文。
> 负责人:peter@donutbrowser.ai

---

## 1. 产品定义
输入一个奥克兰地址 → 自动返回:分区、地块/面积、规划覆盖层、地形、地下管网 → **判断分割可行性,产出可行性报告**(将来网页收费)。
- 目标用户:开发商/投资人/买家。
- **房屋买卖/上市数据明确不在 MVP 范围**(那是 relab 等的付费壁垒)。

## 2. 已确认的架构与顺序(重要)
- **先做"引擎"(纯函数 `analyze(address) → 结构化报告`),不做界面**;引擎是价值核心,3D 网页是展示层。本地把逻辑跑通 → 再拆前后端 → 再上服务器。
- 数据模型从第一天起**带 Z(z-aware / 2.5D)**,2D 图、剖面、3D 视图都是同一模型的不同呈现。
- **模块顺序**:
  1. 数据层(取数 + 归一化)
  2. **B = 合规 / 可建包络规则(最难、最值钱、别人抄不动 → 下一步要做的核心)**
  3. A = 可视化(已验证可行,属执行)
  4. C1 = 产能/可建量测算(并入核心)
  5. C2 = 精细排布方案 + 雨水容量计算(往后,最难)

## 3. 关键产品洞察
- **urban MHU 的产能不是"面积 ÷ 最小地块"**,而是"**这块地能合规塞下几栋房子**"(围着已建房子细分 subdivision-around-development)。
- 因此真正卡产能的是**塑造可建包络的发展标准**:HIRB 日照斜面、退界、覆盖率、不透水率、户外生活空间、停车/车道 access、基础设施容量。E38 最小地块面积反而次要。
- 报告结论三态:**✅符合 / ❌不符合 / ⚠️需人工评估**;超出 MVP 范围的一律标 ⚠️。
- MVP 范围:**仅 MHU 分区 + fee simple(产权)细分 + urban subdivision**;rural、复杂 overlay 暂不做。

## 4. 规则库版本控制
- AUP 官网无版本号 → 我们**对每条规则存 {条款号, 文本哈希, 抓取日期}**,逐条哈希比对来检测更新。
- council 其实**按法定版本分服务**:Operative / Proposed / Decisions / Recommendation / Sealed,外加 **PNPSUD(Plan Change 78 城市强化)** 整套图层。
- **待 planner 确认**:MHU fee simple 细分现在到底归哪套规则管(Operative 还是 PNPSUD)。这是开做 B 模块前的头号问题。

## 5. 3D 可视化验证(2026-06-16/17 已完成)
本地 demo:
- `F:\万一呢\map-demo\` —— 2D(Leaflet):地块、周边地块、管网、检查井(可点)、等高线、洪泛区。
- `F:\万一呢\map-demo-3d\` —— 2.5D(deck.gl):等高线三角网地形面、**Esri 卫星图 UV 纹理贴合**、地下管线/检查井按埋深、拉伸包络盒、lot 边线贴地。
**已验证**:地形面、透明看管网、卫星贴图、线贴合地面(=道路同法)、盒子穿模、datum 机制。
- 当前高度 = DTM(等高线/裸地面);**DSM + 房树识别(nDSM=DSM−DTM + LINZ 建筑轮廓)待真 LiDAR 下好后补**。
- 生产 3D 引擎目标:**CesiumJS**(地形+影像贴合+道路 clampToGround 原生)。

## 6. 数据决策
- **垂直 datum 统一 NZVD2016**;用 council 管网的 `_NZVD2016` 字段。
- **高程数据**:LINZ "Auckland Part 1 LiDAR 1m DEM / DSM (2024)",**EPSG:2193 (NZTM2000)**,NZVD2016,垂直精度 ±0.2m,**CC BY 4.0(可商用,需署名)**。用户正在下西区瓦片。注意:数据是洪灾后补测、仍在精修。
- **底图**:不要用 OSM(会被封、禁商用);开发用 Carto,生产用 **LINZ 航拍(0.075–0.1m,免费 key)** 或 Esri World Imagery。
- council 的 `Raster`/`ElevationImage`/`Basemap`/`OpenData` 文件夹**需 token,公开拿不到**;高程栅格只能从 LINZ 下。

## 7. 技术架构(2026-06-18 定 + 已搭骨架)
- **从第一天就分前后端两个服务、用 JSON API 对话,都先跑本地**;上线只是改地址,不重构。后端=引擎(HTTP 暴露),前端=可视化+验证工具。
- **后端**:Python + FastAPI(+ requests;将来 shapely/rasterio/pyproj/geopandas 做几何与栅格、ezdxf 出 DXF、reportlab/weasyprint 出 PDF)。Pydantic 模型 = 契约。
- **前端**:TypeScript + React(MVP 阶段先用 CDN + Leaflet/deck.gl);产品级 3D-GeoMaps 用 **CesiumJS**(地形+航拍+3D建筑+洪水)。3D 库可换,藏在应用后面。
- **契约(关键 seam)**:`GET /site?address=` → SiteModel;`POST /analyze {address,params}` → Scheme[];`GET /export` → PDF/DXF。
- **已搭最小骨架并跑通**(2026-06-18):`F:\万一呢\backend\app.py`(FastAPI,`/ping` + `/site`,已实测返回 31 Malmo 的 zone/面积/title/几何)+ `F:\万一呢\frontend\index.html`(Leaflet,调后端画地块)。
  - 启动:`py -m uvicorn app:app --port 8000 --app-dir "F:/万一呢/backend" --reload` + `py -m http.server 5500 --directory "F:/万一呢/frontend"` → 开 http://localhost:5500
  - 依赖目前装在全局 Python 3.14;待整理成 venv + requirements;前端长大后转 Vite+React+npm。
- 环境:Python 3.14、Node 24、npm、git 均已装。负责人背景=Godot/C++/C,数据结构强,**web 前后端这层由 Claude 负责**。

## 8. 引擎架构 — 计算 pipeline(2026-06-18 定)
- **结算 pipeline 模式**(类比游戏回合结算):一个 **Context(黑板)** 对象流过**有序步骤**,每步**读它需要的、写回自己的结果**;步骤之间不互相调用,由 runner 按顺序跑。加步骤 = 往 `PIPELINE` 列表插一行。
- **两类"规则",分开放**:
  - **变换步骤 Transform(有序)** = pipeline 列表:A 画布 / B 车道 / C 分段 / D 建筑平台 / E 高度 / F 汇总。
  - **校验规则 Check(无序集合)** = **自注册表(registry)+ 阶段钩子**。加校验 = 写一个 `@rule` 函数,引擎/步骤/其它规则**不动**(开闭原则)。
- **铁律**:步骤"产出值"(写 context);校验"只读 + 断言"(纯谓词)。任何要产出"被别人用到的值"的,一定是**步骤**不是校验 → 校验之间永远无依赖、无顺序问题。
- **参数 vs 逻辑**:数值/阈值外置成 **config(按 zone,JSON)**;逻辑写成**代码函数**去读 config。**不做 JSON 规则 DSL(过度工程)。**
- **改动局部化**:改阈值=只改 config;加独立校验=只加注册表;加新几何行为=只改那一个 step 文件;核心引擎稳定。
- **每步把几何写进 `ctx.layers`**,API 一并返回,前端**逐层渲染** → 每步都能单独可视化验证。
- **几何运算在 NZTM2000(EPSG:2193,米)里做**,显示时转 4326。
- 文件结构:`engine/{pipeline.py, context.py, steps/a_canvas…f_assemble, geom/, rules/(registry+checks), config/zones.json}` + `api/app.py`。
- 开发用 PRD 记录每个 slice:见 `F:\万一呢\PRD\`。

## 8b. 计算引擎已完成的 slices(截至 2026-06-19)
pipeline:`a_canvas → b_driveway → c_subdivide → d_platform → e_envelope`(+ a 后建地形 ground、b 后建 HIRB 外边界)。
- **1-1**:取数 → 画布/车道/分段/可建范围(2D)。车道=沿真实长边恒定 3.5m;可建范围=按每条真实边各自方向退界的**一般四边形**(非矩形);首户补偿 = front−side。
- **1-2b**:**3D 可建包络(地形 + HIRB)+ 2D/3D 前端**(已验收 2026-06-19)。
  - 地形:council Contours2024(1m 反推),抓一次缓存本地;`matplotlib.tri` 插值 `ground(x,y)`。
  - **HIRB = 平面下包络(关键决策,2026-06-19 与负责人定)**:不逐点采高度场,而是每户(沿长轴的 x 段)算几个**平整 recession 平面**——低长边/高长边各一斜面(3m 起 + 45°)、后界斜面(仅末户)、11m 平顶;基准用 **segment-average 地面**(该边落在本户 x 段内的地面平均,逐户一档台阶)。天花板 = 这些平面取 min,半平面裁剪切成平整 facet。**临街侧 / 户间分隔线竖直,无 recession**;HIRB 只从 2 长边 + 后界算。
  - 理由:recession plane 本就是平面 → 几何正确、轻、不碎;且每个面带法向量,**为后续"放体块算超出 HIRB %"留好接口**。
  - **数据资产**:`ctx.envelope_planes = {angle, origin, bands:[{x0,x1, planes:[{kind,a,b,c}]}]}`(local 坐标,`z=a·x+b·y+c`)。下一步碰撞/容量直接复用,别重算。
  - 前端 `frontend/index.html`:2D(Leaflet)↔3D(deck.gl)切换;3D = 主题底图贴地形(单张纹理 drape,非分层叠加)+ 可建区青绿 facet(按高度)+ 其余 60% 灰纱 + 建筑墙 + 户间 fin;图层开关 + 指北针。左右车道:两 side 共用同一稳定坐标系(角度归一化到 (-90,90]),只切换落在低/高长边。
  - 验证手段:后端先用 matplotlib 3D 出图自检几何,再上 deck.gl(浏览器渲染 Claude 看不到)。诊断图存 `Records/refs/`。

## 9. 下一步(待负责人定方向)
**已铺好两条可走的路,开工前按约定先对算法:**
- **路线 A:产能/合规判定(用 envelope_planes)** —— 往包络里"放体块/楼面",算占地、覆盖率、不透水率,以及**超出 HIRB 的面积/体积百分比**(AUP 允许一定超出,需判定),输出三态结论。这是把已建好的几何变现成"可行性结论"。
- **路线 B:B 模块规则库** —— 先咨询 planner 确认 MHU 细分归哪套规则(Operative / PNPSUD),再由负责人逐项讲检查点,结构化成"规则单元"(检查什么/用哪字段/通过条件/引用条款/结论分级),挂进 Check 注册表。
- 其它待办:依赖整理成 venv + requirements;真 LiDAR(DSM/nDSM)下好后补 DSM 高度。
