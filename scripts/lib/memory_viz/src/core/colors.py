"""
内存可视化颜色配置模块
定义了亮色和暗色主题的统一颜色方案，用于内存可视化图表
与网站整体设计保持一致
"""

from typing import Dict, Any

# 导入公共系统颜色常量
from ....common.colors import (
    SYSTEM_RED_LIGHT, SYSTEM_RED_DARK,
    SYSTEM_ORANGE_LIGHT, SYSTEM_ORANGE_DARK,
    SYSTEM_GREEN_LIGHT, SYSTEM_GREEN_DARK,
    SYSTEM_BLUE_LIGHT, SYSTEM_BLUE_DARK,
    SYSTEM_YELLOW_LIGHT, SYSTEM_YELLOW_DARK,
    SYSTEM_CYAN_LIGHT, SYSTEM_CYAN_DARK,
    SYSTEM_TEAL_LIGHT, SYSTEM_TEAL_DARK,
    SYSTEM_MINT_LIGHT, SYSTEM_MINT_DARK,
    SYSTEM_INDIGO_LIGHT, SYSTEM_INDIGO_DARK,
    SYSTEM_PURPLE_LIGHT, SYSTEM_PURPLE_DARK,
    SYSTEM_PINK_LIGHT, SYSTEM_PINK_DARK,
    SYSTEM_BROWN_LIGHT, SYSTEM_BROWN_DARK,
    SYSTEM_BLACK, SYSTEM_WHITE, SYSTEM_GRAY,
    SYSTEM_GRAY2_LIGHT, SYSTEM_GRAY2_DARK,
    SYSTEM_GRAY3_LIGHT, SYSTEM_GRAY3_DARK,
    SYSTEM_GRAY4_LIGHT, SYSTEM_GRAY4_DARK,
    SYSTEM_GRAY5_LIGHT, SYSTEM_GRAY5_DARK,
    SYSTEM_GRAY6_LIGHT, SYSTEM_GRAY6_DARK,
    hex_with_alpha
)

# 主题颜色配置
THEME_COLORS: Dict[str, Dict[str, Any]] = {
    "light": {
        # 文字和边框颜色
        "text_color": "#1c1e21",
        "border_color": "#1c1e21",
        # 背景颜色 (带透明度)
        "addr_bg": hex_with_alpha(SYSTEM_PINK_LIGHT, 0.18),
        "val_bg": hex_with_alpha(SYSTEM_GREEN_LIGHT, 0.18),
        "index_bg": hex_with_alpha(SYSTEM_BLUE_LIGHT, 0.18),
        # 集群颜色
        "cluster_color": SYSTEM_GRAY3_LIGHT,
        # 系统颜色（按常量定义顺序排列）
        "system_red": SYSTEM_RED_LIGHT,
        "system_orange": SYSTEM_ORANGE_LIGHT,
        "system_green": SYSTEM_GREEN_LIGHT,
        "system_blue": SYSTEM_BLUE_LIGHT,
        "system_yellow": SYSTEM_YELLOW_LIGHT,
        "system_cyan": SYSTEM_CYAN_LIGHT,
        "system_teal": SYSTEM_TEAL_LIGHT,
        "system_mint": SYSTEM_MINT_LIGHT,
        "system_indigo": SYSTEM_INDIGO_LIGHT,
        "system_purple": SYSTEM_PURPLE_LIGHT,
        "system_pink": SYSTEM_PINK_LIGHT,
        "system_brown": SYSTEM_BROWN_LIGHT,
        "system_black": SYSTEM_BLACK,
        "system_white": SYSTEM_WHITE,
        "system_gray": SYSTEM_GRAY,
        "system_gray2": SYSTEM_GRAY2_LIGHT,
        "system_gray3": SYSTEM_GRAY3_LIGHT,
        "system_gray4": SYSTEM_GRAY4_LIGHT,
        "system_gray5": SYSTEM_GRAY5_LIGHT,
        "system_gray6": SYSTEM_GRAY6_LIGHT,
        # 二叉树专用颜色
        "tree_line": SYSTEM_GRAY,
    },
    "dark": {
        # 文字和边框颜色
        "text_color": "#e3e3e3",
        "border_color": "#e3e3e3",
        # 背景颜色 (带透明度)
        "addr_bg": hex_with_alpha(SYSTEM_PINK_DARK, 0.18),
        "val_bg": hex_with_alpha(SYSTEM_GREEN_DARK, 0.18),
        "index_bg": hex_with_alpha(SYSTEM_BLUE_DARK, 0.18),
        # 集群颜色
        "cluster_color": SYSTEM_GRAY3_DARK,
        # 系统颜色（按常量定义顺序排列）
        "system_red": SYSTEM_RED_DARK,
        "system_orange": SYSTEM_ORANGE_DARK,
        "system_green": SYSTEM_GREEN_DARK,
        "system_blue": SYSTEM_BLUE_DARK,
        "system_yellow": SYSTEM_YELLOW_DARK,
        "system_cyan": SYSTEM_CYAN_DARK,
        "system_teal": SYSTEM_TEAL_DARK,
        "system_mint": SYSTEM_MINT_DARK,
        "system_indigo": SYSTEM_INDIGO_DARK,
        "system_purple": SYSTEM_PURPLE_DARK,
        "system_pink": SYSTEM_PINK_DARK,
        "system_brown": SYSTEM_BROWN_DARK,
        "system_black": SYSTEM_BLACK,
        "system_white": SYSTEM_WHITE,
        "system_gray": SYSTEM_GRAY,
        "system_gray2": SYSTEM_GRAY2_DARK,
        "system_gray3": SYSTEM_GRAY3_DARK,
        "system_gray4": SYSTEM_GRAY4_DARK,
        "system_gray5": SYSTEM_GRAY5_DARK,
        "system_gray6": SYSTEM_GRAY6_DARK,
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
