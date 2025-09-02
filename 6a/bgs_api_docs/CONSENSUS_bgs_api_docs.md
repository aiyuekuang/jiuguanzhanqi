# CONSENSUS_bgs_api_docs

## 明确的需求描述
- 在 `docs/` 下新增一份面向“酒馆战棋（Battlegrounds）”的 Hearthstone API 本地文档，便于离线查询与快速集成。
- 文档需覆盖：鉴权、端点清单、请求参数、示例、典型响应字段、速率与错误、最佳实践与陷阱。

## 验收标准
- `docs/api-docs.md` 存在且完整，章节齐全；所有端点均附参数说明与示例。
- 文档内引用官方文档链接并以 Markdown 链接标注来源：`https://develop.battle.net/documentation/hearthstone`。
- 涵盖 Battlegrounds 过滤维度：如 `gameMode=battlegrounds`，以及响应中 `battlegrounds` 字段（如 tier、techLevel、tribes、buddies 等若存在）。
- 含 OAuth 流程说明，并与 `6aScript/` 中现有脚本呼应（不泄露秘钥，提示使用 `.env`）。
- 示例如无真实 key 亦能作为模板直接替换运行。

## 技术实现方案
- 以单文件 `docs/api-docs.md` 起步：如内容超长，再拆分到 `docs/api/` 子目录并在主文档建立索引。
- 代码示例统一使用 `js` fenced code；使用 `yarn` 生态的依赖提示。
- 参考现有脚本 `6aScript/bnet_oauth.mjs`、`6aScript/fetch_bgs_from_api.mjs` 衔接说明。

## 组件与库
- Node.js fetch/axios（示例以 fetch 为主）。
- OAuth2 客户端凭证流（暴雪 Battle.net 开放平台）。
- dotenv（本地开发读取 `.env`）。

## 边界限制
- 不创建或改造官方 API，只做本地文档与调用示例；项目内部若以 POST 代理请求，属网关层设计，另行实现。
- 不包含非 Battlegrounds 视角的扩展指南（如构筑模式特性），除非与端点共享且与本任务必要。

## 不确定性处理
- 若官方文档字段或示例与实际响应存在差异，优先以线上实际返回为准，并在文档中标注“以实测为准”。
- 速率限制与错误码按官方描述并结合常见 HTTP 错误补充。

## 集成方案
- 文档示例支持直接在 `6aScript/` 新增调用脚本；后续可添加 `scripts:` 命令在 `package.json`。

## 最终共识
- 以 Battlegrounds 为主线完成第一版；保证可查、可用、可直接替换 token 运行。
