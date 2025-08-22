#!/usr/bin/env python3
"""
Litmus 模块通用工具函数
提供模块间共享的工具函数
"""

import sys


def eprint(*args, **kwargs):
    """输出到标准错误流"""
    print(*args, file=sys.stderr, **kwargs)
