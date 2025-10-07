#!/usr/bin/env python3
"""
bytefield 转换器主入口模块

该模块负责命令行参数解析、流程编排和结果统计。
"""

import argparse
import sys

from .colors import THEME_CHOICES
from .converter import convert_to_svg
from .files import find_bytefield_files
from .params import process_bytefield_params
from .parser import extract_bytefield_content
from .utils import eprint


def parse_args() -> argparse.Namespace:
    """
    解析命令行参数
    
    返回:
        解析后的命令行参数对象
    """
    parser = argparse.ArgumentParser(
        description='将 bytefield EDN 文件转换为主题化的 SVG 图表'
    )

    parser.add_argument(
        '--theme',
        choices=THEME_CHOICES + ['all'],
        default='all',
        help='要生成的主题 (light, dark, 或 all，默认: all)'
    )

    return parser.parse_args()


def main() -> int:
    """
    主函数，执行完整的转换流程
    
    流程:
        1. 解析命令行参数
        2. 查找所有 bytefield 文件
        3. 处理每个文件，为每个主题生成 SVG
        4. 输出处理进度和结果
        5. 打印统计摘要
    
    返回:
        退出码 (0 表示全部成功，1 表示有失败)
    """
    # 1. 解析命令行参数
    args = parse_args()

    # 确定要生成的主题列表
    if args.theme == 'all':
        themes = THEME_CHOICES
    else:
        themes = [args.theme]

    # 2. 查找所有 bytefield 文件
    print(f"正在扫描 bytefield 文件...")
    bytefield_files = find_bytefield_files(themes)

    if not bytefield_files:
        print("未找到任何 bytefield 文件")
        return 0

    print(f"找到 {len(bytefield_files)} 个文件\n")

    # 统计变量
    total_conversions = 0
    successful_conversions = 0
    failed_conversions = 0

    # 3. 处理每个文件
    for edn_file_path, theme_outputs in bytefield_files:
        # 显示正在处理的文件
        print(f"处理: {edn_file_path.name}")

        # 提取 bytefield 内容
        bytefield_content = extract_bytefield_content(edn_file_path)

        if bytefield_content is None:
            eprint(f"  ✗ 无法从文件中提取 bytefield 内容")
            # 计算该文件所有主题的失败数
            failed_conversions += len(theme_outputs)
            total_conversions += len(theme_outputs)
            continue

        # 处理参数（注入/替换 left-margin, right-margin, box-width）
        processed_content, param_info = process_bytefield_params(bytefield_content)

        # 为每个主题生成 SVG
        for theme, output_path in theme_outputs:
            total_conversions += 1

            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 转换为 SVG（使用处理后的内容）
            success = convert_to_svg(processed_content, output_path, theme)

            if success:
                print(f"  ✓ {theme}: {output_path}")
                successful_conversions += 1
            else:
                eprint(f"  ✗ {theme}: 转换失败")
                failed_conversions += 1

        print()  # 文件之间添加空行

    # 5. 打印统计摘要
    print("=" * 50)
    print(f"转换完成: {successful_conversions}/{total_conversions} 成功")

    if failed_conversions > 0:
        print(f"失败: {failed_conversions}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
