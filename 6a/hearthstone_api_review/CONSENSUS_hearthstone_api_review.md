### Hearthstone API 最终共识（含酒馆战棋）

#### 明确的需求与验收标准
- 明确区分“酒馆战棋”数据与其他模式：
  - 请求参数包含 `gameMode=battlegrounds`；
  - 响应携带 `battlegrounds` 专属字段（如 `tier`）；
  - 多数 BG 实体 `collectible=false`，集合归属为 BG；
  - 可通过 `type` 细分 BG 英雄/随从/法术。
- 提供端点与参数清单、分页/排序/本地化与认证说明、可直接调用的示例。

#### 技术实现方案与约束
- 仅文档与示例阶段，不落地代码。
- 若后续自动化采集：通过 `GET /hearthstone/cards` + `gameMode=battlegrounds` 分页抓取，配合 `metadata` 映射显示名与本地化。

#### 端点与参数要点
- Cards：`/hearthstone/cards`
  - 核心参数：`gameMode`、`type`、`minionType`、`rarity`、`class`、`keyword`、`textFilter`、`pageSize`、`page`、`sort`、`order`、`locale` 等
  - BG 特化：`gameMode=battlegrounds`；在响应 `battlegrounds` 字段下可见 `tier` 等属性
- Metadata：`/hearthstone/metadata`
  - 提供集合、职业、类型、随从种族、关键词、模式等元数据
- Cardbacks：`/hearthstone/cardbacks`
- Deck：`/hearthstone/deck`

#### 本地化与分页
- 本地化：`locale=zh_CN` 等
- 分页：`pageSize`（默认/上限以文档为准），`page` 从 1 开始
- 排序：`sort` 与 `order`（升/降），合法字段以官方为准

#### 认证
- Battle.net OAuth 客户端凭证流获取 `access_token`，请求时附带

#### 示例（可直接调用）
- BG 英雄：
  - `GET https://us.api.blizzard.com/hearthstone/cards?locale=zh_CN&gameMode=battlegrounds&type=hero`
- BG T1 随从：
  - `GET https://us.api.blizzard.com/hearthstone/cards?locale=zh_CN&gameMode=battlegrounds&type=minion&tier=1`
- BG 指定种族（如野兽）随从：
  - `GET https://us.api.blizzard.com/hearthstone/cards?locale=zh_CN&gameMode=battlegrounds&type=minion&minionType=beast`

#### 任务边界与确认
- 边界：本任务不改动代码，仅梳理文档与给出可调用示例
- 不确定性：BG 层数筛选参数名与排序字段需以线上响应或更细节文档校验
- 上述不确定点已记录，后续如需采集实现，将进一步验证

#### 质量门控
- 边界清晰、与官方文档对齐
- 验收标准：具备查询与区分 BG 的清晰方法与示例链接

参考：
- Card Search Guide（官方）：https://develop.battle.net/documentation/hearthstone/guides/card-search


