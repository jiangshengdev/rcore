#!/usr/bin/env python3
"""
RISC-V Litmus DOT 文件处理器
复用现有 litmus 模块逻辑，处理已有的 DOT 文件并生成主题化 SVG
"""

import pathlib
import re
from typing import List, Tuple

from scripts.lib.common.utils import ensure_dir
from scripts.lib.litmus.dot import apply_theme_colors_to_dot, parse_dot_graphs
from scripts.lib.litmus.svg import run_neato
from scripts.lib.litmus.utils import eprint


def scale_dot_content(dot_content: str, scale_factor: float = 2.0) -> str:
    """
    缩放DOT内容中的位置和尺寸参数，但保持线条和字体大小不变
    
    Args:
        dot_content: 原始DOT内容
        scale_factor: 缩放因子，默认2.0（2倍）
    
    Returns:
        缩放后的DOT内容
    """
    modified_content = dot_content

    # 缩放节点位置坐标 pos="x,y!"
    def scale_pos(match):
        x, y = match.groups()
        new_x = float(x) * scale_factor
        new_y = float(y) * scale_factor
        return f'pos="{new_x:.6f},{new_y:.6f}!"'

    modified_content = re.sub(
        r'pos="([0-9.]+),([0-9.]+)!"',
        scale_pos,
        modified_content
    )

    # 缩放节点尺寸 width="x" height="y"，但不缩放其他属性
    def scale_width(match):
        value = float(match.group(1))
        new_value = value * scale_factor
        return f'width="{new_value:.6f}"'

    def scale_height(match):
        value = float(match.group(1))
        new_value = value * scale_factor
        return f'height="{new_value:.6f}"'

    modified_content = re.sub(
        r'\bwidth="([0-9.]+)"',
        scale_width,
        modified_content
    )

    modified_content = re.sub(
        r'\bheight="([0-9.]+)"',
        scale_height,
        modified_content
    )

    # 调整字体大小以匹配原始litmus设置
    # 原始litmus使用fontsize=14，而我们的DOT文件使用fontsize=8和fontsize=11
    # 将fontsize=8调整为fontsize=14 (节点字体)
    modified_content = re.sub(
        r'fontsize=8\b',
        'fontsize=14',
        modified_content
    )

    # 将fontsize=11调整为fontsize=14 (边标签字体)
    modified_content = re.sub(
        r'fontsize=11\b',
        'fontsize=14',
        modified_content
    )

    # 调整线条宽度以匹配原始litmus设置
    # 原始litmus使用penwidth="2.000000"，而我们的DOT文件使用penwidth="3.000000"
    modified_content = re.sub(
        r'penwidth="3\.000000"',
        'penwidth="2.000000"',
        modified_content
    )

    # 调整箭头大小以匹配原始litmus设置  
    # 原始litmus使用arrowsize="1.000000"，而我们的DOT文件使用arrowsize="0.666700"
    modified_content = re.sub(
        r'arrowsize="0\.666700"',
        'arrowsize="1.000000"',
        modified_content
    )

    # 特殊处理LaTeX样式变量（如 $v$）：去除$符号
    def replace_latex_var(match):
        full_label = match.group(1)  # 整个label内容
        # 在label内容中查找并替换所有$变量$，只去除$符号
        processed_label = re.sub(r'\$([^$]+)\$', r'\1', full_label)
        return f'label="{processed_label}"'

    # 匹配并处理包含LaTeX变量的label
    modified_content = re.sub(
        r'label="([^"]*\$[^"]*)"',
        replace_latex_var,
        modified_content
    )

    # 保持字体大小不变 - 移除字体缩放
    # 保持线条宽度不变 - 移除线条缩放
    # 保持箭头大小不变 - 移除箭头缩放

    return modified_content


def find_dot_files(source_dir: pathlib.Path, themes: List[str]) -> List[
    Tuple[pathlib.Path, List[Tuple[str, pathlib.Path]]]]:
    """查找已存在的DOT文件（.txt后缀）及其输出目录"""

    # 目标输出目录：docs/example/_assets/images/
    target_base = pathlib.Path("docs/example/_assets/images")

    dot_files = []

    # 查找所有.txt文件（实际是DOT格式）
    for txt_file in source_dir.glob("*.txt"):
        # 为每个主题创建输出目录
        theme_dirs = []
        for theme in themes:
            theme_output_dir = target_base / theme
            theme_dirs.append((theme, theme_output_dir))

        dot_files.append((txt_file, theme_dirs))

    return dot_files


def process_dot_file(dot_file: pathlib.Path, theme_dirs: List[Tuple[str, pathlib.Path]],
                     scale_factor: float = 2.0) -> int:
    """处理单个DOT文件，生成不同主题的SVG
    
    Args:
        dot_file: DOT文件路径
        theme_dirs: 主题输出目录列表
        scale_factor: 缩放因子，默认2.0（2倍大小）
    """

    total_exported = 0

    for theme, output_dir in theme_dirs:
        # 为当前文件和主题创建子目录
        test_output_dir = output_dir / dot_file.stem
        ensure_dir(str(test_output_dir))

        # 读取原始DOT内容
        try:
            dot_content = dot_file.read_text(encoding="utf-8")
        except Exception as e:
            eprint(f"[WARN] 无法读取文件 {dot_file.name}: {e}")
            continue

        # 解析DOT图形（通常只有一个图形）
        graphs = parse_dot_graphs(dot_file)
        if not graphs:
            eprint(f"[WARN] 未找到图形数据: {dot_file.name}")
            continue

        exported = 0
        for i, graph_lines in enumerate(graphs, 1):
            if not graph_lines:
                continue

            # 重构图形内容
            graph_content = "\n".join(graph_lines)

            # 确保图形格式正确
            if not graph_content.rstrip().endswith('}'):
                continue

            # 应用缩放处理（使SVG变为指定倍数大小）
            scaled_graph_content = graph_content
            if scale_factor != 1.0:
                scaled_graph_content = scale_dot_content(graph_content, scale_factor)

            # 应用主题颜色（复用现有逻辑）
            themed_graph_content = apply_theme_colors_to_dot(scaled_graph_content, theme)

            # 保存主题化的DOT文件
            themed_dot_path = test_output_dir / f"graph_{i:02d}.dot"
            themed_dot_path.write_text(themed_graph_content + "\n", encoding="utf-8")

            # 生成SVG（复用现有逻辑，使用缩放后的内容）
            svg_path = test_output_dir / f"graph_{i:02d}.svg"
            if run_neato(scaled_graph_content, svg_path, theme):
                exported += 1

        if exported > 0:
            scale_info = f" (缩放 {scale_factor}x)" if scale_factor != 1.0 else ""
            eprint(f"[INFO] {dot_file.name} ({theme}): 生成 {exported} 个 SVG{scale_info} -> {test_output_dir}")
            total_exported += exported

    return total_exported
