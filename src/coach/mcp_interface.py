"""
MCP集成接口
提供MCP工具供Cursor调用，实现游戏辅助功能
"""

import json
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class MCPTool:
    """MCP工具定义"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    outputSchema: Dict[str, Any]


class MCPInterface:
    """MCP接口管理器"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:8000"):
        self.api_base_url = api_base_url
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[MCPTool]:
        """定义可用的MCP工具"""
        return [
            MCPTool(
                name="get_game_state",
                description="获取当前游戏状态，包括商店随从、我方场面、英雄信息等",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                outputSchema={
                    "type": "object",
                    "properties": {
                        "timestamp": {"type": "string"},
                        "tavern_tier": {"type": "integer"},
                        "gold": {"type": "integer"},
                        "turn": {"type": "integer"},
                        "hero": {"type": "object"},
                        "shop": {"type": "object"},
                        "board": {"type": "object"}
                    }
                }
            ),
            MCPTool(
                name="get_recognition_status",
                description="获取识别服务状态和连接信息",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                outputSchema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "active_connections": {"type": "integer"},
                        "last_update": {"type": "string"}
                    }
                }
            ),
            MCPTool(
                name="get_game_advice",
                description="基于当前游戏状态提供游戏建议",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "advice_type": {
                            "type": "string",
                            "enum": ["buy", "sell", "position", "upgrade"],
                            "description": "建议类型：购买、出售、站位、升级"
                        }
                    },
                    "required": ["advice_type"]
                },
                outputSchema={
                    "type": "object",
                    "properties": {
                        "advice": {"type": "string"},
                        "reason": {"type": "string"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                    }
                }
            ),
            MCPTool(
                name="analyze_board",
                description="分析当前场面，提供阵容建议",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                outputSchema={
                    "type": "object",
                    "properties": {
                        "current_composition": {"type": "string"},
                        "strength": {"type": "string"},
                        "suggestions": {"type": "array", "items": {"type": "string"}}
                    }
                }
            )
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """获取所有可用工具的列表"""
        return [asdict(tool) for tool in self.tools]
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行指定的MCP工具"""
        try:
            if tool_name == "get_game_state":
                return self._get_game_state()
            elif tool_name == "get_recognition_status":
                return self._get_recognition_status()
            elif tool_name == "get_game_advice":
                return self._get_game_advice(parameters.get("advice_type", "buy"))
            elif tool_name == "analyze_board":
                return self._analyze_board()
            else:
                return {"error": f"未知工具: {tool_name}"}
        except Exception as e:
            return {"error": f"工具执行失败: {str(e)}"}
    
    def _get_game_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        try:
            response = requests.get(f"{self.api_base_url}/api/status")
            if response.status_code == 200:
                status = response.json()
                # 这里应该返回完整的游戏状态
                # 暂时返回模拟数据
                return {
                    "timestamp": status.get("last_update", "2024-01-01T00:00:00Z"),
                    "tavern_tier": 6,
                    "gold": 10,
                    "turn": 8,
                    "hero": {
                        "name": "Reno Jackson",
                        "health": 25,
                        "armor": 9
                    },
                    "shop": {
                        "frozen": False,
                        "minions": [
                            {
                                "position": 0,
                                "name": "Kalecgos",
                                "attack": 2,
                                "health": 6,
                                "tier": 6,
                                "tribe": "dragon",
                                "golden": False
                            }
                        ]
                    },
                    "board": {
                        "minions": [
                            {
                                "position": 0,
                                "name": "Bronze Warden",
                                "attack": 8,
                                "health": 56,
                                "golden": True,
                                "divine_shield": True,
                                "reborn": True
                            }
                        ]
                    }
                }
            else:
                return {"error": f"API请求失败: {response.status_code}"}
        except requests.RequestException as e:
            return {"error": f"网络请求失败: {str(e)}"}
    
    def _get_recognition_status(self) -> Dict[str, Any]:
        """获取识别服务状态"""
        try:
            response = requests.get(f"{self.api_base_url}/api/status")
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API请求失败: {response.status_code}"}
        except requests.RequestException as e:
            return {"error": f"网络请求失败: {str(e)}"}
    
    def _get_game_advice(self, advice_type: str) -> Dict[str, Any]:
        """获取游戏建议"""
        # 基于当前游戏状态提供建议
        game_state = self._get_game_state()
        if "error" in game_state:
            return game_state
        
        if advice_type == "buy":
            shop_minions = game_state.get("shop", {}).get("minions", [])
            if shop_minions:
                best_minion = max(shop_minions, key=lambda x: x.get("tier", 0))
                return {
                    "advice": f"建议购买 {best_minion['name']}",
                    "reason": f"这是商店中最高等级的随从（{best_minion['tier']}星）",
                    "priority": "high"
                }
            else:
                return {
                    "advice": "商店中没有随从，建议刷新",
                    "reason": "商店为空，需要刷新寻找更好的选择",
                    "priority": "medium"
                }
        
        elif advice_type == "position":
            board_minions = game_state.get("board", {}).get("minions", [])
            if board_minions:
                # 简单的站位建议
                return {
                    "advice": "圣盾随从放前排，高攻击随从放后排",
                    "reason": "保护圣盾随从，最大化输出",
                    "priority": "medium"
                }
            else:
                return {
                    "advice": "暂无随从，无需考虑站位",
                    "reason": "场面上没有随从",
                    "priority": "low"
                }
        
        elif advice_type == "upgrade":
            current_tier = game_state.get("tavern_tier", 1)
            if current_tier < 6:
                return {
                    "advice": f"建议升级到 {current_tier + 1} 本",
                    "reason": "升级可以获得更高等级的随从",
                    "priority": "high"
                }
            else:
                return {
                    "advice": "已达到最高等级，无需升级",
                    "reason": "当前已经是6本，无法继续升级",
                    "priority": "low"
                }
        
        else:
            return {
                "advice": "建议类型无效",
                "reason": f"不支持的建议类型: {advice_type}",
                "priority": "low"
            }
    
    def _analyze_board(self) -> Dict[str, Any]:
        """分析当前场面"""
        game_state = self._get_game_state()
        if "error" in game_state:
            return game_state
        
        board_minions = game_state.get("board", {}).get("minions", [])
        if not board_minions:
            return {
                "current_composition": "空场",
                "strength": "极弱",
                "suggestions": ["尽快购买随从", "考虑升级酒馆"]
            }
        
        # 分析种族构成
        tribes = {}
        golden_count = 0
        total_attack = 0
        total_health = 0
        
        for minion in board_minions:
            tribe = minion.get("tribe", "neutral")
            tribes[tribe] = tribes.get(tribe, 0) + 1
            if minion.get("golden", False):
                golden_count += 1
            total_attack += minion.get("attack", 0)
            total_health += minion.get("health", 0)
        
        # 确定主要种族
        main_tribe = max(tribes.items(), key=lambda x: x[1])[0] if tribes else "neutral"
        
        # 评估强度
        if len(board_minions) >= 7 and golden_count >= 3:
            strength = "极强"
        elif len(board_minions) >= 5 and golden_count >= 1:
            strength = "强"
        elif len(board_minions) >= 3:
            strength = "中等"
        else:
            strength = "弱"
        
        # 生成建议
        suggestions = []
        if len(board_minions) < 7:
            suggestions.append("继续购买随从填满场面")
        if golden_count == 0:
            suggestions.append("寻找机会制作金色随从")
        if main_tribe != "neutral" and tribes[main_tribe] >= 3:
            suggestions.append(f"继续强化{main_tribe}种族阵容")
        
        return {
            "current_composition": f"{main_tribe}种族阵容 ({tribes.get(main_tribe, 0)}个)",
            "strength": strength,
            "suggestions": suggestions
        }


# 测试代码
if __name__ == "__main__":
    interface = MCPInterface()
    
    # 测试工具列表
    print("可用工具:")
    for tool in interface.get_tools():
        print(f"- {tool['name']}: {tool['description']}")
    
    # 测试游戏状态获取
    print("\n游戏状态:")
    game_state = interface.execute_tool("get_game_state", {})
    print(json.dumps(game_state, ensure_ascii=False, indent=2))
    
    # 测试游戏建议
    print("\n购买建议:")
    advice = interface.execute_tool("get_game_advice", {"advice_type": "buy"})
    print(json.dumps(advice, ensure_ascii=False, indent=2))
    
    # 测试场面分析
    print("\n场面分析:")
    analysis = interface.execute_tool("analyze_board", {})
    print(json.dumps(analysis, ensure_ascii=False, indent=2))
