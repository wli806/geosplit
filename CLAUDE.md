# 项目:奥克兰地块分割可行性 MVP

这个目录(`d:\0-develop\1-code\civil_proj\old`,原 F:\万一呢)的项目是:**做一个自动化网站,输入奥克兰地址 → 产出地块分割可行性报告**(将来收费)。负责人 wli806nogi@gmail.com。

**MVP 范围(2026-06-22 调整)**:GeoMap 多图层预览 + 3D 模型 + **分割收支平衡** + DEM/DSM/flood 成像。**不做**自动房屋 layout(留作以后独立模块);产能只讲理论上限(推荐分几块 + 每块面积/层数/透水/室外)。

## 开始工作前,先读这三份(项目全部上下文)
- `Records/项目进展与决策.md` —— 产品定义、关键决策、数据资产、下一步。
- `Records/V2-架构.md` —— **V2 五层架构(锁定)**:目录树、三条铁律、文件粒度、技术决策、残留检查清单。
- `Records/Auckland-GIS-数据接口手册.md` —— 所有已验证可用的公开数据接口(council ArcGIS + LINZ)、查询方法、解码、datum。
- 另:`AUP-MHU规则数值.md`(法定数值)、`数据字典.md`(输入模型)、`待确认-planner问题.md`。

## 代码:V2 全新写
- **V2 在 `backend/` + `frontend/`**,按 `V2-架构.md` 五层结构;开工前每刀跑残留检查清单。**当前进度见 `Records/项目进展与决策.md`**。
- **跑**:双击 `start.bat` → 起 backend(:8001)+ frontend(:5501),自动开 http://localhost:5501。
- **已完成**:slice 1-1「场地基础信息总览」(地块/CV/分区/洪水/等高线/学校 2D 图层 + 溯源面板)。PRD 在 `PRD/Stage 1/`。
- 旧 Stage 0(`backup/backend_stage0/` `backup/frontend_stage0/` `map-demo*/` `PRD/Stage 0 Demo/` `Records/archive/`)只作参考,不在其上改架构。

## 约定
- **⭐ 每个 slice 开工前,先确认算法再施工**:动任何代码前,先用文字/示意把该 slice 的算法讲清楚、列出关键决策点、和负责人讨论达成一致,**再开始写**。严禁"一上来就一顿乱做、做完再反复修算法问题"——那样效率极低(已多次踩坑)。讨论 → 确认 → 施工 → 验证。
- 规则/规章以 **planner 和负责人** 为权威,我负责结构化;不要凭记忆编 AUP 的条款号或数字标准。
- **PRD 先行**:所有要做的东西先用 PRD(`PRD/`)以文字确立,达成一致后再写代码。
- **守 V2 五层铁律**:单向依赖(sources→domain→render→api→frontend,绝不反向);domain 出抽象、render 出画法;数据带溯源 `Field`。开工前跑 `V2-架构.md` 第 6 节残留检查,防旧 layout 方案渗入。
- 数据/接口的事,先查《接口手册》,别重复探测。
- 项目知识写进 `Records/`(不要写进 .claude 的全局 memory)。
