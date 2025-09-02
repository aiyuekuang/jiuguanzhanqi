### TypeScript 版采集与文档生成

#### 环境变量（.env）
```
BNET_CLIENT_ID=xxxxx
BNET_CLIENT_SECRET=xxxxx
BNET_REGION=us
BNET_LOCALE=zh_CN
```

#### 运行
```
yarn bgs:all
```

流程：
- `bgs:api:ts` 抓取酒馆战棋英雄/随从 JSON
- `bgs:docs:ts` 生成 `docs/` 下 Markdown（写入前会备份原文档）

参考文档：
- Card Search Guide（官方）：https://develop.battle.net/documentation/hearthstone/guides/card-search


