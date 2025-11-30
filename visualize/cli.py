#!/usr/bin/env python3
"""
性能测试结果可视化分析工具 - 命令行入口
Author: AI Assistant
Date: 2024
"""

import sys
from pathlib import Path

# 添加父目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from visualize.main import main

if __name__ == '__main__':
    main()
