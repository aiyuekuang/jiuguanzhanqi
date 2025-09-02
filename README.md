# 炉石战棋项目

## 项目概述

这是一个炉石战棋相关的项目，包含数据收集、API文档生成、以及**智能识别辅助系统**。

## 主要功能

### 1. 数据收集
- 从炉石战棋API收集英雄、随从、元数据
- 下载媒体资源（英雄和随从图片）
- 生成结构化的JSON数据

### 2. API文档生成
- 基于收集的数据生成API文档
- 支持英雄、随从、元数据的查询
- 提供完整的API使用说明

### 3. 🆕 智能识别辅助系统
- **实时识别**炉石战棋游戏画面
- **智能分析**游戏状态和策略
- **MCP集成**，供Cursor调用
- **Overlay界面**，游戏内实时提示

## 🚀 快速开始

### 安装依赖
```bash
pip install -r src/coach/requirements.txt
```

### 启动识别系统
```bash
cd src/coach
python main.py
```

### 配置MCP（可选）
在项目根目录已有 `.cursor/mcp.json` 配置，重启Cursor即可使用MCP工具。

## 📁 项目结构

```
lushi/
├── .cursor/                 # Cursor MCP配置
├── 6a/                      # 6A工作流文档
├── 6aScript/                # 临时脚本
├── data/                    # 游戏数据
├── docs/                    # 项目文档
├── src/                     # 源代码
│   └── coach/              # 🆕 智能识别系统
├── static/                  # 静态资源
└── README.md               # 项目说明
```

## 🎮 智能识别系统特性

### 核心功能
- **图像识别**: 自动识别商店随从、我方场面、英雄信息
- **实时分析**: 100ms/帧，识别准确率>90%
- **智能建议**: 购买建议、站位建议、升级建议
- **数据服务**: WebSocket实时推送 + HTTP API

### MCP工具（6个）
1. `get_game_state` - 获取游戏状态
2. `get_recognition_status` - 获取服务状态  
3. `get_game_advice` - 获取游戏建议
4. `analyze_board` - 分析当前场面
5. `start_recognition` - 启动识别服务
6. `stop_recognition` - 停止识别服务

### Overlay界面
- **F8**: 显示/隐藏提示面板
- **F9**: 显示示例建议
- **F10**: 保存屏幕截图
- **F7**: 切换面板位置
- **F6**: 调整透明度
- **Esc**: 退出系统

## 📚 详细文档

- **使用说明**: [src/coach/README.md](src/coach/README.md)
- **MCP配置**: [docs/mcp-setup.md](docs/mcp-setup.md)
- **项目总结**: [6a/auto_coach/FINAL_auto_coach.md](6a/auto_coach/FINAL_auto_coach.md)
- **待办事项**: [6a/auto_coach/TODO_auto_coach.md](6a/auto_coach/TODO_auto_coach.md)

## 🔧 技术栈

- **图像识别**: OpenCV + 模板匹配
- **Web服务**: FastAPI + WebSocket
- **数据结构**: Python dataclass + JSON
- **MCP集成**: MCP协议 + 工具定义
- **界面系统**: tkinter + 热键控制

## ⚠️ 注意事项

- 确保Python 3.8+环境
- 游戏分辨率建议1920x1080
- 截图功能需要管理员权限
- 首次使用需要重启Cursor

## 📄 许可证

本项目仅供学习和研究使用，请勿用于商业用途。

---

**项目状态**: 🎉 开发完成，包含完整的智能识别辅助系统！
