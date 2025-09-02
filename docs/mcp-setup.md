# MCP配置详细说明

## 什么是MCP？

MCP (Model Context Protocol) 是一个开放协议，允许AI助手（如Cursor、Claude等）调用外部工具和服务。通过MCP，AI可以：

- 访问本地文件系统
- 调用外部API
- 执行本地脚本
- 获取实时数据
- 控制外部服务

## 我们的MCP服务

我们提供了一个炉石战棋识别辅助系统的MCP服务，包含以下功能：

### 可用工具列表

1. **get_game_state** - 获取当前游戏状态
   - 描述：获取当前游戏状态，包括商店随从、我方场面、英雄信息等
   - 参数：无
   - 返回：完整的游戏状态JSON数据

2. **get_recognition_status** - 获取识别服务状态
   - 描述：获取识别服务状态和连接信息
   - 参数：无
   - 返回：服务运行状态

3. **get_game_advice** - 获取游戏建议
   - 描述：基于当前游戏状态提供游戏建议
   - 参数：advice_type (buy/sell/position/upgrade)
   - 返回：具体的游戏建议和原因

4. **analyze_board** - 分析当前场面
   - 描述：分析当前场面，提供阵容建议
   - 参数：无
   - 返回：阵容分析结果和建议

5. **start_recognition** - 启动识别服务
   - 描述：启动游戏识别服务
   - 参数：无
   - 返回：启动状态

6. **stop_recognition** - 停止识别服务
   - 描述：停止游戏识别服务
   - 参数：无
   - 返回：停止状态

## 配置方法

### 方法1: 项目级配置（推荐）

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
      "description": "炉石战棋识别辅助系统MCP服务",
      "capabilities": {
        "tools": {
          "listChanged": true,
          "listChangedNotification": true
        }
      }
    }
  }
}
```

### 方法2: 工作区配置

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

### 方法3: 全局配置

在Cursor的全局配置中添加：

**Windows:**
```
%APPDATA%\Cursor\User\globalStorage\cursor.mcp\mcp_config.json
```

**macOS:**
```
~/Library/Application Support/Cursor/User/globalStorage/cursor.mcp/mcp_config.json
```

**Linux:**
```
~/.config/Cursor/User/globalStorage/cursor.mcp/mcp_config.json
```

## 配置步骤详解

### 步骤1: 安装依赖

确保已安装所有必要的Python包：

```bash
cd src/coach
pip install -r requirements.txt
```

### 步骤2: 创建配置文件

选择上述任一方法创建MCP配置文件。

### 步骤3: 验证配置

检查配置文件语法是否正确：

```bash
# 测试MCP服务器是否能正常启动
cd src/coach
python mcp_server.py
```

### 步骤4: 重启Cursor

配置完成后，重启Cursor使配置生效。

### 步骤5: 测试MCP工具

在Cursor中测试MCP工具是否可用：

1. 打开Cursor
2. 在聊天中输入工具名称，如"获取游戏状态"
3. 检查是否有相关工具被调用

## 故障排除

### 常见问题

1. **MCP工具不显示**
   - 检查配置文件语法是否正确
   - 确认Python路径是否正确
   - 重启Cursor

2. **工具调用失败**
   - 检查依赖是否安装完整
   - 确认MCP服务器是否能正常启动
   - 查看错误日志

3. **路径问题**
   - 确认相对路径是否正确
   - 检查PYTHONPATH设置
   - 使用绝对路径测试

### 调试方法

1. **检查日志**
   - 在Cursor中查看MCP相关日志
   - 检查Python脚本的输出

2. **测试独立运行**
   - 单独运行MCP服务器
   - 测试各个工具功能

3. **验证环境**
   - 检查Python版本
   - 确认包依赖
   - 验证文件权限

## 高级配置

### 自定义工具

可以在 `mcp_server.py` 中添加新的工具：

```python
Tool(
    name="custom_tool",
    description="自定义工具描述",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        }
    }
)
```

### 环境变量配置

可以在配置文件中添加更多环境变量：

```json
{
  "env": {
    "PYTHONPATH": ".",
    "CUSTOM_VAR": "value",
    "DEBUG": "true"
  }
}
```

### 多服务器配置

可以配置多个MCP服务器：

```json
{
  "mcpServers": {
    "hearthstone-coach": { ... },
    "other-service": { ... }
  }
}
```

## 使用示例

### 在Cursor中使用

1. **获取游戏状态**
   ```
   请帮我获取当前炉石战棋的游戏状态
   ```

2. **获取游戏建议**
   ```
   基于当前游戏状态，给我一些购买建议
   ```

3. **分析场面**
   ```
   分析一下我当前的场面，有什么建议吗？
   ```

### 工具调用示例

```python
# 获取游戏状态
result = await call_tool("get_game_state", {})

# 获取购买建议
advice = await call_tool("get_game_advice", {"advice_type": "buy"})

# 分析场面
analysis = await call_tool("analyze_board", {})
```

## 注意事项

1. **安全性**
   - MCP工具可以访问本地系统
   - 确保只运行可信的脚本
   - 注意文件权限设置

2. **性能**
   - MCP调用会增加响应时间
   - 避免在工具中执行耗时操作
   - 合理使用缓存机制

3. **兼容性**
   - 确保Python版本兼容
   - 检查依赖包版本
   - 测试不同操作系统

## 更新和维护

### 更新工具

1. 修改 `mcp_server.py`
2. 更新配置文件（如需要）
3. 重启MCP服务

### 监控服务

1. 检查服务状态
2. 监控错误日志
3. 定期测试功能

### 版本管理

1. 记录配置变更
2. 备份配置文件
3. 测试新功能
