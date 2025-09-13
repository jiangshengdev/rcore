#!/usr/bin/env python3
"""
WaveDrom 转换器
封装 wavedrom-cli 工具调用，支持主题配置和字体设置
"""

import re
import subprocess
import tempfile
from pathlib import Path

import json5

from .colors import get_theme_config
from .utils import eprint


def analyze_wavedrom_fields(wavedrom_content: str) -> dict:
    """
    分析 WaveDrom 内容，找出1位字段但字符数超过3的情况
    
    Args:
        wavedrom_content: wavedrom JSON 内容
        
    Returns:
        包含需要特殊处理字段信息的字典
    """
    special_fields = {}

    try:
        # 解析 JSON5 内容
        wavedrom_data = json5.loads(wavedrom_content)

        # 检查是否有 reg 字段
        if 'reg' not in wavedrom_data:
            return special_fields

        reg_fields = wavedrom_data['reg']

        for field in reg_fields:
            # 检查必要的字段
            if 'bits' not in field or 'name' not in field or 'attr' not in field:
                continue

            bits_count = field['bits']
            field_name = field['name']
            attr_list = field['attr']

            # 检查是否是1位字段
            if bits_count == 1 and isinstance(attr_list, list) and len(attr_list) > 1:
                # 检查 attr 数组中除第一个元素外是否有字符数超过3的
                for attr_text in attr_list[1:]:  # 跳过第一个元素（位数）
                    if isinstance(attr_text, str) and len(attr_text) > 3:
                        special_fields[field_name] = {
                            'original_text': attr_text,
                            'needs_small_font': True
                        }
                        break

    except (ValueError, KeyError, TypeError) as e:
        # ValueError: json5 解析错误
        # KeyError: 缺少必要字段
        # TypeError: 字段类型不匹配
        eprint(f"解析 WaveDrom 内容时出错: {e}")

    return special_fields


def apply_theme_to_svg(svg_content: str, theme: str, wavedrom_content: str = "") -> str:
    """
    对生成的 SVG 内容应用主题颜色和字体
    这是唯一可行的实现方式，因为 wavedrom-cli 不支持主题配置
    
    Args:
        svg_content: 原始 SVG 内容
        theme: 主题名称 ('light' 或 'dark')
        wavedrom_content: 原始 wavedrom JSON 内容，用于分析特殊字段
        
    Returns:
        应用主题后的 SVG 内容
    """
    theme_config = get_theme_config(theme)
    stroke_color = theme_config["stroke"]

    # 替换默认的黑色描边为主题颜色
    svg_content = svg_content.replace('stroke="black"', f'stroke="{stroke_color}"')

    # 为根 SVG 组添加文本颜色，这样所有文本都会继承这个颜色
    svg_content = svg_content.replace(
        'text-anchor="middle" font-size="14"',
        f'text-anchor="middle" font-size="14" fill="{stroke_color}"'
    )

    # 替换默认字体为 M PLUS 1p（空格字体名必须用引号）
    svg_content = svg_content.replace(
        'font-family="sans-serif"',
        'font-family="\'M PLUS 1p\',\'MPLUS1p-Regular\',monospace"'
    )

    # 处理1位字段但字符数超过3的特殊情况，设置字体大小为12px
    if wavedrom_content:
        special_fields = analyze_wavedrom_fields(wavedrom_content)

        for field_name, field_info in special_fields.items():
            if field_info['needs_small_font']:
                original_text = field_info['original_text']

                # 查找包含该文本的 text 元素（可能包装在 tspan 中），将字体大小改为12px
                # 匹配 <text><tspan>content</tspan></text> 格式
                text_pattern = f'(<text[^>]*>)<tspan>{re.escape(original_text)}</tspan>(</text>)'

                def replace_font_size(match):
                    opening_tag = match.group(1)
                    closing_tag = match.group(2)

                    # 替换或添加 font-size 属性
                    if 'font-size=' in opening_tag:
                        opening_tag = re.sub(r'font-size="[^"]*"', 'font-size="12"', opening_tag)
                    else:
                        # 在 > 之前添加 font-size 属性
                        opening_tag = opening_tag.replace('>', ' font-size="12">')

                    return f'{opening_tag}<tspan>{original_text}</tspan>{closing_tag}'

                svg_content = re.sub(text_pattern, replace_font_size, svg_content)

    return svg_content


def convert_text_to_paths(svg_path: Path) -> bool:
    """
    使用 Inkscape 将 SVG 中的文本转换为路径，以不依赖字体
    
    Args:
        svg_path: SVG 文件路径
        
    Returns:
        转换是否成功
    """
    try:
        # 检查 Inkscape 是否安装
        subprocess.run(['inkscape', '-V'],
                       check=True, capture_output=True)

        # 使用 Inkscape 将文本转换为路径
        subprocess.run([
            'inkscape',
            '-T',  # --export-text-to-path 的简写形式
            '-l',  # --export-plain-svg 移除 Inkscape 特定属性
            f'--export-filename={svg_path}',
            str(svg_path)
        ], check=True, capture_output=True)

        return True

    except FileNotFoundError:
        eprint("错误: 未找到 Inkscape，请先安装 Inkscape")
        eprint("macOS: brew install inkscape")
        eprint("Ubuntu: sudo apt install inkscape")
        return False
    except subprocess.CalledProcessError as e:
        eprint(f"Inkscape 执行失败: {e}")
        return False


def convert_to_svg(wavedrom_content: str, output_path: Path, theme: str) -> bool:
    """
    使用 wavedrom-cli 将 wavedrom 内容转换为 SVG，然后应用主题并转换文本为路径
    
    Args:
        wavedrom_content: wavedrom JSON5 内容
        output_path: 输出 SVG 文件路径
        theme: 主题名称
        
    Returns:
        转换是否成功
    """
    try:
        # 第一步：创建临时输入文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json5', delete=False) as temp_json:
            temp_json.write(wavedrom_content)
            temp_json_path = Path(temp_json.name)

        # 第二步：创建临时输出文件
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.svg', delete=False) as temp_svg:
            temp_svg_path = Path(temp_svg.name)

        try:
            # 第三步：调用 wavedrom-cli 生成基础 SVG
            subprocess.run([
                'wavedrom-cli',
                '-i', str(temp_json_path),
                '-s', str(temp_svg_path)
            ], check=True, capture_output=True)

            # 第四步：读取生成的 SVG 并应用主题
            svg_content = temp_svg_path.read_text(encoding='utf-8')
            themed_svg = apply_theme_to_svg(svg_content, theme, wavedrom_content)

            # 第五步：确保输出目录存在并写入临时文件
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(themed_svg, encoding='utf-8')

            # 第六步：使用 Inkscape 将文本转换为路径
            if not convert_text_to_paths(output_path):
                return False

            return True

        except subprocess.CalledProcessError as e:
            eprint(f"wavedrom-cli 执行失败: {e}")
            return False
        finally:
            # 清理临时文件
            temp_json_path.unlink(missing_ok=True)
            temp_svg_path.unlink(missing_ok=True)

    except Exception as e:
        eprint(f"转换过程中出错: {e}")
        return False
