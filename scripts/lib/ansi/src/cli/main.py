#!/usr/bin/env python3
"""
ANSI 到 MDX 转换器命令行工具

将 ANSI 文件转换为 Docusaurus 兼容的 MDX 格式。
完整流程：ANSI -> HTML -> MDX
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

# 添加项目路径到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 添加 scripts 目录到路径
scripts_path = project_root / "scripts"
sys.path.insert(0, str(scripts_path))

try:
    from lib.ansi.src.core.mdx_formatter import MdxFormatter, MdxFormatterError
    from lib.ansi.src.utils.terminal_utils import TerminalUtils, TerminalToHtmlError
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在正确的目录中运行此脚本")
    sys.exit(1)


def setup_logging(verbose: bool = False):
    """配置日志记录"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def convert_ansi_to_mdx(input_file: str, output_file: str, title: Optional[str] = None, verbose: bool = False) -> bool:
    """
    转换 ANSI 文件为 MDX 格式
    完整流程：ANSI -> HTML -> MDX
    
    Args:
        input_file: 输入 ANSI 文件路径
        output_file: 输出 MDX 文件路径  
        title: 可选的 MDX 文档标题
        verbose: 是否显示详细日志
        
    Returns:
        bool: 转换是否成功
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # 验证输入文件
        input_path = Path(input_file)
        if not input_path.exists():
            logger.error(f"输入文件不存在: {input_file}")
            return False

        # 检查文件类型并决定处理方式
        is_ansi_file = input_path.suffix.lower() in ['.ansi', '.txt'] or 'ansi' in input_path.name.lower()
        is_html_file = input_path.suffix.lower() in ['.html', '.htm']

        html_content = ""

        if is_ansi_file:
            # ANSI 文件：需要先转换为 HTML
            logger.info(f"🔄 检测到 ANSI 文件，开始转换流程...")

            try:
                # 初始化 terminal-to-html 工具
                terminal_utils = TerminalUtils()
                logger.info(f"✅ terminal-to-html 工具已准备就绪")

                # 转换 ANSI 到 HTML
                logger.info(f"📄 第1步：ANSI -> HTML")
                html_content = terminal_utils.convert_ansi_to_html(input_file)
                logger.info(f"✅ ANSI -> HTML 转换完成 ({len(html_content)} 字符)")

            except TerminalToHtmlError as e:
                logger.error(f"❌ ANSI -> HTML 转换失败: {e}")
                return False

        elif is_html_file:
            # HTML 文件：直接读取
            logger.info(f"🔄 检测到 HTML 文件，直接读取...")
            with open(input_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

        else:
            # 未知文件类型：尝试作为 ANSI 处理
            logger.warning(f"⚠️  未知文件类型，尝试作为 ANSI 文件处理: {input_file}")

            # 读取文件内容检查是否包含 ANSI 转义序列
            with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            if '\033[' in content:
                # 包含 ANSI 转义序列，使用 terminal-to-html 处理
                try:
                    terminal_utils = TerminalUtils()
                    html_content = terminal_utils.convert_ansi_to_html(input_file)
                    logger.info(f"✅ 自动检测并转换 ANSI 内容")
                except TerminalToHtmlError:
                    # 如果 terminal-to-html 失败，直接包装内容
                    html_content = content
                    logger.warning(f"⚠️  ANSI 转换失败，使用原始内容")
            else:
                # 不包含 ANSI 转义序列，直接使用
                html_content = content
                logger.info(f"📄 文件不包含 ANSI 转义序列，直接处理")

        # 第2步：HTML -> MDX
        logger.info(f"📄 第2步：HTML -> MDX")
        formatter = MdxFormatter()

        # 将 HTML 内容转换为 MDX
        mdx_content = formatter.convert_html_to_mdx(html_content, title)

        # 写入输出文件
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(mdx_content)

        # 输出成功信息
        file_size = output_path.stat().st_size
        logger.info(f"✅ 转换完成!")
        logger.info(f"📄 输入文件: {input_file}")
        logger.info(f"📄 输出文件: {output_file} ({file_size} 字节)")
        if title:
            logger.info(f"📝 文档标题: {title}")

        return True

    except MdxFormatterError as e:
        logger.error(f"❌ MDX 格式化错误: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 未知错误: {e}")
        return False


def convert_batch(input_dir: str, output_dir: str, pattern: str = "*.ansi",
                  title_prefix: Optional[str] = None, verbose: bool = False) -> int:
    """
    批量转换 ANSI 文件为 MDX 格式
    
    Args:
        input_dir: 输入目录路径
        output_dir: 输出目录路径
        pattern: 文件匹配模式（默认 "*.ansi"）
        title_prefix: 文档标题前缀
        verbose: 是否显示详细日志
        
    Returns:
        int: 成功转换的文件数量
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if not input_path.exists() or not input_path.is_dir():
            logger.error(f"输入目录不存在或不是目录: {input_dir}")
            return 0

        # 创建输出目录
        output_path.mkdir(parents=True, exist_ok=True)

        # 查找匹配的文件
        files = list(input_path.glob(pattern))
        if not files:
            logger.warning(f"在 {input_dir} 中未找到匹配 '{pattern}' 的文件")
            return 0

        logger.info(f"找到 {len(files)} 个文件待转换")

        # 批量转换
        successful_conversions = 0

        for file in files:
            # 生成输出文件名
            mdx_filename = file.stem + ".mdx"
            output_file = output_path / mdx_filename

            # 生成标题
            title = None
            if title_prefix:
                title = f"{title_prefix} - {file.stem}"

            logger.info(f"转换: {file.name} -> {mdx_filename}")

            try:
                success = convert_ansi_to_mdx(
                    str(file),
                    str(output_file),
                    title,
                    verbose=False  # 批量模式下不显示详细日志
                )

                if success:
                    successful_conversions += 1
                    logger.info(f"  ✅ 成功")
                else:
                    logger.error(f"  ❌ 失败")

            except Exception as e:
                logger.error(f"  ❌ 错误: {e}")

        logger.info(f"批量转换完成: {successful_conversions}/{len(files)} 文件成功")
        return successful_conversions

    except Exception as e:
        logger.error(f"批量转换错误: {e}")
        return 0


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description="将 ANSI 文件转换为 Docusaurus 兼容的 MDX 格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  单文件转换:
    python main.py convert input.ansi output.mdx
    python main.py convert input.ansi output.mdx --title "虚拟内存示例"
    
  批量转换:
    python main.py batch input/ output/
    python main.py batch input/ output/ --pattern "*.ansi" --title-prefix "终端输出"
        """
    )

    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 单文件转换命令
    convert_parser = subparsers.add_parser("convert", help="转换单个 ANSI 文件")
    convert_parser.add_argument("input", help="输入 ANSI 文件路径")
    convert_parser.add_argument("output", help="输出 MDX 文件路径")
    convert_parser.add_argument("--title", "-t", help="MDX 文档标题")
    convert_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    # 批量转换命令
    batch_parser = subparsers.add_parser("batch", help="批量转换 ANSI 文件")
    batch_parser.add_argument("input_dir", help="输入目录路径")
    batch_parser.add_argument("output_dir", help="输出目录路径")
    batch_parser.add_argument("--pattern", "-p", default="*.ansi", help="文件匹配模式 (默认: *.ansi)")
    batch_parser.add_argument("--title-prefix", help="文档标题前缀")
    batch_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    # 解析命令行参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 执行对应命令
    if args.command == "convert":
        success = convert_ansi_to_mdx(args.input, args.output, args.title, args.verbose)
        return 0 if success else 1

    elif args.command == "batch":
        count = convert_batch(
            args.input_dir,
            args.output_dir,
            args.pattern,
            args.title_prefix,
            args.verbose
        )
        return 0 if count > 0 else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
