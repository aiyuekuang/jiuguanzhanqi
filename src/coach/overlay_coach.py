import sys
import time
import os
from threading import Thread, Event
import tkinter as tk
import ctypes
from ctypes import wintypes


class ScreenGrabber(Thread):
    """Background screen grabber placeholder. Keeps last frame timestamp for perf."""

    def __init__(self, stop_event: Event, interval_ms: int = 100):
        super().__init__(daemon=True)
        self.stop_event = stop_event
        self.interval_ms = interval_ms
        self.last_capture_at = 0.0
        self.last_bmp = None  # bytes of BMP file content
        self.last_size = (0, 0)

    def run(self) -> None:
        while not self.stop_event.is_set():
            try:
                self.last_bmp, self.last_size = self._capture_screen_bmp()
                self.last_capture_at = time.time()
            except Exception:
                self.last_capture_at = time.time()
            self.stop_event.wait(self.interval_ms / 1000.0)

    # Win32 GDI screen capture → BMP bytes (no external deps)
    def _capture_screen_bmp(self):
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32

        hdc_screen = user32.GetDC(0)
        width = user32.GetSystemMetrics(0)
        height = user32.GetSystemMetrics(1)
        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        hbm = gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
        gdi32.SelectObject(hdc_mem, hbm)
        SRCCOPY = 0x00CC0020
        gdi32.BitBlt(hdc_mem, 0, 0, width, height, hdc_screen, 0, 0, SRCCOPY)

        class BITMAPFILEHEADER(ctypes.Structure):
            _fields_ = [
                ("bfType", wintypes.WORD),
                ("bfSize", wintypes.DWORD),
                ("bfReserved1", wintypes.WORD),
                ("bfReserved2", wintypes.WORD),
                ("bfOffBits", wintypes.DWORD),
            ]

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wintypes.DWORD),
                ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG),
                ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD),
            ]

        bmi = BITMAPINFOHEADER()
        bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.biWidth = width
        bmi.biHeight = -height  # top-down
        bmi.biPlanes = 1
        bmi.biBitCount = 24
        bmi.biCompression = 0  # BI_RGB
        bmi.biSizeImage = ((width * 3 + 3) & ~3) * height

        buf_len = bmi.biSizeImage
        buf = ctypes.create_string_buffer(buf_len)
        bits = ctypes.cast(buf, ctypes.c_void_p)
        gdi32.GetDIBits(hdc_mem, hbm, 0, height, bits, ctypes.byref(bmi), 0)

        # cleanup GDI objects
        gdi32.DeleteObject(hbm)
        gdi32.DeleteDC(hdc_mem)
        user32 = ctypes.windll.user32
        user32.ReleaseDC(0, hdc_screen)

        # build BMP file in memory
        bfh = BITMAPFILEHEADER()
        bfh.bfType = 0x4D42  # 'BM'
        bfh.bfOffBits = ctypes.sizeof(BITMAPFILEHEADER) + ctypes.sizeof(BITMAPINFOHEADER)
        bfh.bfSize = bfh.bfOffBits + buf_len
        bfh.bfReserved1 = 0
        bfh.bfReserved2 = 0

        bmp = bytearray()
        bmp += bytes(bfh)
        bmp += bytes(bmi)
        bmp += buf.raw
        return bytes(bmp), (width, height)


class OverlayWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('overlay')
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.0)  # fully transparent base
        self.root.overrideredirect(True)

        self.panel = tk.Toplevel(self.root)
        self.panel.overrideredirect(True)
        self.panel.attributes('-topmost', True)
        self.alpha_levels = [0.85, 0.6, 0.4]
        self.alpha_idx = 0
        self.panel.attributes('-alpha', self.alpha_levels[self.alpha_idx])

        screen_w = self.panel.winfo_screenwidth()
        screen_h = self.panel.winfo_screenheight()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.position_idx = 0  # 0:全屏, 1:上边条, 2:下边条, 3:右上角
        self._apply_position()

        self.canvas = tk.Canvas(self.panel, width=screen_w, height=screen_h, highlightthickness=0)
        self.canvas.pack()

        self.show_hint = True
        self.hint_text = '按 F8 显示/隐藏提示 · Esc 退出'

        self._draw()

        self.panel.bind('<F8>', lambda e: self.toggle_hint())
        self.panel.bind('<F9>', lambda e: self._demo())
        self.panel.bind('<Escape>', lambda e: self._exit())
        # 新增热键：F7切换位置，F6切换透明度
        self.panel.bind('<F7>', lambda e: self.toggle_position())
        self.panel.bind('<F6>', lambda e: self.toggle_alpha())
        self.panel.focus_force()

    def _draw(self):
        self.canvas.delete('all')
        if self.show_hint:
            # 根据位置选择面板推荐位置
            if self.position_idx == 3:  # 右上角小面板
                x, y, w, h = self.screen_w - 560, 40, 520, 140
            elif self.position_idx == 2:  # 下边条
                x, y, w, h = 40, self.screen_h - 200, 520, 140
            elif self.position_idx == 1:  # 上边条
                x, y, w, h = 40, 40, 520, 140
            else:  # 全屏覆盖时也放在左上
                x, y, w, h = 40, 40, 520, 140
            self.canvas.create_rectangle(x, y, x + w, y + h, fill='#000000', outline='#78c8ff', width=2, stipple='gray50')
            self.canvas.create_text(x + 12, y + 12, anchor='nw', fill='#e6f0ff', font=('Microsoft YaHei', 14), text=self.hint_text)
        self.panel.after(33, self._draw)

    def toggle_hint(self):
        self.show_hint = not self.show_hint

    def _demo(self):
        self.hint_text = '建议：买“左二”，若无关键则刷新。F8 隐藏/显示'

    def _exit(self):
        self.panel.destroy()
        self.root.destroy()

    def _apply_position(self):
        if self.position_idx == 0:
            # 全屏透明画布（默认）
            self.panel.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        elif self.position_idx == 1:
            # 顶部条
            self.panel.geometry(f"{self.screen_w}x220+0+0")
        elif self.position_idx == 2:
            # 底部条
            self.panel.geometry(f"{self.screen_w}x220+0+{self.screen_h-220}")
        else:
            # 右上角
            self.panel.geometry(f"600x220+{self.screen_w-620}+0")

    def toggle_position(self):
        self.position_idx = (self.position_idx + 1) % 4
        self._apply_position()
        self.hint_text = f'已切换位置（F7 继续切换）'

    def toggle_alpha(self):
        self.alpha_idx = (self.alpha_idx + 1) % len(self.alpha_levels)
        self.panel.attributes('-alpha', self.alpha_levels[self.alpha_idx])
        self.hint_text = f'已调整透明度（F6 继续调整）'


class CoachApp:
    def __init__(self):
        self.stop_event = Event()
        self.overlay = OverlayWindow()
        self.grabber = ScreenGrabber(self.stop_event)
        self.grabber.start()
        self.overlay.panel.bind('<F10>', lambda e: self.save_last_frame())

    def exec(self):
        self.overlay.root.mainloop()

    def save_last_frame(self):
        if not self.grabber.last_bmp:
            self.overlay.hint_text = '暂未捕获到帧，稍后再试 (F10 保存)'
            return
        out_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(out_dir, exist_ok=True)
        ts = int(time.time())
        path = os.path.join(out_dir, f'screenshot_{ts}.bmp')
        with open(path, 'wb') as f:
            f.write(self.grabber.last_bmp)
        w, h = self.grabber.last_size
        # 复制路径到剪贴板，方便你发图或查看
        try:
            self.overlay.root.clipboard_clear()
            self.overlay.root.clipboard_append(path)
        except Exception:
            pass
        self.overlay.hint_text = f'已保存截图 {w}x{h}，路径已复制(F10 再次保存)'


def main():
    app = CoachApp()
    app.exec()


if __name__ == '__main__':
    main()


