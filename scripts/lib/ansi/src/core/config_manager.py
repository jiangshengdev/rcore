"""
统一配置管理器

单例模式管理所有配置项，提供统一的配置访问接口，避免重复的配置加载和验证。
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Optional, Any

from ..utils.common import find_project_root
from ..utils.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class ConversionConfig:
    """转换相关配置"""
    # 输入输出设置
    default_input_file: str = "_assets/data/input.ansi"
    default_output_file: str = "_assets/output/_output.pre.mdx"
    max_file_size_mb: int = 50

    # 转换选项
    auto_detect_ansi: bool = True
    fallback_to_raw: bool = True  # ANSI转换失败时回退到原始内容
    fallback_to_raw_content: bool = True  # 与 main.py 兼容的别名
    create_dirs: bool = True  # 自动创建输出目录
    create_output_dirs: bool = True  # 与 main.py 兼容的别名

    def __post_init__(self):
        # 支持的文件扩展名
        self.supported_extensions = ['.ansi', '.txt', '.html', '.htm']
        # 兼容性：确保别名指向相同数据
        self.supported_input_extensions = self.supported_extensions

        # 确保兼容属性同步
        if self.fallback_to_raw != self.fallback_to_raw_content:
            self.fallback_to_raw_content = self.fallback_to_raw
        if self.create_dirs != self.create_output_dirs:
            self.create_output_dirs = self.create_dirs


@dataclass
class ToolConfig:
    """工具配置的简化版本"""
    terminal_timeout: int = 30

    def __post_init__(self):
        self.required_tools = ["python3", "terminal-to-html"]


@dataclass
class LogConfig:
    """日志配置的简化版本"""
    default_level: str = "INFO"
    verbose_level: str = "DEBUG"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class ConfigManager:
    """
    配置管理器单例类
    
    统一管理所有配置项，避免重复加载和验证配置。
    采用单例模式确保配置的一致性。
    """

    _instance: Optional['ConfigManager'] = None
    _lock = Lock()

    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return

        self._initialized = True

        # 初始化配置对象
        self.conversion = ConversionConfig()
        self.tool = ToolConfig()
        self.logging = LogConfig()  # 兼容 main.py 中的 config.logging

        # 初始化路径（延迟到访问时）
        self._project_root: Optional[Path] = None
        self._ansi_dir: Optional[Path] = None

        logger.debug("配置管理器初始化完成")

    def _setup_paths(self) -> None:
        """初始化项目路径"""
        if self._project_root is None:
            try:
                self._project_root = find_project_root()
                self._ansi_dir = self._project_root / "scripts" / "lib" / "ansi"
                logger.debug(f"项目根目录: {self._project_root}")
                logger.debug(f"ANSI 模块目录: {self._ansi_dir}")
            except Exception as e:
                raise ConfigurationError(f"路径初始化失败: {e}")

    @property
    def project_root(self) -> Path:
        """获取项目根目录"""
        if self._project_root is None:
            self._setup_paths()
        return self._project_root  # type: ignore

    @property
    def ansi_dir(self) -> Path:
        """获取 ANSI 模块目录"""
        if self._ansi_dir is None:
            self._setup_paths()
        return self._ansi_dir  # type: ignore

    def get_absolute_input_path(self, input_file: str) -> Path:
        """
        获取输入文件的绝对路径
        
        如果是相对路径，则相对于 ANSI 模块目录解析。
        
        Args:
            input_file: 输入文件路径
            
        Returns:
            绝对路径
        """
        input_path = Path(input_file)
        if input_path.is_absolute():
            return input_path

        # 相对路径相对于 ANSI 模块目录
        return (self.ansi_dir / input_path).resolve()

    def get_absolute_output_path(self, output_file: str) -> Path:
        """
        获取输出文件的绝对路径
        
        如果是相对路径，则相对于 ANSI 模块目录解析。
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            绝对路径
        """
        output_path = Path(output_file)
        if output_path.is_absolute():
            return output_path

        # 相对路径相对于 ANSI 模块目录
        return (self.ansi_dir / output_path).resolve()

    def get_default_input_path(self) -> Path:
        """获取默认输入文件路径"""
        return self.get_absolute_input_path(self.conversion.default_input_file)

    def get_default_output_path(self) -> Path:
        """获取默认输出文件路径"""
        return self.get_absolute_output_path(self.conversion.default_output_file)

    def validate(self) -> bool:
        """
        验证配置有效性
        
        Returns:
            配置是否有效
        """
        try:
            # 检查项目根目录
            if not self.project_root.exists():
                logger.error(f"项目根目录不存在: {self.project_root}")
                return False

            # 检查 ANSI 模块目录
            if not self.ansi_dir.exists():
                logger.error(f"ANSI 模块目录不存在: {self.ansi_dir}")
                return False

            # 检查默认输入文件（如果指定了相对路径）
            default_input = self.get_default_input_path()
            if not default_input.exists():
                logger.warning(f"默认输入文件不存在: {default_input}")

            logger.debug("配置验证通过")
            return True

        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False

    def update_config(self, **kwargs: Any) -> None:
        """
        动态更新配置项
        
        Args:
            **kwargs: 配置项键值对
        """
        for key, value in kwargs.items():
            if hasattr(self.conversion, key):
                setattr(self.conversion, key, value)
            elif hasattr(self.tool, key):
                setattr(self.tool, key, value)
            elif hasattr(self.logging, key):
                setattr(self.logging, key, value)
            else:
                logger.warning(f"未知配置项: {key}")

    def get_default_input_file(self) -> Path:
        """获取默认输入文件路径 - 兼容 main.py"""
        return self.get_default_input_path()

    def get_default_output_file(self) -> Path:
        """获取默认输出文件路径 - 兼容 main.py"""
        return self.get_default_output_path()


# 提供全局配置实例的便捷访问函数
_config_manager = None


def get_config() -> ConfigManager:
    """
    获取全局配置管理器实例
    
    Returns:
        配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def validate_config() -> bool:
    """
    验证全局配置
    
    Returns:
        配置是否有效
    """
    return get_config().validate()
