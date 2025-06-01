#!/usr/bin/env python3
"""
ANSI 到 MDX 转换器命令行工具 - 重构版本

将 ANSI 文件转换为 Docusaurus 兼容的 MDX 格式。
重构后的版本提供更简洁的接口和更好的性能。
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, List

# 添加项目路径到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
scripts_path = project_root / "scripts"
sys.path.insert(0, str(scripts_path))

try:
    from ..core.conversion_pipeline import convert_ansi_to_mdx
    from ..core.config_manager import get_config, validate_config
    from ..utils.common import setup_logging, validate_files
    from ..utils.exceptions import MdxFormatterError, TerminalToHtmlError
    from ..utils.environment import EnvironmentValidator
    from ..core.mdx_formatter import MdxFormatter
    from ..utils.terminal_utils import TerminalUtils
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在正确的目录中运行此脚本")
    sys.exit(1)


def setup_logging(verbose: bool = False, use_config: bool = True):
    """配置日志记录 - 增强版本支持配置文件"""
    if use_config:
        try:
            config = get_config()
            level_name = config.logging.verbose_level if verbose else config.logging.default_level
            format_str = config.logging.log_format
        except Exception:
            # 如果配置加载失败，使用默认设置
            level_name = "DEBUG" if verbose else "INFO"
            format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    else:
        level_name = "DEBUG" if verbose else "INFO"
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def check_environment_and_config() -> bool:
    """检查环境和配置 - 新增的综合检查函数"""
    logger = logging.getLogger(__name__)

    try:
        # 验证配置
        if not validate_config():
            logger.error("配置验证失败")
            return False

        # 验证环境
        validator = EnvironmentValidator()
        if not validator.validate_environment():
            logger.error("环境验证失败")
            return False

        logger.debug("环境和配置检查完成")
        return True

    except Exception as e:
        logger.error(f"环境检查过程中出错: {e}")
        return False


def convert_ansi_to_mdx(input_file: str, output_file: str, title: Optional[str] = None,
                        verbose: bool = False, skip_env_check: bool = False) -> bool:
    """
    转换 ANSI 文件为 MDX 格式 - 增强版本
    完整流程：ANSI -> HTML -> MDX
    
    Args:
        input_file: 输入 ANSI 文件路径
        output_file: 输出 MDX 文件路径  
        title: 可选的 MDX 文档标题
        verbose: 是否显示详细日志
        skip_env_check: 是否跳过环境检查（用于批量处理优化）
        
    Returns:
        bool: 转换是否成功
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # 环境和配置检查（可选）
        if not skip_env_check:
            if not check_environment_and_config():
                logger.error("环境检查失败，无法继续")
                return False

        # 文件验证 - 使用新的验证模块
        files_valid, validation_errors = validate_files(input_file, output_file)
        if not files_valid:
            for error in validation_errors:
                logger.error(error)
            return False

        # 获取配置以支持默认路径处理
        config = get_config()

        # 转换为绝对路径
        input_path = Path(input_file)
        output_path = Path(output_file)

        if not input_path.is_absolute():
            input_path = config.get_absolute_input_path(input_file)

        if not output_path.is_absolute():
            output_path = config.get_absolute_output_path(output_file)

        # 检查文件类型并决定处理方式
        is_ansi_file = input_path.suffix.lower() in config.conversion.supported_input_extensions or 'ansi' in input_path.name.lower()
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
                html_content = terminal_utils.convert_ansi_to_html(str(input_path))
                logger.info(f"✅ ANSI -> HTML 转换完成 ({len(html_content)} 字符)")

            except TerminalToHtmlError as e:
                logger.error(f"❌ ANSI -> HTML 转换失败: {e}")
                if config.conversion.fallback_to_raw_content:
                    logger.warning("尝试使用原始内容作为fallback")
                    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
                        html_content = f.read()
                else:
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

            if '\033[' in content and config.conversion.auto_detect_ansi:
                # 包含 ANSI 转义序列，使用 terminal-to-html 处理
                try:
                    terminal_utils = TerminalUtils()
                    html_content = terminal_utils.convert_ansi_to_html(str(input_path))
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

        # 确保输出目录存在
        if config.conversion.create_output_dirs:
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入输出文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(mdx_content)

        # 输出成功信息
        file_size = output_path.stat().st_size
        logger.info(f"✅ 转换完成!")
        logger.info(f"📄 输入文件: {input_path}")
        logger.info(f"📄 输出文件: {output_path} ({file_size} 字节)")
        if title:
            logger.info(f"📝 文档标题: {title}")

        return True

    except MdxFormatterError as e:
        logger.error(f"❌ MDX 格式化错误: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 未知错误: {e}")
        if verbose:
            import traceback
            logger.error(traceback.format_exc())
        return False


def convert_batch(input_dir: str, output_dir: str, pattern: str = "*.ansi",
                  title_prefix: Optional[str] = None, verbose: bool = False) -> int:
    """
    批量转换 ANSI 文件为 MDX 格式 - 增强版本
    
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
        # 首先进行环境检查（只在批量开始时检查一次）
        if not check_environment_and_config():
            logger.error("环境检查失败，无法进行批量转换")
            return 0

        config = get_config()

        input_path = Path(input_dir)
        output_path = Path(output_dir)

        # 输入路径验证
        if not input_path.is_absolute():
            input_path = config.get_absolute_input_path(input_dir)

        if not output_path.is_absolute():
            output_path = config.get_absolute_output_path(output_dir)

        if not input_path.exists() or not input_path.is_dir():
            logger.error(f"输入目录不存在或不是目录: {input_path}")
            return 0

        # 创建输出目录
        if config.conversion.create_output_dirs:
            output_path.mkdir(parents=True, exist_ok=True)

        # 查找匹配的文件 - 支持多种模式
        patterns = pattern.split(',') if ',' in pattern else [pattern]
        files: List[Path] = []

        for pat in patterns:
            pat = pat.strip()
            found_files = list(input_path.glob(pat))
            files.extend(found_files)
            logger.debug(f"模式 '{pat}' 找到 {len(found_files)} 个文件")

        # 去重（如果有重叠的模式）
        files = list(set(files))

        if not files:
            logger.warning(f"在 {input_path} 中未找到匹配 '{pattern}' 的文件")
            return 0

        logger.info(f"找到 {len(files)} 个文件待转换")

        # 批量转换
        successful_conversions = 0
        failed_conversions: List[str] = []

        for i, file in enumerate(files, 1):
            # 生成输出文件名
            mdx_filename = file.stem + ".mdx"
            output_file = output_path / mdx_filename

            # 生成标题
            title = None
            if title_prefix:
                title = f"{title_prefix} - {file.stem}"

            logger.info(f"[{i}/{len(files)}] 转换: {file.name} -> {mdx_filename}")

            try:
                # 批量模式跳过重复的环境检查
                success = convert_ansi_to_mdx(
                    str(file),
                    str(output_file),
                    title,
                    verbose=False,  # 批量模式下不显示详细日志
                    skip_env_check=True
                )

                if success:
                    successful_conversions += 1
                    logger.info(f"  ✅ 成功")
                else:
                    failed_conversions.append(file.name)
                    logger.error(f"  ❌ 失败")

            except Exception as e:
                failed_conversions.append(file.name)
                logger.error(f"  ❌ 错误: {e}")

        # 输出批量转换总结
        logger.info(f"批量转换完成: {successful_conversions}/{len(files)} 文件成功")

        if failed_conversions:
            logger.warning(f"失败的文件 ({len(failed_conversions)}):")
            for failed_file in failed_conversions:
                logger.warning(f"  - {failed_file}")

        return successful_conversions

    except Exception as e:
        logger.error(f"批量转换错误: {e}")
        return 0


def main():
    """主函数 - 命令行接口 - 增强版本支持默认参数和更好的帮助"""
    parser = argparse.ArgumentParser(
        description="将 ANSI 文件转换为 Docusaurus 兼容的 MDX 格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  单文件转换:
    python main.py convert input.ansi output.mdx
    python main.py convert input.ansi output.mdx --title "虚拟内存示例"
    
  使用默认文件（无参数时）:
    python main.py convert
    
  批量转换:
    python main.py batch input/ output/
    python main.py batch input/ output/ --pattern "*.ansi" --title-prefix "终端输出"
    
  环境检查:
    python main.py convert --check-env
        """
    )

    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 单文件转换命令 - 增强版本
    convert_parser = subparsers.add_parser("convert", help="转换单个 ANSI 文件")
    convert_parser.add_argument("input", nargs='?', help="输入 ANSI 文件路径（可选，使用默认文件）")
    convert_parser.add_argument("output", nargs='?', help="输出 MDX 文件路径（可选，使用默认文件）")
    convert_parser.add_argument("--title", "-t", help="MDX 文档标题")
    convert_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    convert_parser.add_argument("--check-env", action="store_true", help="执行环境检查")

    # 批量转换命令 - 增强版本
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
        # 处理默认参数
        config = get_config()

        input_file = args.input
        output_file = args.output

        # 如果没有提供输入文件，使用默认文件
        if input_file is None:
            input_file = str(config.get_default_input_file())
            print(f"[INFO] 使用默认输入文件: {input_file}")

        # 如果没有提供输出文件，使用默认文件
        if output_file is None:
            output_file = str(config.get_default_output_file())
            print(f"[INFO] 使用默认输出文件: {output_file}")

        # 执行环境检查（如果请求）
        if args.check_env:
            print("[INFO] 执行环境检查...")
            if not check_environment_and_config():
                print("[ERROR] 环境检查失败")
                return 1
            print("[INFO] ✅ 环境检查通过")

        success = convert_ansi_to_mdx(input_file, output_file, args.title, args.verbose)
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
