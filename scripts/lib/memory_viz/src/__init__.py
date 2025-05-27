"""
内存可视化系统

这个包提供了内存布局和伙伴系统的可视化功能。
"""

__version__ = "1.0.0"

# 导出主要的类和函数，保持向后兼容
from .core.generator import MemoryDotGenerator
from .core.parser import parse_gdb_output, parse_gdb_groups
from .core.colors import get_theme_colors, hex_with_alpha

__all__ = [
    'MemoryDotGenerator',
    'parse_gdb_output', 
    'parse_gdb_groups',
    'get_theme_colors',
    'hex_with_alpha'
]
