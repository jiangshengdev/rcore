"""
公共颜色常量模块
定义了项目通用的系统颜色常量，用于各类可视化图表
与网站整体设计保持一致
"""

# 系统 UI 颜色：红色
SYSTEM_RED_LIGHT = '#FF3B30'
SYSTEM_RED_DARK = '#FF453A'

# 系统 UI 颜色：橙色
SYSTEM_ORANGE_LIGHT = '#FF9500'
SYSTEM_ORANGE_DARK = '#FF9F0A'

# 系统 UI 颜色：绿色
SYSTEM_GREEN_LIGHT = "#34C759"
SYSTEM_GREEN_DARK = "#30D158"

# 系统 UI 颜色：蓝色
SYSTEM_BLUE_LIGHT = '#007AFF'
SYSTEM_BLUE_DARK = '#0A84FF'

# 系统 UI 颜色：黄色
SYSTEM_YELLOW_LIGHT = '#FFCC00'
SYSTEM_YELLOW_DARK = '#FFD60A'

# 系统 UI 颜色：青色
SYSTEM_CYAN_LIGHT = '#32ADE6'
SYSTEM_CYAN_DARK = '#64D2FF'

# 系统 UI 颜色：青蓝色
SYSTEM_TEAL_LIGHT = '#30B0C7'
SYSTEM_TEAL_DARK = '#40CBE0'

# 系统 UI 颜色：薄荷色
SYSTEM_MINT_LIGHT = '#00C7BE'
SYSTEM_MINT_DARK = '#63E6E2'

# 系统 UI 颜色：靛青色
SYSTEM_INDIGO_LIGHT = '#5856D6'
SYSTEM_INDIGO_DARK = '#5E5CE6'

# 系统 UI 颜色：紫色
SYSTEM_PURPLE_LIGHT = '#AF52DE'
SYSTEM_PURPLE_DARK = '#BF5AF2'

# 系统 UI 颜色：粉色
SYSTEM_PINK_LIGHT = "#FF2D55"
SYSTEM_PINK_DARK = "#FF375F"

# 系统 UI 颜色：棕色
SYSTEM_BROWN_LIGHT = '#A2845E'
SYSTEM_BROWN_DARK = '#AC8E68'

# 系统 UI 颜色：黑色
SYSTEM_BLACK = '#000000'

# 系统 UI 颜色：白色
SYSTEM_WHITE = '#FFFFFF'

# 系统 UI 颜色：灰色
SYSTEM_GRAY = '#8E8E93'

# 系统 UI 颜色：灰色2
SYSTEM_GRAY2_LIGHT = '#AEAEB2'
SYSTEM_GRAY2_DARK = '#636366'

# 系统 UI 颜色：灰色3
SYSTEM_GRAY3_LIGHT = '#C7C7CC'
SYSTEM_GRAY3_DARK = '#48484A'

# 系统 UI 颜色：灰色4
SYSTEM_GRAY4_LIGHT = '#D1D1D6'
SYSTEM_GRAY4_DARK = '#3A3A3C'

# 系统 UI 颜色：灰色5
SYSTEM_GRAY5_LIGHT = '#E5E5EA'
SYSTEM_GRAY5_DARK = '#2C2C2E'

# 系统 UI 颜色：灰色6
SYSTEM_GRAY6_LIGHT = '#F2F2F7'
SYSTEM_GRAY6_DARK = '#1C1C1E'


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
