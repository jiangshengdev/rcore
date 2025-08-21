#!/usr/bin/env python3
"""
Litmus 测试 SVG 生成器
自动扫描 docs 目录下的 _assets/litmus 文件夹，生成 light 和 dark 主题的 SVG 文件
"""

import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
from typing import List, Tuple

from scripts.lib.common.utils import find_project_root, ensure_dir
from .colors import get_litmus_theme_colors, THEME_CHOICES
from .herd_config import build_herd_args, get_theme_specific_dot_modifications


def eprint(*args, **kwargs):
    """输出到标准错误流"""
    print(*args, file=sys.stderr, **kwargs)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="生成 Litmus 测试的 SVG 可视化图形",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成所有主题（默认）
  scripts/lib/litmus/litmus_to_svg.py
  
  # 只生成 light 主题
  scripts/lib/litmus/litmus_to_svg.py --theme light
  
  # 只生成 dark 主题  
  scripts/lib/litmus/litmus_to_svg.py --theme dark
        """
    )

    parser.add_argument(
        '--theme',
        choices=THEME_CHOICES + ['all'],
        default='all',
        help='指定要生成的主题 (默认: all - 生成所有主题)'
    )

    return parser.parse_args()


def usage():
    """显示使用说明"""
    eprint("""
用法: scripts/lib/litmus/litmus_to_svg.py [--theme THEME]
  - 自动扫描 docs/ 目录下的所有 _assets/litmus/ 文件夹
  - 为每个 .litmus 文件生成 SVG 图形到对应的主题目录
  - 生成的目录结构:
    docs/section/_assets/svg/light/TestName/graph_01.svg
    docs/section/_assets/svg/dark/TestName/graph_01.svg

参数:
  --theme {light,dark,all}  指定主题 (默认: all)

示例: 
  scripts/lib/litmus/litmus_to_svg.py --theme light
    """)


def which_or_fail(name: str, fatal: bool = True) -> bool:
    """检查命令是否存在"""
    if shutil.which(name):
        return True
    msg = f"[ERROR] 未找到 {name}"
    if fatal:
        eprint(msg)
        sys.exit(127)
    else:
        eprint("[WARN] " + msg + " : 某些功能将被跳过")
        return False


def find_litmus_files(themes: List[str]) -> List[Tuple[pathlib.Path, List[Tuple[str, pathlib.Path]]]]:
    """查找所有的 litmus 文件及其对应的主题输出目录"""
    # 使用 common 工具查找项目根目录
    repo_root_str = find_project_root()
    if not repo_root_str:
        raise FileNotFoundError("无法找到项目根目录")

    repo_root = pathlib.Path(repo_root_str)
    docs_dir = repo_root / "docs"

    if not docs_dir.is_dir():
        raise FileNotFoundError(f"找不到 docs 目录: {docs_dir}")

    litmus_files = []

    # 递归查找所有 _assets/litmus 目录
    for litmus_dir in docs_dir.rglob("_assets/litmus"):
        if not litmus_dir.is_dir():
            continue

        # 查找该目录下的所有 .litmus 文件
        for litmus_file in litmus_dir.glob("*.litmus"):
            # 为每个主题创建对应的输出目录
            theme_dirs = []
            for theme in themes:
                svg_theme_dir = litmus_dir.parent / "svg" / theme
                theme_dirs.append((theme, svg_theme_dir))

            litmus_files.append((litmus_file, theme_dirs))

    return litmus_files


def run_herd(lit: pathlib.Path, theme: str = "light", output_dir: pathlib.Path = None) -> pathlib.Path:
    """运行 herd7 生成指定主题的 DOT 文件"""
    # 如果指定了输出目录，使用它，否则使用临时目录
    if output_dir:
        ensure_dir(str(output_dir))
        dot_path = output_dir / f"{lit.stem}.dot"  # 去掉主题后缀，因为已经在主题目录中
        work_dir = output_dir
    else:
        # 在临时目录生成 DOT 文件
        work_dir = pathlib.Path(tempfile.mkdtemp())
        dot_path = work_dir / (lit.stem + ".dot")

    # 使用新的配置生成器构建参数
    herd_args = build_herd_args(lit, theme, work_dir)

    eprint(f"[INFO] 处理 {lit.name} ({theme} 主题)")
    try:
        subprocess.run(herd_args, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        eprint(f"[WARN] herd7 执行失败 {lit.name} ({theme}): {e}")
        return None

    # herd7 总是生成以原始文件名命名的 DOT 文件
    original_dot = work_dir / (lit.stem + ".dot")
    if not original_dot.is_file():
        eprint(f"[WARN] herd7 未生成 DOT 文件: {original_dot}")
        return None

    # 如果需要重命名（包含主题信息），则重命名
    if output_dir and dot_path != original_dot:
        original_dot.rename(dot_path)
        return dot_path
    else:
        return original_dot


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


def create_text_stroke_effect(text_group, svg_container, theme="light"):
    """
    为文本组创建外描边效果
    
    通过复制文本组并在原始文本之前插入描边版本来实现外描边
    """
    import copy

    try:
        # 从 colors.py 导入系统颜色
        from .colors import SYSTEM_WHITE, WEB_BACKGROUND_DARK

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
    import xml.etree.ElementTree as ET

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


def process_litmus_file(lit_file: pathlib.Path, theme_dirs: List[Tuple[str, pathlib.Path]]) -> int:
    """处理单个 litmus 文件，为所有指定主题生成 SVG"""
    total_exported = 0

    for theme, svg_output_dir in theme_dirs:
        # 为当前 litmus 文件和主题创建子目录
        test_output_dir = svg_output_dir / lit_file.stem
        ensure_dir(str(test_output_dir))

        # 为每个主题运行 herd7，保留 DOT 文件到输出目录
        dot_file = run_herd(lit_file, theme, test_output_dir)
        if not dot_file:
            continue

        graphs = parse_dot_graphs(dot_file)
        if not graphs:
            eprint(f"[WARN] 未找到图形数据: {lit_file.name} ({theme})")
            continue

        exported = 0
        for i, graph_lines in enumerate(graphs, 1):
            if not graph_lines:
                continue

            # 保持原始图形内容
            graph_content = "\n".join(graph_lines)

            # 确保图形格式正确
            if not graph_content.rstrip().endswith('}'):
                continue

            # 应用主题颜色到图形内容
            themed_graph_content = apply_theme_colors_to_dot(graph_content, theme)

            # 保存分割后的 DOT 文件（参考 simple_extract.py）
            individual_dot_path = test_output_dir / f"graph_{i:02d}.dot"
            individual_dot_path.write_text(themed_graph_content + "\n", encoding="utf-8")

            # 生成对应的 SVG，使用已经应用颜色的内容
            svg_path = test_output_dir / f"graph_{i:02d}.svg"
            if run_neato(graph_content, svg_path, theme):  # run_neato 内部会再次应用颜色
                exported += 1

        # 保留完整的 DOT 文件用于调试
        eprint(f"[DEBUG] 完整 DOT 文件保存为: {dot_file}")

        if exported > 0:
            eprint(f"[INFO] {lit_file.name} ({theme}): 生成 {exported} 个 SVG -> {test_output_dir}")
            total_exported += exported

    return total_exported


def main() -> int:
    """主函数"""
    try:
        # 解析命令行参数
        args = parse_args()

        # 确定要生成的主题列表
        if args.theme == 'all':
            themes = THEME_CHOICES
        else:
            themes = [args.theme]

        eprint(f"[INFO] 生成主题: {', '.join(themes)}")

        # 检查必要工具
        which_or_fail("herd7", fatal=True)
        which_or_fail("neato", fatal=False)

        # 查找所有 litmus 文件
        litmus_files = find_litmus_files(themes)
        if not litmus_files:
            eprint("[INFO] 未找到任何 litmus 文件")
            return 0

        total_exported = 0
        processed_files = 0
        theme_stats = {theme: 0 for theme in themes}

        for lit_file, theme_dirs in litmus_files:
            exported = process_litmus_file(lit_file, theme_dirs)
            if exported > 0:
                total_exported += exported
                processed_files += 1

                # 统计每个主题的生成数量
                for theme, _ in theme_dirs:
                    theme_stats[theme] += exported // len(themes)  # 假设每个主题生成相同数量的文件

        # 输出统计信息
        theme_summary = ', '.join([f"{theme}: {count}" for theme, count in theme_stats.items()])
        eprint(
            f"[SUMMARY] 处理 {processed_files}/{len(litmus_files)} 个文件，导出 {total_exported} 个 SVG ({theme_summary})")

        return 0 if total_exported > 0 else 4

    except Exception as e:
        eprint(f"[ERROR] 未知错误: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        usage()
        sys.exit(0)

    raise SystemExit(main())
