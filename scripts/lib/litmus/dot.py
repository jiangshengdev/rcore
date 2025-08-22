#!/usr/bin/env python3
"""
DOT 文件处理模块
处理 DOT 格式文件的解析和主题颜色应用
"""

import pathlib
import re
from typing import List

from .herd_config import get_theme_specific_dot_modifications


def parse_dot_graphs(dot_file: pathlib.Path) -> List[List[str]]:
    """解析 DOT 文件，提取所有图"""
    digraph_re = re.compile(r"^\s*digraph\b")

    text = dot_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    graphs = []
    current_graph = []
    depth = 0
    collecting = False

    for line in text:
        if digraph_re.match(line):
            if collecting and current_graph:
                current_graph = []
                depth = 0
            collecting = True
            current_graph = [line]
            depth = line.count('{') - line.count('}')
            continue

        if collecting:
            current_graph.append(line)
            depth += line.count('{') - line.count('}')
            if depth == 0:
                graphs.append(current_graph)
                current_graph = []
                collecting = False

    return graphs


def apply_theme_colors_to_dot(dot_content: str, theme: str) -> str:
    """将主题颜色应用到 DOT 内容中，替换硬编码的颜色"""
    theme_mods = get_theme_specific_dot_modifications(theme)

    # 定义颜色映射：硬编码颜色 -> 主题颜色
    color_mappings = {
        # herd7 默认使用的颜色映射到主题颜色
        "indigo": theme_mods['ppo_color'],  # program order (ppo)
        "blue": theme_mods['co_color'],  # coherence (co)
        "red": theme_mods['rf_color'],  # read-from (rf)
        "#ffa040": theme_mods['fr_color'],  # from-read (fr)
        "purple": theme_mods['fence_color'],  # fence
        "green": theme_mods['addr_color'],  # address dependency
        "orange": theme_mods['ctrl_color'],  # control dependency
        "black": theme_mods['edge_color'],  # 默认边颜色
    }

    modified_content = dot_content

    # 替换所有出现的颜色，包括组合颜色中的单个颜色
    for old_color, new_color in color_mappings.items():
        # 替换边颜色（color="..."）
        modified_content = re.sub(
            rf'color="{re.escape(old_color)}"',
            f'color="{new_color}"',
            modified_content
        )

        # 替换组合颜色中的单个颜色（如 color="blue:#ffa040:red" 中的各个颜色）
        modified_content = re.sub(
            rf'(?<=[\s":])({re.escape(old_color)})(?=[\s":])',
            new_color,
            modified_content
        )

        # 替换字体颜色（<font color="...">）
        modified_content = re.sub(
            rf'<font color="{re.escape(old_color)}">',
            f'<font color="{new_color}">',
            modified_content
        )

    return modified_content
