"""
Litmus 测试图形颜色配置模块
定义了亮色和暗色主题的统一颜色方案，用于 herd7 生成的内存一致性模型图表
与网站整体设计保持一致
"""

from typing import Dict, Any

# 导入公共系统颜色常量
from ..common.colors import (
    SYSTEM_RED_LIGHT, SYSTEM_RED_DARK,
    SYSTEM_ORANGE_LIGHT, SYSTEM_ORANGE_DARK,
    SYSTEM_BLUE_LIGHT, SYSTEM_BLUE_DARK,
    SYSTEM_PURPLE_LIGHT, SYSTEM_PURPLE_DARK,
    SYSTEM_BROWN_LIGHT, SYSTEM_BROWN_DARK,
    SYSTEM_GRAY, SYSTEM_GRAY5_LIGHT, SYSTEM_GRAY5_DARK
)

# Litmus 专用颜色常量定义
LITMUS_TEXT_COLOR_LIGHT = "#1c1e21"
LITMUS_TEXT_COLOR_DARK = "#e3e3e3"
LITMUS_BACKGROUND_LIGHT = "transparent"
LITMUS_BACKGROUND_DARK = "transparent"

# 网页背景颜色
WEB_BACKGROUND_DARK = "#1b1b1d"

# Litmus 图形专用颜色映射
LITMUS_THEME_COLORS: Dict[str, Dict[str, Any]] = {
    "light": {
        # 节点颜色
        "node_fill": SYSTEM_GRAY5_LIGHT,
        "node_border": LITMUS_TEXT_COLOR_LIGHT,
        "node_text": LITMUS_TEXT_COLOR_LIGHT,

        # 边颜色（优化以保留原始色相）
        "edge_normal": SYSTEM_GRAY,  # 使用灰色代替纯黑色
        "edge_rf": SYSTEM_RED_LIGHT,  # 使用红色对应原始 red
        "edge_co": SYSTEM_BLUE_LIGHT,  # 使用蓝色对应原始 blue
        "edge_fr": SYSTEM_ORANGE_LIGHT,  # 使用橙色对应原始 #ffa040
        "edge_ppo": SYSTEM_PURPLE_LIGHT,  # 使用紫色对应原始 indigo (PPO, data, control, address 依赖)
        "edge_fence": SYSTEM_BROWN_LIGHT,  # fence 指令，使用棕色

        # 背景颜色
        "background": LITMUS_BACKGROUND_LIGHT,
        "cluster_bg": "transparent",
    },
    "dark": {
        # 节点颜色
        "node_fill": SYSTEM_GRAY5_DARK,
        "node_border": LITMUS_TEXT_COLOR_DARK,
        "node_text": LITMUS_TEXT_COLOR_DARK,

        # 边颜色（优化以保留原始色相）
        "edge_normal": SYSTEM_GRAY,  # 暗色主题中使用灰色，保持与亮色主题一致
        "edge_rf": SYSTEM_RED_DARK,  # 使用红色对应原始 red
        "edge_co": SYSTEM_BLUE_DARK,  # 使用蓝色对应原始 blue
        "edge_fr": SYSTEM_ORANGE_DARK,  # 使用橙色对应原始 #ffa040
        "edge_ppo": SYSTEM_PURPLE_DARK,  # 使用紫色对应原始 indigo (PPO, data, control, address 依赖)
        "edge_fence": SYSTEM_BROWN_DARK,  # fence 指令，使用棕色

        # 背景颜色
        "background": LITMUS_BACKGROUND_DARK,
        "cluster_bg": "transparent",
    }
}

# 支持的主题列表
THEME_CHOICES = ["light", "dark"]


def get_litmus_theme_colors(theme: str = "light") -> Dict[str, Any]:
    """
    获取指定主题的 litmus 颜色配置
    
    Args:
        theme: 主题名称，"light" 或 "dark"
    
    Returns:
        包含颜色配置的字典
    
    Raises:
        ValueError: 当主题名称无效时
    """
    if theme not in LITMUS_THEME_COLORS:
        raise ValueError(f"不支持的主题: {theme}。支持的主题: {list(LITMUS_THEME_COLORS.keys())}")

    return LITMUS_THEME_COLORS[theme].copy()
