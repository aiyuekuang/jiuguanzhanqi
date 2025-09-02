"""
炉石战棋识别辅助系统主程序
整合识别引擎、WebSocket服务和Overlay界面
"""

import asyncio
import threading
import time
import cv2
import numpy as np
from pathlib import Path
import sys
import os
from typing import Optional

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recognition_engine import RecognitionEngine
from websocket_service import WebSocketManager
from overlay_coach import CoachApp


class GameRecognitionSystem:
    """游戏识别系统主类"""
    
    def __init__(self):
        self.recognition_engine = RecognitionEngine()
        self.websocket_manager = WebSocketManager()
        self.running = False
        self.recognition_thread = None
        
        # 创建输出目录
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
    
    def start_recognition_loop(self):
        """启动识别循环"""
        self.running = True
        self.recognition_thread = threading.Thread(target=self._recognition_worker, daemon=True)
        self.recognition_thread.start()
        print("识别循环已启动")
    
    def stop_recognition_loop(self):
        """停止识别循环"""
        self.running = False
        if self.recognition_thread:
            self.recognition_thread.join()
        print("识别循环已停止")
    
    def _recognition_worker(self):
        """识别工作线程"""
        while self.running:
            try:
                # 截取屏幕
                frame = self._capture_screen()
                if frame is not None:
                    # 处理帧
                    asyncio.run(self.websocket_manager.process_frame(frame))
                
                # 控制识别频率
                time.sleep(0.1)  # 100ms间隔
                
            except Exception as e:
                print(f"识别循环错误: {e}")
                time.sleep(1)  # 出错时等待更长时间
    
    def _capture_screen(self) -> Optional[np.ndarray]:
        """截取屏幕"""
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            
            # 获取屏幕尺寸
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
            
            # 创建设备上下文
            hdc_screen = user32.GetDC(0)
            hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
            hbm = gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
            gdi32.SelectObject(hdc_mem, hbm)
            
            # 复制屏幕内容
            SRCCOPY = 0x00CC0020
            gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc_screen, 0, 0, SRCCOPY)
            
            # 获取位图数据
            class BITMAPINFO(ctypes.Structure):
                _fields_ = [
                    ("bmiHeader", ctypes.c_uint32 * 11),
                    ("bmiColors", ctypes.c_uint32 * 3)
                ]
            
            bmi = BITMAPINFO()
            bmi.bmiHeader[0] = ctypes.sizeof(BITMAPINFO)
            bmi.bmiHeader[1] = width
            bmi.bmiHeader[2] = -height  # top-down
            bmi.bmiHeader[3] = 1
            bmi.bmiHeader[4] = 24
            bmi.bmiHeader[5] = 0
            
            # 分配缓冲区
            buf_len = ((width * 3 + 3) & ~3) * height
            buf = ctypes.create_string_buffer(buf_len)
            
            # 获取位图数据
            gdi32.GetDIBits(hdc_mem, hbm, 0, height, buf, ctypes.byref(bmi), 0)
            
            # 转换为numpy数组
            frame = np.frombuffer(buf, dtype=np.uint8)
            frame = frame.reshape((height, width, 3))
            
            # 转换颜色空间（BGR -> RGB）
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 清理资源
            gdi32.DeleteObject(hbm)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(0, hdc_screen)
            
            return frame
            
        except Exception as e:
            print(f"屏幕截取失败: {e}")
            return None
    
    async def start_websocket_service(self):
        """启动WebSocket服务"""
        from websocket_service import start_websocket_service
        await start_websocket_service()
    
    def start_overlay(self):
        """启动Overlay界面"""
        try:
            app = CoachApp()
            app.exec()
        except Exception as e:
            print(f"Overlay启动失败: {e}")


def main():
    """主函数"""
    print("启动炉石战棋识别辅助系统...")
    
    # 创建系统实例
    system = GameRecognitionSystem()
    
    try:
        # 启动识别循环
        system.start_recognition_loop()
        
        # 启动Overlay界面（在新线程中）
        overlay_thread = threading.Thread(target=system.start_overlay, daemon=True)
        overlay_thread.start()
        
        # 启动WebSocket服务
        print("启动WebSocket服务...")
        asyncio.run(system.start_websocket_service())
        
    except KeyboardInterrupt:
        print("\n收到中断信号，正在关闭...")
    except Exception as e:
        print(f"系统运行错误: {e}")
    finally:
        # 清理资源
        system.stop_recognition_loop()
        print("系统已关闭")


if __name__ == "__main__":
    main()
