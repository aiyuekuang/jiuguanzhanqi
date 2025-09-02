# 炉石传说 酒馆战棋 API 本地参考文档

> 官方参考文档：[`https://develop.battle.net/documentation/hearthstone`](https://develop.battle.net/documentation/hearthstone)

本文档聚焦酒馆战棋（Battlegrounds）相关 API 的本地离线参考，覆盖鉴权、端点清单、关键参数（含 `gameMode=battlegrounds`）、请求/响应示例、速率限制、错误与最佳实践。示例以 Node.js `fetch` 为主，便于与本仓库的 `6aScript/` 脚本协作。

---

## 1. 鉴权（Battle.net OAuth 客户端凭证流）

- 授权方式：Client Credentials（客户端凭证流）
- 获取 Token：`POST https://oauth.battle.net/token`
- Header：`Authorization: Basic base64(client_id:client_secret)`，`Content-Type: application/x-www-form-urlencoded`
- Body：`grant_type=client_credentials`

示例（与 `6aScript/ts/src/bnet_oauth.ts` 一致的思路）：
```js
import 'dotenv/config'

const tokenEndpoint = 'https://oauth.battle.net/token'
const clientId = process.env.BNET_CLIENT_ID
const clientSecret = process.env.BNET_CLIENT_SECRET

async function getAccessToken() {
  const res = await fetch(tokenEndpoint, {
    method: 'POST',
    headers: {
      'Authorization': 'Basic ' + Buffer.from(`${clientId}:${clientSecret}`).toString('base64'),
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({ grant_type: 'client_credentials' })
  })
  if (!res.ok) throw new Error(`Token request failed: ${res.status}`)
  const data = await res.json()
  return data.access_token
}
```

使用方式：
- 后续请求在 `Authorization` 头部加 `Bearer ${access_token}`。
- 请将 `BNET_CLIENT_ID`、`BNET_CLIENT_SECRET` 放入 `.env`，不要提交到 Git。

---

## 2. API 基础信息

- 基础路径（示例）：`https://us.api.blizzard.com/hearthstone/`
- 常见查询参数：
  - `locale`（如 `zh_CN`）
  - `access_token`（或使用 `Authorization: Bearer` 头）
  - `namespace`（通常为 `static-{region}` 或 `dynamic-{region}`，官方文档会明确）
- 速率限制与错误：遵循 Battle.net 平台通用策略，详见官方文档链接。

---

## 3. 核心端点总览（Battlegrounds 视角）

> 下列端点来自官方卡牌/搜索/元数据能力，结合 `gameMode=battlegrounds` 或响应中的 `battlegrounds` 字段使用。请以官方文档为准：[`https://develop.battle.net/documentation/hearthstone`](https://develop.battle.net/documentation/hearthstone)

- 卡牌搜索：`GET /hearthstone/cards`（支持 `gameMode=battlegrounds`、名称/文本/关键字过滤、分页等）
- 单卡详情：`GET /hearthstone/cards/{id}`（返回包含 `battlegrounds` 字段的对象时与酒馆战棋相关）
- 元数据查询：`GET /hearthstone/metadata`（包含 `sets`、`types`、`rarities`、`classes`、`keywords`、`minionTypes` 等，部分可与 BG 关联）
- 媒体资源：`GET /hearthstone/metadata/{type}/{id}` 或卡牌媒体（用于图片/美术资源；与 BG 资产关联时使用）

备注：
- Battlegrounds 相关实体（英雄、随从、法术）通常通过卡牌搜索/详情端点以 `gameMode=battlegrounds` 进行过滤，并在响应对象的 `battlegrounds` 字段下提供 BG 专属信息（如 `tier`/`techLevel`、`hero` 标记、`duos`、`tribes`、`buddies` 等，具体以官方和实测为准）。

---

## 4. 卡牌搜索 `GET /hearthstone/cards`

用途：按条件查询 BG 卡牌（英雄、随从、法术等）。

关键参数（节选）：
- `gameMode=battlegrounds`：限定为 BG 模式卡牌。
- `textFilter` / `name`：按名称或文本匹配。
- `class`、`minionType`、`keyword`：按职业、随从类型、关键字过滤。
- `rarity`、`manaCost`：通常用于传统模式，BG 下仅在适配字段时有效。
- `page`、`pageSize`：分页。
- `sort`：排序字段（如 `manaCost`、`attack`、`health` 等，BG 可能以 `battlegrounds.tier` 相关字段为主要参考，视官方支持）。

示例：查询 BG 英雄/随从混合列表
```js
async function searchBgsCards({ token, region = 'us', locale = 'zh_CN', page = 1, pageSize = 50 }) {
  const base = `https://${region}.api.blizzard.com/hearthstone/cards`
  const params = new URLSearchParams({
    gameMode: 'battlegrounds',
    locale,
    page: String(page),
    pageSize: String(pageSize)
  })
  const res = await fetch(`${base}?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (!res.ok) throw new Error(`Search failed: ${res.status}`)
  return res.json()
}
```

典型响应字段（与 BG 相关）：
- `id`, `slug`, `name`, `text`, `image`, `imageGold`
- `cardTypeId`, `classId`, `minionTypeId`, `keywordIds`
- `battlegrounds`：对象，常见包含：
  - `tier` 或 `techLevel`：酒馆等级
  - `hero`：是否为英雄卡
  - `duos`：双打相关字段（若有）
  - `tribes`：部族（覆盖 BG 视角）
  - `buddies`：伙伴（历史或当期机制，若存在）

---

## 5. 单卡详情 `GET /hearthstone/cards/{id}`

用途：查询单个 BG 卡牌详情。

示例：
```js
async function getBgsCardById({ token, id, region = 'us', locale = 'zh_CN' }) {
  const url = `https://${region}.api.blizzard.com/hearthstone/cards/${id}?locale=${locale}`
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } })
  if (!res.ok) throw new Error(`Get card failed: ${res.status}`)
  return res.json()
}
```

典型响应中的 BG 字段：参考上一节 `battlegrounds` 对象内容。不同卡牌（英雄/随从/法术）字段组合有所差异。

---

## 6. 元数据 `GET /hearthstone/metadata`

用途：获取卡牌体系元数据（集合、类型、职业、关键字、随从类型等），用于构建检索条件或做 ID 到名称映射。

示例：
```js
async function getMetadata({ token, region = 'us', locale = 'zh_CN' }) {
  const url = `https://${region}.api.blizzard.com/hearthstone/metadata?locale=${locale}`
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } })
  if (!res.ok) throw new Error(`Get metadata failed: ${res.status}`)
  return res.json()
}
```

与 BG 相关：
- `minionTypes`：部族映射（在 BG 中大量使用）。
- `classes`：可能用于英雄归类映射（以官方为准）。
- `keywords`：效果/机制关键字（部分与 BG 通用）。

---

## 7. 媒体与图片

用途：卡牌图、金卡图、缩略图等媒体资源。通常通过卡牌对象中的 `image`/`imageGold` 或媒体端点获取。

注意：媒体链接的稳定性与授权需求请以官方为准，生产环境建议做缓存与失效策略。

### 7.1 本地批量下载卡图/英雄图

- 运行命令：`yarn bgs:media`
- 实现位置：`6aScript/ts/src/download_media.ts`
- 输入数据：`data/battlegrounds.json`（由 `yarn bgs:api` 生成）
- 输出目录：`6aScript/output/media/{heroes|minions}`，文件名基于卡名/slug。
- 下载内容：
  - `image` → 普通卡图，保存为 `${name}.png`
  - `imageGold` → 金卡图，保存为 `${name}_gold.png`
- 建议：首次全量下载后做增量更新与失败重试；尊重速率限制与版权使用规范。

---

## 8. 速率限制与错误处理

- 平台级速率限制：遵循 Battle.net 全局策略（不同环境/应用配额不同）。
- 常见错误：`401 Unauthorized`（Token 失效/错误）、`403 Forbidden`（权限/命名空间/区域配置异常）、`429 Too Many Requests`（限流）、`5xx`（服务端异常）。
- 建议：实现带抖动的重试、指数退避；对 `429` 做适度 backoff；关键请求加超时与日志。

---

## 9. 最佳实践与坑位

- 优先在查询中增加 `gameMode=battlegrounds`，以保证结果聚焦 BG 实体。
- 使用 `locale=zh_CN` 获取中文文本；如需多语言，建立本地映射缓存。
- 注意不同赛季机制变动（如伙伴、双打等），`battlegrounds` 字段结构可能变化，以实测为准。
- 对图片链接做缓存与兜底，避免频繁热链导致失败。
- 严格将 `client_id`/`client_secret` 放在 `.env`，避免泄露。

---

## 10. 与本仓库脚本衔接

- 运行命令：
  - `yarn bgs:api`（抓取 BG 英雄/随从，统一写入 `data/battlegrounds.json`）
  - `yarn bgs:docs`（基于 `data/battlegrounds.json` 生成/更新文档）
  - `yarn bgs:all`（依次执行上述两步）
- 脚本位置（TypeScript）：
  - `6aScript/ts/src/bnet_oauth.ts`（获取 Token）
  - `6aScript/ts/src/fetch_bgs_from_api.ts`（拉取 BG 数据并写入统一 JSON）
  - `6aScript/ts/src/generate_docs_from_api.ts`（从统一 JSON 生成文档）
- 统一数据文件：
  - 路径：`data/battlegrounds.json`
  - 结构：`{ region, locale, generatedAt, heroes: [...], minions: [...] }`
- 示例（最小抓取片段，Node.js fetch）：

```js
import 'dotenv/config'

async function main() {
  const { getAccessToken } = await import('../../6aScript/ts/src/bnet_oauth.ts')
  const token = await getAccessToken()
  const res = await fetch(`https://us.api.blizzard.com/hearthstone/cards?${new URLSearchParams({
    gameMode: 'battlegrounds',
    locale: 'zh_CN',
    page: '1',
    pageSize: '50'
  })}`, { headers: { Authorization: `Bearer ${token}` } })
  if (!res.ok) throw new Error(`status=${res.status}`)
  const data = await res.json()
  console.log(`items=${data.cards?.length}`)
}

main().catch(err => { console.error(err); process.exit(1) })
```

---

## 11. 参考链接

- 官方文档（Hearthstone API）：[`https://develop.battle.net/documentation/hearthstone`](https://develop.battle.net/documentation/hearthstone)
- OAuth 文档（Battle.net）：请参考官方平台文档（与上方页面关联）。

---

## 12. 端点目录与覆盖范围（与官方对齐）

- 已覆盖：
  - `GET /hearthstone/cards`（搜索）
  - `GET /hearthstone/cards/{id}`（单卡详情）
  - `GET /hearthstone/metadata`（元数据）
  - 媒体资源（通过卡牌对象中的 `image`/`imageGold` 与媒体端点说明）
- 本章节新增：
  - `GET /hearthstone/cardbacks`（卡背列表）
  - `GET /hearthstone/deck`（卡组编码/解析）

> 说明：本仓库聚焦酒馆战棋（BG）。`cardbacks`、`deck` 等端点属于通用能力，仍在此文档中收录作离线参考；BG 相关抓取仍以 `gameMode=battlegrounds` 的卡牌为主。

---

## 13. 卡背列表 `GET /hearthstone/cardbacks`

用途：获取卡背（Card Backs）集合（通用能力，非 BG 专属）。

常用参数：
- `locale`：语言（如 `zh_CN`）

示例：
```js
async function listCardbacks({ token, region = 'us', locale = 'zh_CN', page = 1, pageSize = 50 }) {
  const base = `https://${region}.api.blizzard.com/hearthstone/cardbacks`
  const params = new URLSearchParams({ locale, page: String(page), pageSize: String(pageSize) })
  const res = await fetch(`${base}?${params.toString()}`, { headers: { Authorization: `Bearer ${token}` } })
  if (!res.ok) throw new Error(`cardbacks failed: ${res.status}`)
  return res.json()
}
```

典型响应字段（节选）：
- `id`, `name`, `text`, `image`, `slug`, `sortCategory`, `sortOrder` 等

---

## 14. 卡组编码/解析 `GET /hearthstone/deck`

用途：对标准模式卡组进行编码/解析（通用能力，非 BG）。可用于将卡牌 ID 集合编码为 deckstring，或将 deckstring 解析成卡牌清单。

常见用法（以官方文档为准）：
- 解析（Decode）：通过 `code` 参数传入 deckstring，服务返回卡组详情。
- 编码（Encode）：通过卡牌 `ids`/`codes` 等参数提供卡牌与数量，由服务返回 deckstring。

示例：解析 deckstring
```js
async function decodeDeck({ token, region = 'us', locale = 'zh_CN', deckstring }) {
  const base = `https://${region}.api.blizzard.com/hearthstone/deck`
  const params = new URLSearchParams({ locale, code: deckstring })
  const res = await fetch(`${base}?${params.toString()}`, { headers: { Authorization: `Bearer ${token}` } })
  if (!res.ok) throw new Error(`decode failed: ${res.status}`)
  return res.json()
}
```

示例：编码生成 deckstring（以官方参数为准）
```js
async function encodeDeck({ token, region = 'us', locale = 'zh_CN', ids }) {
  // ids 形如 [[cardId1, count1], [cardId2, count2], ...]，具体以官方参数命名为准
  const base = `https://${region}.api.blizzard.com/hearthstone/deck`
  const params = new URLSearchParams({ locale })
  // 不同实现可能使用 query 方式传入多组卡牌与数量，或使用特定字段名
  // 这里仅给出占位示例，实际请以官方文档为准进行拼装
  ids.forEach(([id, count]) => params.append('ids', `${id}:${count}`))
  const res = await fetch(`${base}?${params.toString()}`, { headers: { Authorization: `Bearer ${token}` } })
  if (!res.ok) throw new Error(`encode failed: ${res.status}`)
  return res.json()
}
```

注意：Decks 能力属于对战/构筑模式的通用工具，不适用于 BG 的“随从池/英雄池/任务奖励”这类机制。

---

## 15. BG 任务/奖励（Quests/Rewards）可得性说明

- 公开 Hearthstone API 不提供“对局实时状态”，因此“第 3 回合给出的三个任务候选”不可通过 API 获取。
- 若存在“任务/奖励”的静态卡定义，它们应通过 `GET /hearthstone/cards` 搭配 `gameMode=battlegrounds` 与响应内 `battlegrounds` 字段进行识别（例如 `quest`/`reward` 标记字段，具体以实测为准）。
- 本仓库当前 `data/battlegrounds.json` 未包含 `quest: true`/`reward: true` 的条目，后续如需静态清单，可在 `6aScript/ts/src` 增加过滤逻辑抓取并生成独立数据集。

示例：检索包含潜在任务/奖励标记的 BG 卡
```js
async function searchPotentialQuestsRewards({ token, region = 'us', locale = 'zh_CN', page = 1, pageSize = 50 }) {
  const base = `https://${region}.api.blizzard.com/hearthstone/cards`
  const params = new URLSearchParams({ gameMode: 'battlegrounds', locale, page: String(page), pageSize: String(pageSize) })
  const res = await fetch(`${base}?${params.toString()}`, { headers: { Authorization: `Bearer ${token}` } })
  if (!res.ok) throw new Error(`Search failed: ${res.status}`)
  const data = await res.json()
  const cards = data.cards || []
  return cards.filter(c => c?.battlegrounds?.quest === true || c?.battlegrounds?.reward === true)
}
```

> 结论：可以收集“静态定义”，但无法通过官方 API 获知“某一局第 3 回合给你的三选一是什么”。