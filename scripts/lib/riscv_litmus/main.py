#!/usr/bin/env python3
"""
RISC-V Litmus DOT 文件处理主脚本
处理已存在的DOT文件（.txt后缀），生成主题化的SVG文件
"""

import argparse
import pathlib
import shutil
import sys

from scripts.lib.litmus.colors import THEME_CHOICES
from scripts.lib.litmus.utils import eprint
from .processor import find_dot_files, process_dot_file


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="处理RISC-V DOT文件生成主题化SVG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理所有主题（默认）
  scripts/lib/riscv_litmus/main.py
  
  # 只处理 light 主题
  scripts/lib/riscv_litmus/main.py --theme light
  
  # 指定源目录
  scripts/lib/riscv_litmus/main.py --source-dir docs/example/_assets/dot
        """
    )

    parser.add_argument(
        '--theme',
        choices=THEME_CHOICES + ['all'],
        default='all',
        help='指定要生成的主题 (默认: all - 生成所有主题)'
    )

    parser.add_argument(
        '--source-dir',
        type=pathlib.Path,
        default=pathlib.Path("docs/example/_assets/dot"),
        help='源DOT文件目录 (默认: docs/example/_assets/dot)'
    )

    parser.add_argument(
        '--scale',
        type=float,
        default=2.0,
        help='SVG缩放因子 (默认: 2.0 - 2倍大小)'
    )

    return parser.parse_args()


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
        eprint(f"[INFO] 源目录: {args.source_dir}")
        eprint(f"[INFO] 缩放因子: {args.scale}x")

        # 检查必要工具
        which_or_fail("neato", fatal=False)

        # 检查源目录是否存在
        if not args.source_dir.is_dir():
            eprint(f"[ERROR] 源目录不存在: {args.source_dir}")
            return 1

        # 查找DOT文件
        dot_files = find_dot_files(args.source_dir, themes)

        if not dot_files:
            eprint("[INFO] 未找到任何DOT文件")
            return 0

        eprint(f"[INFO] 找到 {len(dot_files)} 个DOT文件")

        # 处理每个文件
        total_exported = 0
        processed_files = 0
        theme_stats = {theme: 0 for theme in themes}

        for dot_file, theme_dirs in dot_files:
            exported = process_dot_file(dot_file, theme_dirs, args.scale)
            if exported > 0:
                total_exported += exported
                processed_files += 1

                # 统计每个主题的生成数量
                for theme, _ in theme_dirs:
                    theme_stats[theme] += exported // len(themes)

        # 输出统计信息
        theme_summary = ', '.join([f"{theme}: {count}" for theme, count in theme_stats.items()])
        eprint(
            f"[SUMMARY] 处理 {processed_files}/{len(dot_files)} 个文件，导出 {total_exported} 个 SVG ({theme_summary})")

        return 0 if total_exported > 0 else 1

    except Exception as e:
        eprint(f"[ERROR] 处理失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
