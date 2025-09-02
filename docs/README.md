# 炉石战棋项目

## 项目概述

这是一个炉石战棋相关的项目，包含数据收集、API文档生成、以及智能识别辅助系统。

## 主要功能

### 1. 数据收集
- 从炉石战棋API收集英雄、随从、元数据
- 下载媒体资源（英雄和随从图片）
- 生成结构化的JSON数据

### 2. API文档生成
- 基于收集的数据生成API文档
- 支持英雄、随从、元数据的查询
- 提供完整的API使用说明

### 3. 智能识别辅助系统
- 实时识别炉石战棋游戏画面
- 提供游戏建议和策略分析
- 支持MCP集成，供Cursor调用

## MCP配置

### 什么是MCP？
MCP (Model Context Protocol) 是一个协议，允许AI助手（如Cursor）调用外部工具和服务。

### 配置方法

#### 方法1: 项目级配置（推荐）
在项目根目录创建 `.cursor/mcp_config.json` 文件：

```json
{
  "mcpServers": {
    "hearthstone-coach": {
      "command": "python",
      "args": ["src/coach/mcp_server.py"],
      "env": {
        "PYTHONPATH": "."
      },
      "description": "炉石战棋识别辅助系统MCP服务"
    }
  }
}
```

#### 方法2: 工作区配置
在 `.vscode/settings.json` 中添加：

```json
{
  "mcp.servers": {
    "hearthstone-coach": {
      "command": "python",
      "args": ["src/coach/mcp_server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  },
  "mcp.enabled": true
}
```

### 可用的MCP工具

配置完成后，Cursor可以使用以下工具：

1. **get_game_state** - 获取当前游戏状态
2. **get_recognition_status** - 获取识别服务状态
3. **get_game_advice** - 获取游戏建议
4. **analyze_board** - 分析当前场面
5. **start_recognition** - 启动识别服务
6. **stop_recognition** - 停止识别服务

### 使用方法

1. 确保项目依赖已安装：`pip install -r src/coach/requirements.txt`
2. 配置MCP配置文件
3. 重启Cursor
4. 在Cursor中直接调用工具名称即可

## 项目结构

```
lushi/
├── .cursor/                 # Cursor MCP配置
├── .vscode/                 # VSCode/Cursor工作区配置
├── 6a/                      # 6A工作流文档
├── 6aScript/                # 临时脚本
├── data/                    # 游戏数据
├── docs/                    # 项目文档
├── src/                     # 源代码
│   └── coach/              # 智能识别系统
├── static/                  # 静态资源
└── README.md               # 项目说明
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r src/coach/requirements.txt
```

### 2. 配置MCP
按照上述方法配置MCP

### 3. 启动识别系统
```bash
cd src/coach
python main.py
```

### 4. 在Cursor中使用
直接输入工具名称，如：
- "获取游戏状态"
- "分析当前场面"
- "获取购买建议"

## 注意事项

- 确保Python环境已正确配置
- 项目路径配置要正确
- 首次使用需要重启Cursor
- 识别系统需要游戏画面在前台

## 许可证

本项目仅供学习和研究使用。
