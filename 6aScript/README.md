### 6aScript 使用说明（官方 API 版）

#### 环境变量（.env）
```
BNET_CLIENT_ID=xxxxx
BNET_CLIENT_SECRET=xxxxx
BNET_REGION=us   # us|eu|kr|tw|cn
BNET_LOCALE=zh_CN
```

将 `.env` 放在项目根目录（不要提交到 Git）。

#### 安装依赖
项目已使用 Yarn（v4），无需额外依赖即可运行（Node 18+）。

#### 运行
```
yarn bgs:api
```

输出：`6aScript/output/` 目录下生成 `bgs_heroes_<region>_<locale>.json` 与 `bgs_minions_<region>_<locale>.json`。

#### 说明
- 所有请求均使用 `gameMode=battlegrounds` 区分酒馆战棋。
- 英雄与随从分别通过 `type=hero|minion` 获取并分页抓取。
- 参考文档：
  - Card Search Guide（官方）：https://develop.battle.net/documentation/hearthstone/guides/card-search


