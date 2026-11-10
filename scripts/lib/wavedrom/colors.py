#!/usr/bin/env python3
"""
WaveDrom 主题颜色配置
单色 SVG 文件，只需要两个颜色，背景透明
"""

# 主题选择常量
THEME_CHOICES = ['light', 'dark']

# WaveDrom 单色主题配置
WAVEDROM_THEMES = {
    'light': {
        'stroke': '#1C1E21',  # 深色线条用于浅色主题
        'background': 'transparent'
    },
    'dark': {
        'stroke': '#E3E3E3',  # 浅色线条用于深色主题  
        'background': 'transparent'
    }
}


def get_theme_config(theme: str) -> dict:
    """获取指定主题的配置"""
    if theme not in THEME_CHOICES:
        raise ValueError(f"无效的主题: {theme}，可选: {THEME_CHOICES}")

    return WAVEDROM_THEMES[theme]
