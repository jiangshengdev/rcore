#!/usr/bin/env python3
"""
SVG 生成和处理模块
处理 SVG 文件的生成、后处理和样式优化
"""

import copy
import pathlib
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

from scripts.lib.common.utils import ensure_dir
from scripts.lib.common.colors import SYSTEM_WHITE
from .colors import WEB_BACKGROUND_DARK
from .dot import apply_theme_colors_to_dot
from .herd_config import get_theme_specific_dot_modifications


def eprint(*args, **kwargs):
    """输出到标准错误流"""
    print(*args, file=sys.stderr, **kwargs)


def create_text_stroke_effect(text_group, svg_container, theme="light"):
    """
    为文本组创建外描边效果
    
    通过复制文本组并在原始文本之前插入描边版本来实现外描边
    """
    try:
        # 根据主题确定描边颜色
        stroke_width = "2"  # 外描边需要稍粗一些
        stroke_opacity = "1"

        if theme == "dark":
            stroke_color = WEB_BACKGROUND_DARK
        else:
            stroke_color = SYSTEM_WHITE

        # 创建描边版本
        stroke_group = copy.deepcopy(text_group)

        # 设置描边版本的样式：只有描边，没有填充
        stroke_group.set('fill', 'none')
        stroke_group.set('stroke', stroke_color)
        stroke_group.set('stroke-width', stroke_width)
        stroke_group.set('stroke-opacity', stroke_opacity)
        stroke_group.set('stroke-linejoin', 'round')
        stroke_group.set('stroke-linecap', 'round')

        # 处理所有子元素
        for child in stroke_group.iter():
            if child != stroke_group:  # 不处理根元素本身
                child.set('stroke', stroke_color)
                child.set('stroke-width', stroke_width)
                child.set('stroke-opacity', stroke_opacity)
                if child.tag == 'use' or child.tag.endswith('}use'):
                    child.set('fill', 'none')

        # 先添加描边版本到容器
        svg_container.append(stroke_group)

        # 确保原始文本组没有描边
        text_group.set('stroke', 'none')
        for child in text_group.iter():
            if child != text_group:
                child.set('stroke', 'none')

    except Exception as e:
        eprint(f"[WARN] 创建外描边效果失败: {e}")


def reorder_svg_elements_for_label_priority(svg_content: str, theme: str = "light") -> str:
    """
    重新排序 SVG 元素，确保箭头标签始终在最上层显示
    
    在 SVG 中，后面的元素会覆盖前面的元素。为了确保箭头标签不被其他箭头覆盖，
    我们需要将所有包含文本的组元素（箭头标签）移到 SVG 文档的末尾。
    """
    try:
        # 注册 SVG 命名空间以正确解析
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

        # 解析 SVG 内容
        root = ET.fromstring(svg_content)

        # 查找主 SVG 容器
        svg_container = root
        if not (root.tag == 'svg' or root.tag.endswith('}svg')):
            # 查找 svg 元素
            for elem in root.iter():
                if elem.tag == 'svg' or elem.tag.endswith('}svg'):
                    svg_container = elem
                    break

        # 收集所有文本组元素（包含 use 元素且具有 fill 属性的 g 元素，这些是箭头标签）
        text_groups = []

        def is_text_group(element):
            """判断是否为文本组元素（箭头标签）"""
            if element.tag == 'g' or element.tag.endswith('}g'):
                # 检查是否有 fill 属性且包含 use 元素
                if element.get('fill'):
                    # 检查是否包含 use 元素
                    for child in element.iter():
                        if child.tag == 'use' or child.tag.endswith('}use'):
                            return True
            return False

        def collect_text_groups(element, parent=None):
            """递归收集所有文本组元素"""
            if is_text_group(element):
                text_groups.append((element, parent))
                return  # 找到文本组后不需要继续向下搜索

            for child in list(element):  # 使用 list() 避免修改迭代器
                collect_text_groups(child, element)

        collect_text_groups(svg_container)

        # 从原位置移除所有文本组元素
        removed_groups = []
        for text_group, parent in text_groups:
            if parent is not None:
                try:
                    parent.remove(text_group)
                    removed_groups.append(text_group)
                except ValueError:
                    # 元素可能已经被移除
                    pass

        # 将所有文本组元素添加到 SVG 容器的末尾，并为它们添加外描边效果
        for text_group in removed_groups:
            # 为每个文本组创建外描边效果
            create_text_stroke_effect(text_group, svg_container, theme)
            svg_container.append(text_group)

        # 输出调试信息
        if removed_groups:
            eprint(f"[DEBUG] 重排序了 {len(removed_groups)} 个文本标签组元素以优化显示层级")

        # 返回修改后的 SVG 内容，保持原有的格式
        result = ET.tostring(root, encoding='unicode')

        # 如果原始内容有 XML 声明，保持它
        if svg_content.strip().startswith('<?xml'):
            xml_decl = svg_content.split('>', 1)[0] + '>'
            if not result.startswith('<?xml'):
                result = xml_decl + '\n' + result

        return result

    except ET.ParseError as e:
        eprint(f"[WARN] SVG 解析失败，跳过元素重排序: {e}")
        return svg_content
    except Exception as e:
        eprint(f"[WARN] SVG 元素重排序失败: {e}")
        return svg_content


def run_neato(dot_content: str, svg_path: pathlib.Path, theme: str = "light"):
    """使用 neato 从 DOT 内容生成指定主题的 SVG"""
    if not shutil.which("neato"):
        eprint("[WARN] 未找到 neato，跳过 SVG 生成")
        return False

    # 使用 common 工具确保输出目录存在
    ensure_dir(str(svg_path.parent))

    # 将主题颜色应用到 DOT 内容中
    themed_dot_content = apply_theme_colors_to_dot(dot_content, theme)

    # 获取主题相关的颜色配置
    theme_mods = get_theme_specific_dot_modifications(theme)

    cmd = [
        "neato",
        "-Gfontname=SF Pro Display",
        "-Nfontname=SF Pro Display",
        "-Efontname=SF Pro Display",
        f"-Gbgcolor={theme_mods['bgcolor']}",
        f"-Gfontcolor={theme_mods['fontcolor']}",
        f"-Nfillcolor={theme_mods['node_fillcolor']}",
        f"-Ncolor={theme_mods['node_color']}",
        f"-Nfontcolor={theme_mods['fontcolor']}",  # 添加节点字体颜色
        f"-Efontcolor={theme_mods['fontcolor']}",
        f"-Ecolor={theme_mods['edge_color']}",
        "-Tsvg:cairo"
    ]

    try:
        result = subprocess.run(
            cmd,
            input=themed_dot_content,  # 使用处理过颜色的 DOT 内容
            text=True,
            capture_output=True,
            check=True
        )

        # 对生成的 SVG 进行后处理，确保箭头标签在最上层并添加描边
        processed_svg = reorder_svg_elements_for_label_priority(result.stdout, theme)

        svg_path.write_text(processed_svg, encoding="utf-8")
        return True
    except Exception as e:
        eprint(f"[WARN] neato 失败 {svg_path.name}: {e}")
        return False
