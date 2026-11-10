"""
herd7 参数配置生成器
根据主题动态生成 herd7 命令的颜色和样式参数
"""

import pathlib
from typing import List

from .colors import get_litmus_theme_colors


def build_herd_args(litmus_file: pathlib.Path, theme: str = "light", temp_dir: pathlib.Path = None) -> List[str]:
    """
    构建 herd7 命令参数，根据主题应用相应的颜色配置
    
    Args:
        litmus_file: litmus 测试文件路径
        theme: 主题名称 ("light" 或 "dark") 
        temp_dir: 临时输出目录
        
    Returns:
        herd7 命令参数列表
    """
    colors = get_litmus_theme_colors(theme)

    # 基础参数（参考 simple_extract.py 的工作参数）
    base_args = [
        "herd7",
        "-through", "none",
        "-show", "prop",
        "-doshow", "addr,data,ctrl,fence,ppo,rf,fr",
        "-showevents", "mem",
        "-showinitwrites", "false",
        "-showthread", "true",
        "-squished", "true",
        "-graph", "columns",
        "-fixedsize", "false",
        "-fontname", "SF Pro Display",
        "-fontsize", "14",
        "-edgefontsizedelta", "0",
        "-penwidth", "2",
        "-arrowsize", "1",
        "-splines", "spline",
        "-pad", "0.0",
        "-showlegend", "true",
        "-showkind", "true",
        "-yscale", "1.5",
        "-xscale", "5",
        "-extrachars", "0",
        "-edgemerge", "true",
    ]

    # 输出目录参数
    output_args = []
    if temp_dir:
        output_args.extend(["-o", str(temp_dir)])

    # 输入文件参数
    input_args = [str(litmus_file)]

    # 注意：移除了颜色参数，因为 herd7 可能不支持这些参数
    # 颜色将在后续的 neato 阶段应用
    return base_args + output_args + input_args


def get_theme_specific_dot_modifications(theme: str = "light") -> dict:
    """
    获取主题相关的 DOT 图形修改参数
    用于在 DOT 文件生成后进行颜色调整
    
    Args:
        theme: 主题名称
        
    Returns:
        包含 DOT 修改参数的字典
    """
    colors = get_litmus_theme_colors(theme)

    return {
        "bgcolor": colors["background"],
        "fontcolor": colors["node_text"],
        "node_fillcolor": colors["node_fill"],
        "node_color": colors["node_border"],
        "edge_color": colors["edge_normal"],
        # 特定边类型的颜色
        "rf_color": colors["edge_rf"],  # read-from
        "co_color": colors["edge_co"],  # coherence
        "fr_color": colors["edge_fr"],  # from-read
        "ppo_color": colors["edge_ppo"],  # PPO (Preserved Program Order), data, control, address 依赖统一使用
        "fence_color": colors["edge_fence"],  # fence
        "green_color": colors["edge_green"],  # 绿色（对应 darkgreen）
    }
