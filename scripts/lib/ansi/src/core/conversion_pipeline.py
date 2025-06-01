"""
转换流水线

统一管理整个 ANSI -> HTML -> MDX 的转换流程，
提供简洁的转换接口，封装复杂的转换逻辑。
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from .config_manager import get_config
from .file_processor import FileProcessor, FileInfo
from .mdx_formatter import MdxFormatter
from .tool_manager import get_tool_manager
from ..utils.common import setup_logging, format_file_size
from ..utils.exceptions import ConversionError, ToolError, FileProcessingError

logger = logging.getLogger(__name__)


class ConversionPipeline:
    """
    转换流水线
    
    封装完整的 ANSI -> HTML -> MDX 转换流程，
    提供统一的转换接口和错误处理。
    """

    def __init__(self):
        self.config = get_config()
        self.tool_manager = get_tool_manager()
        self.file_processor = FileProcessor()
        self.mdx_formatter = MdxFormatter()

        logger.debug("转换流水线初始化完成")

    def convert_file(self, input_file: str, output_file: str,
                     title: Optional[str] = None, skip_env_check: bool = False) -> Dict[str, Any]:
        """
        转换单个文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            title: 可选的 MDX 文档标题
            skip_env_check: 是否跳过环境检查
            
        Returns:
            转换结果摘要
            
        Raises:
            ConversionError: 转换失败
        """
        try:
            # 环境检查（可选）
            if not skip_env_check:
                self._validate_environment()

            # 文件分析和验证
            input_info = self._prepare_input(input_file)
            output_path = self._prepare_output(output_file)

            # 执行转换
            html_content = self._convert_to_html(input_info)
            mdx_content = self._convert_to_mdx(html_content, title)

            # 写入输出文件
            self._write_output(output_path, mdx_content)

            # 生成处理摘要
            summary = self._generate_summary(input_info, output_path)

            logger.info("✅ 转换完成!")
            logger.info(f"📄 输入文件: {summary['input_file']}")
            logger.info(f"📄 输出文件: {summary['output_file']} ({format_file_size(summary['output_size'])})")

            return summary

        except Exception as e:
            if isinstance(e, (ConversionError, ToolError, FileProcessingError)):
                raise
            raise ConversionError(f"转换过程中出现未知错误: {e}")

    def _validate_environment(self) -> None:
        """验证环境配置"""
        logger.info("🔍 开始环境验证...")

        # 验证配置
        if not self.config.validate():
            raise ConversionError("配置验证失败")

        # 验证工具环境
        if not self.tool_manager.validate_environment():
            raise ConversionError("工具环境验证失败")

        logger.info("✅ 环境验证完成")

    def _prepare_input(self, input_file: str) -> FileInfo:
        """准备输入文件"""
        logger.info(f"📋 分析输入文件: {input_file}")

        # 分析文件信息
        input_info = self.file_processor.analyze_file(input_file)

        logger.info(f"📄 文件类型: {input_info.content_type}")
        logger.info(f"📄 文件大小: {format_file_size(input_info.size)}")

        return input_info

    def _prepare_output(self, output_file: str) -> Path:
        """准备输出文件路径"""
        logger.info(f"📋 准备输出文件: {output_file}")

        # 直接准备输出文件，不验证输入文件（在这个阶段还未知输入文件）
        output_path = self.file_processor.prepare_output_file(output_file)

        return output_path

    def _convert_to_html(self, input_info: FileInfo) -> str:
        """转换为 HTML 格式"""
        content_type = input_info.content_type or 'unknown'

        if content_type == 'html':
            # HTML 文件直接读取
            logger.info("🔄 检测到 HTML 文件，直接读取...")
            return self.file_processor.read_file_content(input_info)

        elif content_type == 'ansi':
            # ANSI 文件需要转换
            logger.info("🔄 检测到 ANSI 文件，开始转换流程...")
            logger.info("📄 第1步：ANSI -> HTML")

            try:
                html_content = self.tool_manager.convert_ansi_to_html(str(input_info.path))
                logger.info(f"✅ ANSI -> HTML 转换完成 ({len(html_content)} 字符)")
                return html_content
            except ToolError as e:
                # 如果启用了 fallback，尝试使用原始内容
                if self.config.conversion.fallback_to_raw:
                    logger.warning("ANSI 转换失败，使用原始内容作为 fallback")
                    return self.file_processor.read_file_content(input_info)
                else:
                    raise ConversionError(f"ANSI -> HTML 转换失败: {e}")

        else:
            # 其他类型文件
            content = self.file_processor.read_file_content(input_info)

            # 如果内容包含 ANSI 序列且启用自动检测
            if self.config.conversion.auto_detect_ansi and '\033[' in content:
                logger.info("🔄 自动检测到 ANSI 内容，尝试转换...")
                try:
                    return self.tool_manager.convert_ansi_to_html(str(input_info.path))
                except ToolError:
                    logger.warning("ANSI 转换失败，使用原始内容")
                    return content
            else:
                logger.info("📄 使用原始文件内容")
                return content

    def _convert_to_mdx(self, html_content: str, title: Optional[str] = None) -> str:
        """转换为 MDX 格式"""
        logger.info("📄 第2步：HTML -> MDX")

        try:
            mdx_content = self.mdx_formatter.convert_html_to_mdx(html_content, title)
            logger.info("✅ HTML -> MDX 转换完成")
            return mdx_content
        except Exception as e:
            raise ConversionError(f"HTML -> MDX 转换失败: {e}")

    def _write_output(self, output_path: Path, content: str) -> None:
        """写入输出文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise ConversionError(f"输出文件写入失败: {e}")

    def _generate_summary(self, input_info: FileInfo, output_path: Path) -> Dict[str, Any]:
        """生成转换摘要"""
        return self.file_processor.get_processing_summary(input_info, output_path)

    def convert_with_defaults(self, input_file: Optional[str] = None,
                              output_file: Optional[str] = None,
                              title: Optional[str] = None) -> Dict[str, Any]:
        """
        使用默认配置进行转换
        
        如果未提供输入/输出文件，则使用配置中的默认值。
        
        Args:
            input_file: 输入文件路径，None 时使用默认值
            output_file: 输出文件路径，None 时使用默认值
            title: 可选的 MDX 文档标题
            
        Returns:
            转换结果摘要
        """
        # 使用默认文件路径
        if input_file is None:
            input_file = str(self.config.get_default_input_path())
            logger.info(f"[INFO] 使用默认输入文件: {input_file}")

        if output_file is None:
            output_file = str(self.config.get_default_output_path())
            logger.info(f"[INFO] 使用默认输出文件: {output_file}")

        return self.convert_file(input_file, output_file, title)


def convert_ansi_to_mdx(input_file: str, output_file: str,
                        title: Optional[str] = None, verbose: bool = False,
                        skip_env_check: bool = False) -> bool:
    """
    便捷的转换函数，保持与原有接口的兼容性
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        title: 可选的 MDX 文档标题
        verbose: 是否启用详细日志
        skip_env_check: 是否跳过环境检查
        
    Returns:
        转换是否成功
    """
    try:
        # 设置日志
        setup_logging(verbose)

        # 执行转换
        pipeline = ConversionPipeline()
        pipeline.convert_file(input_file, output_file, title, skip_env_check)

        return True

    except Exception as e:
        logger.error(f"❌ 转换失败: {e}")
        return False
