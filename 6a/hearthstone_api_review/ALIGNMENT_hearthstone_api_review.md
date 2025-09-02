### 任务：系统性梳理 Hearthstone API 文档（含酒馆战棋）

#### 项目与任务特性规范
- 目标：全面阅读并提炼《炉石传说》官方 API 文档的“Cards/Card Search/Metadata/Cardbacks/Deck/通用机制（认证、本地化、分页、排序）”，明确与“酒馆战棋（Battlegrounds）”相关的筛选与响应字段，输出可直接调用的请求示例与判定规则。
- 范围：仅围绕官方 Battle.net Hearthstone API 文档。引用主文档（卡牌搜索指南）：[Card Search Guide](https://develop.battle.net/documentation/hearthstone/guides/card-search)。

#### 原始需求
- “用谷歌或者网页，把整个的 API 部分的文档都看下”，并聚焦如何区分酒馆战棋数据与其他模式数据，沉淀清晰规则与可用示例。

#### 现有约定与理解
- 所有接口以 POST 为优先用于“项目创建接口”，但本研究为第三方只读查询 API，用 GET 形成示例。
- 文档来源：Battle.net 官方文档。核心参考：[Card Search Guide](https://develop.battle.net/documentation/hearthstone/guides/card-search)。

#### 需求边界
- 输出包含：端点总览、核心查询参数、模式区分（`gameMode` 等）、响应结构关键字段、分页/排序/本地化、鉴权用法、示例请求。
- 不包含：服务端落地代码实现与定时同步；若后续需要，会另起任务。

#### 关键结论（初版对齐）
- 端点家族（常见）：
  - `GET /hearthstone/cards`：卡牌/实体搜索与检索
  - `GET /hearthstone/metadata`：元数据（集合、职业、类型、随从种族、关键词、可用模式等）
  - `GET /hearthstone/cardbacks`：卡背
  - `GET /hearthstone/deck`：卡组解析与信息
- 认证：Battle.net OAuth 客户端凭证流获取 `access_token`，调用时携带 `access_token` 或 `Authorization: Bearer`。
- 本地化：`locale` 参数，示例 `zh_CN`。
- 分页：`pageSize`、`page`；排序：`sort`、`order`（具体可用字段以文档为准）。
- 酒馆战棋区分：
  - 请求侧使用 `gameMode=battlegrounds` 明确限定为 BG 生态。
  - 响应侧存在 `battlegrounds` 专属字段（如 `tier` 等）。
  - 多数 BG 实体 `collectible=false`，且 `set`/`cardSet` 指向 BG 相关集合。
  - 可与 `type`（`hero|minion|spell` 等）联用进一步细分 BG 英雄/随从/法术。

#### 疑问澄清（需在后续共识中确认/更新）
- BG 层数筛选参数名在不同版本文档/实现中可能表现为 `tier`（在 `gameMode=battlegrounds` 语境下）；需以线上响应与 Metadata 交叉校验。
- 可排序字段及其合法值范围需以官方 Cards 端点文档为准。

#### 参考链接（持续补充）
- Card Search Guide（官方）：https://develop.battle.net/documentation/hearthstone/guides/card-search


