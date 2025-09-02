# 炉石战棋识别辅助系统

## 系统概述

这是一个完整的炉石战棋识别辅助系统，包含：
- 实时图像识别引擎
- WebSocket数据服务
- MCP集成接口
- Overlay游戏界面

## 功能特性

### 1. 图像识别
- 自动识别商店随从
- 识别我方场面
- 识别英雄信息
- 识别游戏状态（金币、等级、回合等）

### 2. 数据服务
- WebSocket实时数据推送
- HTTP API接口
- 结构化游戏数据输出

### 3. MCP集成
- 提供MCP工具供Cursor调用
- 游戏状态查询
- 游戏建议生成
- 场面分析

### 4. Overlay界面
- 游戏内覆盖显示
- 实时状态提示
- 热键控制

## 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 或者使用conda
conda install opencv numpy fastapi uvicorn requests pillow
```

## 使用方法

### 1. 启动系统

```bash
# 进入coach目录
cd src/coach

# 启动主程序
python main.py
```

### 2. 使用Overlay界面

启动后会出现游戏覆盖界面，热键说明：
- **F8**: 显示/隐藏提示面板
- **F9**: 显示示例建议
- **F10**: 保存当前屏幕截图
- **F7**: 切换面板位置
- **F6**: 调整透明度
- **Esc**: 退出系统

### 3. 访问Web服务

系统启动后，可以通过以下方式访问：

- **WebSocket**: `ws://127.0.0.1:8000/ws`
- **HTTP API**: `http://127.0.0.1:8000/api/`
- **状态查询**: `http://127.0.0.1:8000/api/status`

### 4. MCP工具使用

系统提供以下MCP工具：

#### get_game_state
获取当前游戏状态
```json
{
  "name": "get_game_state",
  "description": "获取当前游戏状态，包括商店随从、我方场面、英雄信息等",
  "inputSchema": {},
  "outputSchema": {
    "timestamp": "string",
    "tavern_tier": "integer",
    "gold": "integer",
    "turn": "integer",
    "hero": "object",
    "shop": "object",
    "board": "object"
  }
}
```

#### get_game_advice
获取游戏建议
```json
{
  "name": "get_game_advice",
  "description": "基于当前游戏状态提供游戏建议",
  "inputSchema": {
    "advice_type": {
      "type": "string",
      "enum": ["buy", "sell", "position", "upgrade"]
    }
  }
}
```

#### analyze_board
分析当前场面
```json
{
  "name": "analyze_board",
  "description": "分析当前场面，提供阵容建议",
  "inputSchema": {},
  "outputSchema": {
    "current_composition": "string",
    "strength": "string",
    "suggestions": ["string"]
  }
}
```

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   游戏画面      │    │   识别引擎      │    │   数据服务      │
│                │───▶│                │───▶│                │
│   实时截屏      │    │   模板匹配      │    │   结构化输出    │
└─────────────────┘    │   OCR识别       │    │   WebSocket     │
                       │   特征提取      │    │   MCP接口       │
                       └─────────────────┘    └─────────────────┘
```

## 配置说明

### 1. ROI配置

在`recognition_engine.py`中可以调整游戏界面ROI：

```python
self.rois = {
    "shop": (400, 200, 800, 400),      # 商店区域
    "board": (400, 600, 800, 300),     # 我方场面
    "hero": (100, 800, 200, 200),      # 英雄区域
    "gold": (1600, 800, 100, 50),      # 金币区域
    "tavern_tier": (1600, 700, 100, 50), # 酒馆等级
    "turn": (1600, 600, 100, 50),      # 回合数
}
```

### 2. 识别频率

在`main.py`中可以调整识别频率：

```python
time.sleep(0.1)  # 100ms间隔
```

### 3. 服务端口

在`websocket_service.py`中可以调整服务端口：

```python
uvicorn.run(app, host="127.0.0.1", port=8000)
```

## 故障排除

### 1. 识别不准确
- 检查游戏分辨率是否为1920x1080
- 调整ROI坐标
- 检查模板图片是否完整

### 2. 服务启动失败
- 检查端口8000是否被占用
- 确认依赖安装完整
- 检查防火墙设置

### 3. Overlay不显示
- 以管理员权限运行
- 检查显示器缩放设置
- 确认tkinter正常工作

## 开发说明

### 1. 添加新的识别功能

1. 在`recognition_engine.py`中添加新的识别方法
2. 在`GameState`中添加相应的数据字段
3. 更新WebSocket服务的数据推送

### 2. 添加新的MCP工具

1. 在`mcp_interface.py`中定义新的工具
2. 实现工具的执行逻辑
3. 更新工具列表

### 3. 自定义Overlay界面

1. 修改`overlay_coach.py`中的界面逻辑
2. 添加新的热键和功能
3. 调整界面样式和布局

## 性能优化

### 1. 识别性能
- 使用ROI缓存减少重复计算
- 并行处理多个识别任务
- 优化模板匹配算法

### 2. 服务性能
- 使用连接池管理WebSocket连接
- 实现数据压缩和缓存
- 异步处理请求

### 3. 系统资源
- 控制识别频率
- 及时释放图像数据
- 监控系统资源使用

## 许可证

本项目仅供学习和研究使用，请勿用于商业用途。
