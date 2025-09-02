# ALIGNMENT_bgs_api_docs

## 项目上下文分析
- 项目文档主目录为 `docs/`，`docs/README.md` 为索引与规范总览。
- 现有数据与机制文档已按英雄、随从、法术、机制分门别类。
- 本任务需基于官方文档 `https://develop.battle.net/documentation/hearthstone` 汇总与酒馆战棋（Battlegrounds）相关的全部 API，用于本地离线查询与后续脚本调用参考。

## 需求理解确认
- 目标：在本地新增一份结构化、可检索、示例齐全的 Battlegrounds API 文档。
- 输出：`docs/api-docs.md`（或子目录细分），包含鉴权、端点、参数、示例请求/响应、错误码、速率限制、最佳实践。
- 边界：仅收录与 Battlegrounds 直接相关的 API 用法与参数；若 API 为公共卡牌/搜索端点，但需通过 `gameMode=battlegrounds` 等参数区分，也应明确记录。
- 约束：遵循项目文档风格与结构；接口创建习惯（POST）仅作为项目实现规范说明，记录官方 API 原生方法不强行改写。

## 现有约定与模式
- 文档以 Markdown 为主；代码示例使用 `js` fenced code。
- 依赖管理默认使用 yarn；已有 `6aScript/` 脚本与 OAuth 获取示例可复用。

## 疑问澄清
1. 是否需要将通用 Hearthstone API 全量收录，还是仅列出 Battlegrounds 相关参数过滤视角？
2. 是否需要提供 TypeScript 接口定义片段，或保持以 API 文档与示例为主？
3. 错误码与速率限制是否需结合实际调用观测补充？

## 初步决策
- 以 Battlegrounds 视角组织：先总览，再分别覆盖“卡牌/搜索/元数据/媒体/局内赛季数据（如有）”。
- 必含 OAuth 鉴权章节，并与 `6aScript/` 中现有脚本衔接。
- 每个端点含：用途、方法与路径、必要/可选参数（包含 `gameMode=battlegrounds` 等）、请求示例、典型响应字段说明、备注与陷阱。

## 输出物
- `docs/api-docs.md` 为主文档；若内容过长，再按模块拆分到 `docs/api/` 子目录并在主文档索引。


