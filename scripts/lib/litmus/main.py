#!/usr/bin/env python3
"""
Litmus 测试 SVG 生成器
自动扫描 docs 目录下的 _assets/litmus 文件夹，生成 light 和 dark 主题的 SVG 文件
"""

import argparse
import pathlib
import shutil
import sys
from typing import List, Tuple

from scripts.lib.common.utils import ensure_dir
from .colors import THEME_CHOICES
from .dot import parse_dot_graphs, apply_theme_colors_to_dot
from .files import find_litmus_files
from .herd import run_herd
from .svg import run_neato
from .utils import eprint


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="生成 Litmus 测试的 SVG 可视化图形",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成所有主题（默认）
  scripts/lib/litmus/main.py
  
  # 只生成 light 主题
  scripts/lib/litmus/main.py --theme light
  
  # 只生成 dark 主题  
  scripts/lib/litmus/main.py --theme dark
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
用法: scripts/lib/litmus/main.py [--theme THEME]
  - 自动扫描 docs/ 目录下的所有 _assets/litmus/ 文件夹
  - 为每个 .litmus 文件生成 SVG 图形到对应的主题目录
  - 生成的目录结构:
    docs/section/_assets/images/light/TestName/graph_01.svg
    docs/section/_assets/images/dark/TestName/graph_01.svg

参数:
  --theme {light,dark,all}  指定主题 (默认: all)

示例: 
  scripts/lib/litmus/main.py --theme light
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


def process_litmus_file(lit_file: pathlib.Path, theme_dirs: List[Tuple[str, pathlib.Path]]) -> int:
    """处理单个 litmus 文件，为所有指定主题生成 SVG"""
    total_exported = 0

    for theme, images_output_dir in theme_dirs:
        # 为当前 litmus 文件和主题创建子目录
        test_output_dir = images_output_dir / lit_file.stem
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
