# PRD — Slice 1-1:几何流水线骨架(A→D)+ 可视化

- 日期:2026-06-18 ｜ 状态:✅ 完成(2026-06-18,11 Malmo 672㎡ / N=4 跑通,四层几何 + 覆盖率校验)
- 架构总纲:`../Records/项目进展与决策.md`(第 7、8 节)

## 1. 目标(一句话)
搭起"计算 pipeline"骨架,让 **输入地址 + 户数 N → 后端把地块切成 N 块带车道的子地块、每块算出建筑平台 → 前端逐层画出来**,跑通整条端到端链路,作为以后所有规则的地基。

## 2. 测试地块
**11 Malmo Place, Massey**(长条形,后有邻居车道,适合后续修复/扩展模型)。

## 3. 范围
**IN(本切片做):**
- pipeline 骨架:runner + Context(黑板)+ `ctx.layers` + `ctx.findings`
- geom 工具:reproject(4326↔2193)、沿边 offset 成带、按进深切 N 段、向内 buffer、算面积
- config:`zones.json`(MHU 参数,**数值为占位、待 planner 确认**)
- rules 注册表骨架 + **1 个示例校验**(覆盖率)证明注册模式
- 步骤 A→D:
  - **A 画布**:地块多边形(2193)、识别临街边、面积、进深
  - **B 车道**:沿**固定一侧**切 3.5m 宽 driveway,得剩余可建面
  - **C 分段**:剩余面**等分成 N 块**(每块临车道)
  - **D 建筑平台**:每块**退界(统一)+ 覆盖率封顶** → building platform 面 + 占地面积
- 后端 `/analyze?address=&n=&side=` → 返回 SiteModel + SchemeResult(layers + 每块面积 + findings)
- 前端:地址 + N + 侧 输入 → 调 `/analyze` → 逐层渲染(地块/车道/子地块/平台,可开关)+ 每块面积读数

**OUT(本切片不做,留接口/后续 slice):**
- 高度 / HIRB 精算(slice 1-2)
- 完整校验套件(逐条 slice 累加)
- 前排/后排地块区别对待、不等分(slice 1-2/1-3)
- 联排、配置档(舒适/紧凑)、选侧优化
- 雨污水 service、outlook、采光、车库/停车精确摆位
- 3D 渲染(沿用已验证的 2.5D,后期接)

## 4. 输入 / 输出契约
```
GET /analyze?address=<str>&n=<int>&side=<left|right>
→ {
   site:   { lonlat, lot_geojson, zone, area_m2, frontage_m, depth_m },
   params: { n, side },
   layers: { driveway, sublots:[…], platforms:[…] },   // GeoJSON(4326),供前端画
   lots:   [ { idx, area_m2, platform_area_m2 } … ],
   findings:[ { rule_id, ok, detail, clause } … ]        // 示例:覆盖率
}
```

## 5. 验收标准(怎么算做完)
1. 输入 `11 Malmo Place, Massey` + N(如 4)→ 前端显示:地块红线、一条沿边 3.5m 车道、N 个子地块、每个子地块上一个建筑平台,并列出每块面积/占地面积。
2. 改 N → 结果实时更新;**同一输入永远同一输出**(确定性)。
3. 所有几何在 2193 算(面积/距离正确),显示转 4326。
4. 退界/覆盖率/车道宽**从 `zones.json` 读**,非硬编码。
5. 覆盖率示例校验出现在 `findings` 里(证明注册表模式可用)。

## 6. 待 planner 确认(先用占位值,标注)
- 子地块退界值(前/侧/后);前排沿街退界。
- MHU 覆盖率 % / 景观率 % / 车道最小宽与最大长。
- 围开发情形下最小子地块面积是否仍适用。

## 7. 备注
- 几何按**通用多边形**写(shapely),不特判长方形;梯形/不规则地块以后自动支持。
- 依赖:`shapely`、`pyproj`(本切片新增)。
