#!/usr/bin/env python3
"""
WaveDrom SVG 生成器
自动扫描 blog 目录下的 _assets/wavedrom 文件夹，生成 light 和 dark 主题的 SVG 文件
"""

import argparse
import sys

from .colors import THEME_CHOICES
from .converter import convert_to_svg
from .files import find_wavedrom_files
from .parser import extract_wavedrom_content
from .utils import eprint


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="生成 WaveDrom 的 SVG 可视化图形",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成所有主题（默认）
  scripts/lib/wavedrom/main.py
  
  # 只生成 light 主题
  scripts/lib/wavedrom/main.py --theme light
  
  # 只生成 dark 主题  
  scripts/lib/wavedrom/main.py --theme dark
        """
    )

    parser.add_argument(
        '--theme',
        choices=THEME_CHOICES + ['all'],
        default='all',
        help='指定要生成的主题 (默认: all - 生成所有主题)'
    )

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()

    # 确定要处理的主题
    if args.theme == 'all':
        themes = THEME_CHOICES
    else:
        themes = [args.theme]

    print(f"正在处理主题: {', '.join(themes)}")

    try:
        # 查找所有 wavedrom 文件
        wavedrom_files = find_wavedrom_files(themes)

        if not wavedrom_files:
            print("未找到任何 wavedrom 文件")
            return 0

        print(f"找到 {len(wavedrom_files)} 个 wavedrom 文件")

        success_count = 0
        total_count = 0

        # 处理每个文件
        for edn_file, theme_dirs in wavedrom_files:
            print(f"\n处理文件: {edn_file}")

            # 提取 wavedrom 内容
            wavedrom_content = extract_wavedrom_content(edn_file)
            if not wavedrom_content:
                eprint(f"  跳过: 无法提取 wavedrom 内容")
                continue

            # 为每个主题生成 SVG
            for theme, output_dir in theme_dirs:
                output_file = output_dir / f"{edn_file.stem}.svg"
                print(f"  生成 {theme} 主题: {output_file}")

                total_count += 1
                if convert_to_svg(wavedrom_content, output_file, theme):
                    success_count += 1
                    print(f"    ✓ 成功")
                else:
                    eprint(f"    ✗ 失败")

        print(f"\n生成完成: {success_count}/{total_count} 个文件成功")

        if success_count == total_count:
            return 0
        else:
            return 1

    except Exception as e:
        eprint(f"处理过程中出现错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
