# 半自动教练原型(Overlay Coach)

功能
- 叠加层显示提示，不进行自动点击。
- F8 显示/隐藏提示；F9 显示演示性建议文本；Esc 退出。

运行
```bash
# 建议使用 Python 3.10+
# 创建虚拟环境(可选)
# python -m venv .venv && .venv\\Scripts\\activate
pip install -r requirements.txt
python overlay_coach.py
```

目录
- `overlay_coach.py` 主程序（PyQt 置顶透明窗口 + 截屏线程占位）
- 后续会加入识别与策略模块：`recognition/`, `strategy/`

注意
- 默认不发送鼠标键盘事件，风险较低。
- 若 F8/F9 无效，请以管理员身份运行终端。


