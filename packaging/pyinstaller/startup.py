#!/usr/bin/env python3
"""ChatFilter启动器 - 包装器脚本"""

import sys
import os

# 获取脚本所在目录
if getattr(sys, 'frozen', False):
    # 打包后的环境 - executable所在目录
    base_path = os.path.dirname(sys.executable)
else:
    # 开发环境: startup.py 位于 packaging/pyinstaller/
    base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# 将项目根目录加入路径，保证 core 包可导入
sys.path.insert(0, base_path)

# 现在可以安全地导入core模块了
# 相对导入在包内仍然有效
from core.chat_filter import main

if __name__ == '__main__':
    main()
