# PRD — Slice 1-2c:可建体量拟合(2D 平面)+ 方案/策略化架构

- 日期:2026-06-19 ｜ 状态:**草稿(待负责人确认算法后定稿)**
- 架构总纲:`../Records/项目进展与决策.md`(第 8 节);上一片成果见 8b。
- 测试地块:11 Malmo Place, Massey;N=4。

## 0. 一句话目标
给每户一个**参数化房子**(footprint = 直接 L×W,或 卧室数→面积表;+ 层数),在 **HIRB + 退界包络**内把 footprint 放进去,并预留 **室外生活空间(OLS)/ 景观 / 不透水**约束,产出每户**实际建筑占地**与 **2D 平面图** + 合规结论(✅/❌ + 卡点)。
**同时**把计算 pipeline 升级成"**方案(Scheme)+ 可插拔策略(Strategy)+ 共享校验(Check)**"的清晰分步结构,为以后多布局方案的比较打基础。

---

## A. 架构升级(先做,避免规则搅在一起)

三类东西,职责分明(在现有"有序步骤 + 无序校验"上加一层"策略"):
- **Step(有序)**:产出几何/值,写 Context。顺序固定,各管一段。
- **Strategy(策略,某些步骤的可插拔实现)**:同一步骤多种实现,由 Scheme 选中其一。= "选择模块命中其中一个布局"。
- **Check(无序纯谓词)**:读 Context 出 findings,**跨所有方案复用**。
- **Scheme(方案)** = {各策略点的选择 + 参数} → 跑有序步骤 → Context → 校验 → 打分。比较方案 = 跑多个 Scheme 排名(本片只跑单方案,比较器留后)。

### Pipeline 分相(顺序写死,职责单一)
| 相 | 职责 | 类型 |
|---|---|---|
| 0 Site | 取数 / 地形 ground / 分区 | 固定 |
| 1 Canvas | 转正(稳定坐标系)/ 临街边 / 进深 | 固定 |
| 2 **排布 arrange** | 划户 + 车道 + 定 HIRB 外边界 | **策略点 P1**（今唯一 `detached_row`：沿车道侧等分独栋；未来 `duplex`/`terrace`/`front_back`） |
| 3 法定包络 | 按边退界 → **可建范围**;HIRB recession 平面 → 3D 包络（含 `envelope_planes`） | 固定（已做） |
| 4 **建筑放置 place** | 在 `admissible = 可建范围 ∩ {天花板≥h}` 放 footprint;预留 OLS/景观;出**建筑占地** | **策略点 P2**（本片新增，今唯一 `detached_standard`） |
| 5 汇总/打分 | GFA、户数、合规摘要、（多方案时）score | 固定 |
| 校验 Check | 覆盖率 / 不透水率 / 景观率 / OLS 尺寸 / HIRB 拟合 | 无序、跨方案复用 |

**两个策略点 = P1(怎么排布)、P2(怎么放房子);其余全共享。** 换 P1/P2、复用相 3 与全部校验 → 方案之间互不打扰。
**本片落地**:实装 P2 的一个策略 + 相关校验 + 2D 平面图;P1 维持单策略但**显式经 selector**(把"缝"建好),比较器与更多策略留后续。

### 术语澄清(避免混)
- 相 3 "**可建范围**"= 法定最大可建区(= 现在的 plat / `platform_area_m2`)。
- 相 4 "**建筑占地**"= 真正摆下房子、扣掉 OLS/景观后的 footprint 面积。两者不同,分开命名。

---

## B. P2 算法(本片核心,2D)
输入(每户):`footprint`(L×W 或 卧室数→面积表)、`floors`;`h = floors × 层高`。
1. **admissible** = 可建范围 ∩ ⋂_平面 `{ a·x + b·y + c ≥ h }`（复用 `envelope_planes` 的半平面裁剪;楼层越高 → admissible 越小,这就是"反向推导让房子塞进 HIRB")。
2. **放置策略 `detached_standard`**:footprint 矩形,朝向=地块长轴,**贴可建范围后侧、居中**(固定、可预期)→ 得落点。放不进 admissible 时:先按"必须在 admissible 内"判 ❌;**超出部分的面积/体积 %**作为 ⚠️ 输出(AUP 允许一定超出,精算留后)。
3. **预留**:OLS 矩形(≥ `ground_min_m2`、≥ `ground_min_dim_m`)塞进 `地块 − footprint − 车道`;景观 = `地块 − 不透水(footprint+车道+铺装)`。
4. **输出每户**:`footprint` 多边形、`OLS` 多边形、景观区、`admissible` 轮廓;结论 ✅/❌ + **卡点**(HIRB / 面积 / OLS / 景观 / 不透水)。
5. **2D 图层**(写 `ctx.layers`,前端逐层画):footprint / OLS / 景观 / admissible。

## C. 数值(`zones.json`,planner 待确认 → 先占位标注)
- `storey_height_m`(层高,算 h) — 新增
- 卧室数 → GFA 表(或本片先只用 L×W) — 新增
- `outdoor_living_space.{ground_min_m2, ground_min_dim_m}`(已有)
- `min_landscaped_pct` 0.35 / `max_impervious_pct` 0.60(已有)

## D. 验收标准
1. 11 Malmo, N=4,每户给 `L×W + floors` → 前端 **2D** 显示 footprint/OLS/景观,列每户**建筑占地** + ✅/❌ + 卡点。
2. 改 `floors`:admissible 随高度**收缩**(楼层多→可放区变小),可观察。
3. footprint 放不下 → 正确报 ❌ 并指出卡点;超出 HIRB 时给 ⚠️ + 超出 %。
4. 同输入同输出(确定性)。
5. 加策略点 selector 后,**P1/P2 仍单策略但走选择器**;Scheme 结构能记录"用了哪个策略"。

## E. 明确不做(OUT)
户内房间布局;outlook space 精算(依赖窗位,单列后片或用退界+OLS近似 ⚠️);停车位精摆;雨水容量;3D 拉伸(下一片);**多方案比较器**(下一片)。

## F. 待 planner 确认
- 层高、卧室→面积标准;OLS 是否须邻接居住区/朝向/可否在前院;景观率/不透水率定义口径;HIRB 允许超出的具体条款与比例。
