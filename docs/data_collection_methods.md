# 酒馆战棋数据获取方法文档

## 概述
本文档详细说明了从官方酒馆战棋浏览器获取各种数据的具体方法和步骤。

## 数据获取方法

### 1. 随从数据获取方法

#### 1.1 1级随从数据
- **网站地址**：https://hs.blizzard.cn/battlegrounds/?sort=tier%3Aasc
- **获取方法**：
  1. 打开网站，等待页面完全加载
  2. 页面会自动显示按等级排序的随从
  3. 使用 `chrome_get_web_content` 获取HTML内容
  4. 解析HTML中的随从信息（名称、攻击力、生命值、种族、特殊能力等）
  5. 将数据写入对应的markdown文件

#### 1.2 2-6级随从数据
- **获取方法**：
  1. 在同一个页面，随从会按等级分组显示
  2. 每个等级组都有标题标识（如"酒馆等级2"、"酒馆等级3"等）
  3. 使用相同的HTML解析方法获取各等级随从数据
  4. 分别写入对应的tier文件

### 2. 法术数据获取方法

#### 2.1 酒馆法术
- **获取方法**：
  1. 在主页面上，法术会显示在特定的区域
  2. 使用 `chrome_get_web_content` 获取包含法术信息的HTML
  3. 解析法术的名称、费用、描述等信息
  4. 写入法术数据文件

### 3. 英雄数据获取方法

#### 3.1 英雄列表获取
- **获取方法**：
  1. 在主页面上，英雄会显示在"英雄"分组中
  2. 使用 `chrome_get_web_content` 获取英雄列表的HTML
  3. 解析英雄的名称和基本信息

#### 3.2 英雄详细信息获取
- **重要**：英雄的详细信息需要点击每张英雄卡牌才能获取
- **获取步骤**：
  1. 点击第一张英雄卡牌
  2. 使用 `chrome_screenshot` 截图获取英雄详细信息
  3. 解析截图中的英雄技能名称、描述、费用等信息
  4. 点击"下一张"或关闭当前英雄详情
  5. 重复步骤1-4，直到获取所有英雄的详细信息

#### 3.3 英雄数据获取工具使用
```javascript
// 点击英雄卡牌
chrome_click_element(selector: ".card_list_item.hero-card")

// 截图获取详细信息
chrome_screenshot(storeBase64: true, fullPage: false)

// 点击关闭或下一张
chrome_click_element(selector: ".close-button")
```

### 4. 数据解析方法

#### 4.1 HTML解析
- 使用正则表达式或DOM解析器提取卡牌信息
- 关键字段：名称、攻击力、生命值、种族、特殊能力、费用等

#### 4.2 截图解析
- 对于英雄详细信息，需要从截图中识别文字信息
- 可以使用OCR技术或手动解析截图内容

### 5. 数据存储格式

#### 5.1 Markdown格式
```markdown
### 1. 随从名称
- **攻击力**：X
- **生命值**：X
- **种族**：种族名称
- **特殊能力**：能力描述
- **获取方式**：鲍勃酒馆
- **金色版本**：X/X，能力描述
```

#### 5.2 文件组织结构
```
docs/
├── minions/
│   ├── tier1_minions.md
│   ├── tier2_minions.md
│   ├── tier3_minions.md
│   ├── tier4_minions.md
│   ├── tier5_minions.md
│   └── tier6_minions.md
├── heroes/
│   └── heroes_data.md
├── spells/
│   └── spells_data.md
└── data_collection_methods.md
```

### 6. 注意事项

#### 6.1 页面加载
- 确保页面完全加载后再获取数据
- 使用 `Wait-Tool` 等待页面稳定

#### 6.2 数据准确性
- 定期验证数据的准确性
- 注意游戏更新可能导致的数据变化

#### 6.3 错误处理
- 如果获取失败，记录错误并重试
- 对于部分数据缺失，标记并后续补充

### 7. 自动化脚本建议

#### 7.1 随从数据获取脚本
```javascript
// 伪代码
function getMinionData() {
    navigateToBattlegroundsPage();
    waitForPageLoad();
    const htmlContent = getWebContent();
    const minions = parseMinionData(htmlContent);
    writeToMarkdownFiles(minions);
}
```

#### 7.2 英雄数据获取脚本
```javascript
// 伪代码
function getHeroData() {
    navigateToBattlegroundsPage();
    const heroList = getHeroList();
    
    for (let hero of heroList) {
        clickHeroCard(hero);
        const screenshot = takeScreenshot();
        const heroData = parseHeroData(screenshot);
        saveHeroData(heroData);
        closeHeroDetails();
    }
}
```

## 更新日志
- 2025-01-XX：创建初始文档
- 2025-01-XX：添加英雄数据获取方法
- 2025-01-XX：完善数据解析说明
