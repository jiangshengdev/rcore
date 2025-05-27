"""
颜色配置模块
定义了亮色和暗色主题的统一颜色方案，用于内存可视化图表
与网站整体设计保持一致
"""

from typing import Dict, Any

# 系统 UI 颜色：粉色
SYSTEM_PINK_LIGHT = "#FF2D55"
SYSTEM_PINK_DARK = "#FF375F"

# 系统 UI 颜色：绿色
SYSTEM_GREEN_LIGHT = "#34C759"
SYSTEM_GREEN_DARK = "#30D158"

# 系统 UI 颜色：蓝色
SYSTEM_BLUE_LIGHT = '#007AFF'
SYSTEM_BLUE_DARK = '#0A84FF'

# 系统 UI 颜色：橙色
SYSTEM_ORANGE_LIGHT = '#FF9500'
SYSTEM_ORANGE_DARK = '#FF9F0A'

# 系统 UI 颜色：灰色
SYSTEM_GRAY = '#8E8E93'

# 系统 UI 颜色：灰色2
SYSTEM_GRAY2_LIGHT = '#AEAEB2'
SYSTEM_GRAY2_DARK = '#636366'

# 系统 UI 颜色：灰色3
SYSTEM_GRAY3_LIGHT = '#C7C7CC'
SYSTEM_GRAY3_DARK = '#48484A'


def hex_with_alpha(hex_color: str, alpha: float) -> str:
    """
    将 #RRGGBB 颜色与 alpha 混合，返回 #RRGGBBAA
    
    Args:
        hex_color: 十六进制颜色值，格式为 #RRGGBB
        alpha: 透明度，范围 0.0-1.0
    
    Returns:
        带 alpha 通道的十六进制颜色值，格式为 #RRGGBBAA
    """
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    a = int(alpha * 255)
    return f"#{r:02X}{g:02X}{b:02X}{a:02X}"


# 主题颜色配置
THEME_COLORS: Dict[str, Dict[str, Any]] = {
    "light": {
        # 文字和边框颜色
        "text_color": "#1c1e21",
        "border_color": "#1c1e21",
        # 背景颜色 (带透明度)
        "addr_bg": hex_with_alpha(SYSTEM_PINK_LIGHT, 0.125),
        "val_bg": hex_with_alpha(SYSTEM_GREEN_LIGHT, 0.125),
        # 集群颜色
        "cluster_color": SYSTEM_GRAY3_LIGHT,
        # 系统颜色
        "system_pink": SYSTEM_PINK_LIGHT,
        "system_green": SYSTEM_GREEN_LIGHT,
        "system_blue": SYSTEM_BLUE_LIGHT,
        "system_orange": SYSTEM_ORANGE_LIGHT,
        # 二叉树专用颜色
        "tree_line": SYSTEM_GRAY,
    },
    "dark": {
        # 文字和边框颜色
        "text_color": "#e3e3e3",
        "border_color": "#e3e3e3",
        # 背景颜色 (带透明度)
        "addr_bg": hex_with_alpha(SYSTEM_PINK_DARK, 0.125),
        "val_bg": hex_with_alpha(SYSTEM_GREEN_DARK, 0.125),
        # 集群颜色
        "cluster_color": SYSTEM_GRAY3_DARK,
        # 系统颜色
        "system_pink": SYSTEM_PINK_DARK,
        "system_green": SYSTEM_GREEN_DARK,
        "system_blue": SYSTEM_BLUE_DARK,
        "system_orange": SYSTEM_ORANGE_DARK,
        # 二叉树专用颜色
        "tree_line": SYSTEM_GRAY,
    }
}


def get_theme_colors(theme: str = "light") -> Dict[str, Any]:
    """
    获取指定主题的颜色配置
    
    Args:
        theme: 主题名称，"light" 或 "dark"
    
    Returns:
        包含颜色配置的字典
    
    Raises:
        ValueError: 当主题名称无效时
    """
    if theme not in THEME_COLORS:
        raise ValueError(f"不支持的主题: {theme}。支持的主题: {list(THEME_COLORS.keys())}")

    return THEME_COLORS[theme].copy()
