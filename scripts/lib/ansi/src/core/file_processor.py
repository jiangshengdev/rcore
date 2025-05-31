"""
文件处理器

统一处理输入文件的类型检测、验证和预处理，避免重复的文件操作逻辑。
"""

import logging
from pathlib import Path
from typing import Dict, Any

from .config_manager import get_config
from ..utils.common import validate_file_paths, is_ansi_content, format_file_size
from ..utils.exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class FileInfo:
    """文件信息数据类"""

    def __init__(self, path: Path):
        self.path = path
        self.size = path.stat().st_size if path.exists() else 0
        self.exists = path.exists()
        self.is_file = path.is_file() if path.exists() else False
        self.extension = path.suffix.lower()
        self.content_type = None
        self.encoding = 'utf-8'

    def __str__(self) -> str:
        return f"FileInfo(path={self.path}, size={format_file_size(self.size)}, type={self.content_type})"


class FileProcessor:
    """
    文件处理器
    
    统一处理文件类型检测、内容读取和验证等操作，
    避免在多个模块中重复相同的文件处理逻辑。
    """

    def __init__(self):
        self.config = get_config()
        logger.debug("文件处理器初始化完成")

    def analyze_file(self, file_path: str) -> FileInfo:
        """
        分析文件基本信息和类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息对象
            
        Raises:
            FileProcessingError: 文件分析失败
        """
        try:
            # 获取绝对路径
            abs_path = self.config.get_absolute_input_path(file_path)
            file_info = FileInfo(abs_path)

            if not file_info.exists:
                raise FileProcessingError(f"文件不存在: {abs_path}")

            if not file_info.is_file:
                raise FileProcessingError(f"路径不是文件: {abs_path}")

            # 检测文件类型
            file_info.content_type = self._detect_content_type(file_info)

            logger.debug(f"文件分析完成: {file_info}")
            return file_info

        except Exception as e:
            if isinstance(e, FileProcessingError):
                raise
            raise FileProcessingError(f"文件分析失败: {e}")

    def _detect_content_type(self, file_info: FileInfo) -> str:
        """
        检测文件内容类型
        
        Args:
            file_info: 文件信息对象
            
        Returns:
            内容类型: 'ansi', 'html', 'text'
        """
        # 基于文件扩展名的快速判断
        if file_info.extension in ['.html', '.htm']:
            return 'html'
        elif file_info.extension in ['.ansi']:
            return 'ansi'
        elif file_info.extension in self.config.conversion.supported_extensions:
            # 对于支持的扩展名，需要检查内容
            return self._detect_by_content(file_info.path)
        else:
            # 未知扩展名，通过内容检测
            return self._detect_by_content(file_info.path)

    def _detect_by_content(self, file_path: Path) -> str:
        """
        通过内容检测文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            内容类型
        """
        try:
            # 读取文件开头部分进行检测
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                # 读取前 1KB 进行检测
                sample = f.read(1024)

            # HTML 文件特征检测
            html_indicators = ['<html', '<HTML', '<!DOCTYPE', '<head', '<body']
            if any(indicator in sample for indicator in html_indicators):
                return 'html'

            # ANSI 文件特征检测
            if is_ansi_content(sample):
                return 'ansi'

            # 默认为普通文本
            return 'text'

        except Exception as e:
            logger.warning(f"内容检测失败，使用默认类型: {e}")
            return 'text'

    def read_file_content(self, file_info: FileInfo) -> str:
        """
        读取文件内容
        
        Args:
            file_info: 文件信息对象
            
        Returns:
            文件内容字符串
            
        Raises:
            FileProcessingError: 文件读取失败
        """
        try:
            # 检查文件大小限制
            max_size = self.config.conversion.max_file_size_mb * 1024 * 1024
            if file_info.size > max_size:
                raise FileProcessingError(
                    f"文件过大: {format_file_size(file_info.size)} > {self.config.conversion.max_file_size_mb}MB"
                )

            # 读取文件内容
            with open(file_info.path, 'r', encoding=file_info.encoding, errors='replace') as f:
                content = f.read()

            logger.debug(f"文件内容读取完成: {len(content)} 字符")
            return content

        except Exception as e:
            raise FileProcessingError(f"文件读取失败: {e}")

    def validate_input_output_paths(self, input_file: str, output_file: str) -> None:
        """
        验证输入输出文件路径
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            
        Raises:
            FileProcessingError: 路径验证失败
        """
        # 转换为绝对路径
        input_path = self.config.get_absolute_input_path(input_file)
        output_path = self.config.get_absolute_output_path(output_file)

        # 使用通用验证函数
        is_valid, errors = validate_file_paths(str(input_path), str(output_path))

        if not is_valid:
            error_msg = "文件路径验证失败:\n" + "\n".join(f"  - {error}" for error in errors)
            raise FileProcessingError(error_msg)

        # 如果输出文件已存在，给出警告
        if output_path.exists():
            logger.warning(f"输出文件已存在，将被覆盖: {output_path}")

    def prepare_output_file(self, output_file: str) -> Path:
        """
        准备输出文件
        
        确保输出目录存在，返回输出文件的绝对路径。
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            输出文件的绝对路径
            
        Raises:
            FileProcessingError: 输出文件准备失败
        """
        try:
            output_path = self.config.get_absolute_output_path(output_file)

            # 创建输出目录
            if self.config.conversion.create_dirs:
                output_path.parent.mkdir(parents=True, exist_ok=True)

            return output_path

        except Exception as e:
            raise FileProcessingError(f"输出文件准备失败: {e}")

    def get_processing_summary(self, input_info: FileInfo, output_path: Path) -> Dict[str, Any]:
        """
        获取处理摘要信息
        
        Args:
            input_info: 输入文件信息
            output_path: 输出文件路径
            
        Returns:
            处理摘要字典
        """
        summary = {
            'input_file': str(input_info.path),
            'input_size': input_info.size,
            'input_type': input_info.content_type,
            'output_file': str(output_path),
            'output_size': output_path.stat().st_size if output_path.exists() else 0
        }

        return summary
