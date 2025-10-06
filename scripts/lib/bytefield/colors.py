"""
主题颜色配置模块。

此模块定义了 bytefield SVG 图表的主题颜色配置，
支持浅色（light）和深色（dark）两种主题。
"""

# 支持的主题选项
THEME_CHOICES = ['light', 'dark']

# Bytefield 主题颜色配置
BYTEFIELD_THEMES = {
    'light': {
        'stroke': '#1C1E21',  # 浅色主题的描边颜色（深色线条）
        'background': 'transparent'  # 透明背景
    },
    'dark': {
        'stroke': '#E3E3E3',  # 深色主题的描边颜色（浅色线条）
        'background': 'transparent'  # 透明背景
    }
}


def get_theme_config(theme: str) -> dict:
    """
    获取指定主题的配置。
    
    参数:
        theme: 主题名称，必须是 'light' 或 'dark'
        
    返回:
        包含主题配置的字典，包含 'stroke' 和 'background' 键
        
    异常:
        KeyError: 如果主题名称不存在
    """
    return BYTEFIELD_THEMES[theme]
