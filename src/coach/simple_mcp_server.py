#!/usr/bin/env python3
"""
简化的MCP服务器 - 炉石战棋识别辅助系统
不依赖外部库，提供基本的MCP功能
"""

import json
import sys
import time
from typing import Dict, Any

class SimpleMCPServer:
    """简化的MCP服务器实现"""
    
    def __init__(self):
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
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """执行MCP工具"""
        if tool_name == "get_game_state":
            return {
                "status": "success",
                "data": {
                    "shop_minions": [
                        {"name": "示例随从1", "attack": 3, "health": 3, "tier": 2},
                        {"name": "示例随从2", "attack": 4, "health": 4, "tier": 3}
                    ],
                    "board_minions": [
                        {"name": "我方随从1", "attack": 5, "health": 5, "position": 1}
                    ],
                    "hero": {"name": "示例英雄", "health": 30, "armor": 5},
                    "gold": 7,
                    "tavern_tier": 4,
                    "turn": 8
                }
            }
        
        elif tool_name == "get_recognition_status":
            return {
                "status": "success",
                "data": {
                    "is_running": True,
                    "recognition_frequency": "100ms",
                    "accuracy": ">90%",
                    "last_update": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            }
        
        elif tool_name == "get_game_advice":
            advice_type = arguments.get("advice_type", "general")
            if advice_type == "buy":
                return {
                    "status": "success",
                    "advice": "建议购买商店中的3/3随从，性价比很高",
                    "reason": "当前回合需要提升场面质量"
                }
            elif advice_type == "position":
                return {
                    "status": "success",
                    "advice": "将攻击力高的随从放在右侧",
                    "reason": "优先攻击敌方随从"
                }
            elif advice_type == "upgrade":
                return {
                    "status": "success",
                    "advice": "建议升级到5本",
                    "reason": "当前金币充足，可以寻找更强随从"
                }
            else:
                return {
                    "status": "success",
                    "advice": "保持经济平衡，不要过度升级",
                    "reason": "稳定发展比冒险升级更安全"
                }
        
        elif tool_name == "analyze_board":
            return {
                "status": "success",
                "analysis": {
                    "strength": "中等",
                    "synergy": "机械种族配合良好",
                    "weakness": "缺少嘲讽随从",
                    "recommendation": "考虑添加嘲讽随从保护后排"
                }
            }
        
        elif tool_name == "start_recognition":
            return {
                "status": "success",
                "message": "识别服务启动中...",
                "note": "请确保游戏画面可见"
            }
        
        elif tool_name == "stop_recognition":
            return {
                "status": "success",
                "message": "识别服务已停止"
            }
        
        else:
            return {
                "status": "error",
                "message": f"未知工具: {tool_name}"
            }
    
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
                result = self.execute_tool(tool_name, tool_args)
                
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
                    "message": f"Internal error: {str(e)}"
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
