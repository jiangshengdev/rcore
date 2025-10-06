"""
Bytefield 转换器的工具函数。
"""

import sys


def eprint(*args, **kwargs):
    """
    打印到标准错误输出。
    
    此函数用于错误消息和警告，将它们与正常输出分离，
    以便正确重定向和记录日志。
    
    参数:
        *args: 要打印的位置参数
        **kwargs: 传递给 print() 的关键字参数
    """
    print(*args, file=sys.stderr, **kwargs)
