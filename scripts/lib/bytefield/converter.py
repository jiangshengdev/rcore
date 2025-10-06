"""
SVG 转换和主题应用模块。

此模块负责将 bytefield 内容转换为 SVG 格式，
应用主题颜色，并将文本转换为路径。
"""

import subprocess
import tempfile
from pathlib import Path

from .colors import get_theme_config
from .utils import eprint


def apply_theme_to_svg(svg_content: str, theme: str) -> str:
    """
    对生成的 SVG 内容应用主题颜色。
    
    修改内容：
    1. 替换描边颜色（stroke）
    2. 设置填充颜色（fill）
    3. 确保背景透明
    4. 为文本元素添加填充颜色（Inkscape 转换时会保留）
    5. 替换字体为 'M+ 1p Fallback'
    
    参数:
        svg_content: 原始 SVG 内容
        theme: 主题名称（'light' 或 'dark'）
        
    返回:
        应用主题后的 SVG 内容
    """
    import re

    # 获取主题配置
    theme_config = get_theme_config(theme)
    stroke_color = theme_config['stroke']

    # 替换描边颜色
    # bytefield-svg 生成的 SVG 使用黑色作为默认描边颜色
    svg_content = svg_content.replace('stroke="#000000"', f'stroke="{stroke_color}"')
    svg_content = svg_content.replace('stroke="#000"', f'stroke="{stroke_color}"')
    svg_content = svg_content.replace('stroke="black"', f'stroke="{stroke_color}"')

    # 确保背景透明（移除可能的背景填充）
    svg_content = svg_content.replace('fill="white"', 'fill="none"')
    svg_content = svg_content.replace('fill="#ffffff"', 'fill="none"')
    svg_content = svg_content.replace('fill="#fff"', 'fill="none"')

    # 替换字体设置
    # 使用与 wavedrom 相同的字体列表以保持一致性
    wavedrom_font = "'M PLUS 1p','MPLUS1p-Regular',monospace"
    # 使用正则表达式一次性替换所有 font-family 属性
    svg_content = re.sub(
        r'font-family=["\']([^"\']+)["\']',
        f'font-family="{wavedrom_font}"',
        svg_content
    )

    # 为 <text> 元素添加 fill 属性（如果没有的话）
    # Inkscape 转换文本为路径时会保留 fill 颜色
    def add_fill_to_text(match):
        text_tag = match.group(0)
        # 如果已经有 fill 属性，不修改
        if 'fill=' in text_tag:
            return text_tag
        # 在 <text 后面添加 fill 属性
        return text_tag.replace('<text', f'<text fill="{stroke_color}"', 1)

    svg_content = re.sub(r'<text[^>]*>', add_fill_to_text, svg_content)

    # 为 <path> 元素添加 fill 属性（如果没有的话）
    # 这是为了确保已经转换的路径也有正确的颜色
    def add_fill_to_path(match):
        path_tag = match.group(0)
        # 如果已经有 fill 属性，不修改
        if 'fill=' in path_tag:
            return path_tag
        # 在 <path 后面添加 fill 属性
        return path_tag.replace('<path', f'<path fill="{stroke_color}"', 1)

    svg_content = re.sub(r'<path[^>]*>', add_fill_to_path, svg_content)

    return svg_content


def convert_text_to_paths(svg_path: Path) -> bool:
    """
    使用 Inkscape 将 SVG 中的文本转换为路径，以不依赖字体。
    
    这是必不可少的步骤，确保 SVG 在任何环境下都能正确显示。
    文本转换为路径后，不再依赖系统字体，保证跨平台一致性。
    
    参数:
        svg_path: SVG 文件路径
        
    返回:
        转换是否成功
    """
    try:
        # 使用 Inkscape 将文本转换为路径
        # -T: 将文本转换为路径
        # -l: 输出为纯 SVG（不包含 Inkscape 特定元素）
        # --export-filename: 指定输出文件（覆盖原文件）
        result = subprocess.run(
            [
                'inkscape',
                '-T',
                '-l',
                '--export-filename=' + str(svg_path),
                str(svg_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return True

    except subprocess.CalledProcessError as e:
        eprint(f"Inkscape 转换失败: {e.stderr}")
        return False
    except FileNotFoundError:
        eprint("错误: 未找到 Inkscape，请先安装 Inkscape")
        eprint("macOS: brew install inkscape")
        eprint("Ubuntu: sudo apt install inkscape")
        return False


def convert_to_svg(bytefield_content: str, output_path: Path, theme: str) -> bool:
    """
    将 bytefield 内容转换为 SVG 并应用主题。
    
    转换流程：
    1. 创建临时输入文件（纯 bytefield 内容）
    2. 调用 bytefield-svg 生成基础 SVG
    3. 读取生成的 SVG
    4. 应用主题颜色
    5. 写入最终输出文件
    6. 使用 Inkscape 将文本转换为路径
    7. 清理临时文件
    
    参数:
        bytefield_content: bytefield 内容
        output_path: 输出 SVG 文件路径
        theme: 主题名称（'light' 或 'dark'）
        
    返回:
        转换是否成功
    """
    temp_input = None
    temp_output = None

    try:
        # 创建临时输入文件
        temp_input = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.edn',
            delete=False,
            encoding='utf-8'
        )
        temp_input.write(bytefield_content)
        temp_input.close()

        # 创建临时输出文件
        temp_output = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.svg',
            delete=False,
            encoding='utf-8'
        )
        temp_output.close()

        # 调用 bytefield-svg 生成 SVG
        result = subprocess.run(
            [
                'bytefield-svg',
                '--source', temp_input.name,
                '--output', temp_output.name
            ],
            capture_output=True,
            text=True,
            check=True
        )

        # 读取生成的 SVG
        svg_content = Path(temp_output.name).read_text(encoding='utf-8')

        # 应用主题颜色
        svg_content = apply_theme_to_svg(svg_content, theme)

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入最终输出文件
        output_path.write_text(svg_content, encoding='utf-8')

        # 使用 Inkscape 将文本转换为路径
        if not convert_text_to_paths(output_path):
            eprint(f"警告: 文本转路径失败，但 SVG 文件已生成: {output_path}")
            # 即使文本转路径失败，也认为转换成功（SVG 已生成）
            return True

        return True

    except subprocess.CalledProcessError as e:
        eprint(f"bytefield-svg 转换失败: {e.stderr}")
        return False
    except FileNotFoundError:
        eprint("错误: 未找到 bytefield-svg，请先安装")
        eprint("安装方法: npm install -g bytefield-svg")
        return False
    except Exception as e:
        eprint(f"转换过程出错: {str(e)}")
        return False
    finally:
        # 清理临时文件
        if temp_input:
            try:
                Path(temp_input.name).unlink(missing_ok=True)
            except:
                pass
        if temp_output:
            try:
                Path(temp_output.name).unlink(missing_ok=True)
            except:
                pass
