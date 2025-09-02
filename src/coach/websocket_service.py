"""
WebSocket服务模块
提供实时游戏状态数据推送
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from recognition_engine import RecognitionEngine, GameState
import cv2
import numpy as np
from datetime import datetime


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.recognition_engine = RecognitionEngine()
        self.last_game_state: Optional[GameState] = None
    
    async def connect(self, websocket: WebSocket):
        """处理新的WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"新的WebSocket连接，当前连接数: {len(self.active_connections)}")
        
        # 发送当前游戏状态（如果有）
        if self.last_game_state:
            await websocket.send_text(json.dumps(vars(self.last_game_state), ensure_ascii=False))
    
    def disconnect(self, websocket: WebSocket):
        """处理WebSocket连接断开"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")
    
    async def broadcast(self, message: str):
        """广播消息给所有连接的客户端"""
        if self.active_connections:
            # 创建任务列表，并行发送给所有客户端
            tasks = []
            for connection in self.active_connections:
                try:
                    tasks.append(connection.send_text(message))
                except Exception as e:
                    print(f"发送消息失败: {e}")
                    # 标记连接为无效
                    connection.close()
            
            # 并行执行所有发送任务
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # 清理无效连接
            self.active_connections = [conn for conn in self.active_connections if not conn.closed]
    
    async def process_frame(self, frame: np.ndarray):
        """处理新的游戏帧"""
        try:
            # 使用识别引擎识别游戏状态
            game_state = self.recognition_engine.recognize_frame(frame)
            self.last_game_state = game_state
            
            # 转换为JSON并广播
            game_state_dict = vars(game_state)
            message = json.dumps(game_state_dict, ensure_ascii=False)
            await self.broadcast(message)
            
        except Exception as e:
            print(f"处理游戏帧失败: {e}")
            # 发送错误状态
            error_state = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }
            await self.broadcast(json.dumps(error_state))


# 创建FastAPI应用
app = FastAPI(title="炉石战棋识别服务", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建WebSocket管理器实例
websocket_manager = WebSocketManager()


@app.get("/")
async def root():
    """根路径"""
    return {"message": "炉石战棋识别服务", "status": "running"}


@app.get("/api/status")
async def get_status():
    """获取服务状态"""
    return {
        "status": "running",
        "active_connections": len(websocket_manager.active_connections),
        "last_update": websocket_manager.last_game_state.timestamp if websocket_manager.last_game_state else None
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点"""
    await websocket_manager.connect(websocket)
    try:
        # 保持连接活跃
        while True:
            # 等待客户端消息（心跳检测）
            data = await websocket.receive_text()
            # 可以在这里处理客户端发送的消息
            print(f"收到客户端消息: {data}")
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket错误: {e}")
        websocket_manager.disconnect(websocket)


@app.post("/api/process-frame")
async def process_frame_endpoint(frame_data: Dict[str, Any]):
    """处理游戏帧的HTTP端点（用于测试）"""
    try:
        # 这里应该接收实际的图像数据
        # 暂时返回模拟数据
        return {"status": "success", "message": "帧处理请求已接收"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# 启动函数
async def start_websocket_service():
    """启动WebSocket服务"""
    import uvicorn
    
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
