#!/usr/bin/env python3
"""
MCP服务器 - 炉石战棋识别辅助系统
提供6个MCP工具供Cursor调用
"""

import json
import sys
import traceback
from typing import Dict, Any, List
from mcp_interface import MCPInterface

class SimpleMCPServer:
    """简化的MCP服务器实现"""
    
    def __init__(self):
        self.mcp_interface = MCPInterface()
        self.tools = [
            {
                "name": "get_game_state",
                "description": "获取当前游戏状态，包括商店随从、我方场面、英雄信息等",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_recognition_status",
                "description": "获取识别服务状态，包括是否运行、识别频率等",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_game_advice",
                "description": "获取游戏建议，包括购买建议、站位建议、升级建议等",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "advice_type": {
                            "type": "string",
                            "enum": ["buy", "position", "upgrade", "general"],
                            "description": "建议类型：购买、站位、升级、通用"
                        }
                    },
                    "required": ["advice_type"]
                }
            },
            {
                "name": "analyze_board",
                "description": "分析当前场面，评估随从组合和策略",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "start_recognition",
                "description": "启动识别服务，开始实时识别游戏画面",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "stop_recognition",
                "description": "停止识别服务",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                # 调用对应的工具
                result = self.mcp_interface.execute_tool(tool_name, tool_args)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                    "data": traceback.format_exc()
                }
            }
    
    def run(self):
        """运行MCP服务器"""
        print("MCP服务器启动中...", file=sys.stderr)
        print("支持的工具:", file=sys.stderr)
        for tool in self.tools:
            print(f"  - {tool['name']}: {tool['description']}", file=sys.stderr)
        print("等待请求...", file=sys.stderr)
        
        try:
            while True:
                # 读取标准输入
                line = input()
                if not line.strip():
                    continue
                
                try:
                    request = json.loads(line)
                    response = self.handle_request(request)
                    
                    # 输出响应到标准输出
                    print(json.dumps(response, ensure_ascii=False))
                    sys.stdout.flush()
                    
                except json.JSONDecodeError:
                    print(json.dumps({
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }))
                    sys.stdout.flush()
                    
        except EOFError:
            print("MCP服务器关闭", file=sys.stderr)
        except KeyboardInterrupt:
            print("MCP服务器被中断", file=sys.stderr)

if __name__ == "__main__":
    server = SimpleMCPServer()
    server.run()
