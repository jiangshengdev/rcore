#!/usr/bin/env python3
"""
配置管理模块

统一管理 ANSI 转换器的所有配置项，包括默认路径、工具设置、格式选项等。
将之前分散在 Shell 脚本中的配置统一到 Python 中管理。
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConversionSettings:
    """转换相关设置"""
    # 默认文件路径
    default_input_file: str = "data/input.ansi"
    default_output_file: str = "output/_output.pre.mdx"
    
    # 文件处理选项
    supported_input_extensions: List[str] = None
    output_extension: str = ".mdx"
    max_file_size_mb: int = 50
    
    # 转换选项
    auto_detect_ansi: bool = True
    fallback_to_raw_content: bool = True
    create_output_dirs: bool = True
    
    def __post_init__(self):
        if self.supported_input_extensions is None:
            self.supported_input_extensions = ['.ansi', '.txt', '.html', '.htm']


@dataclass 
class ToolSettings:
    """工具相关设置"""
    # 必需工具列表
    required_tools: List[str] = None
    
    # terminal-to-html 设置
    terminal_to_html_timeout: int = 30
    terminal_to_html_args: List[str] = None
    
    # Python 路径设置
    auto_setup_python_path: bool = True
    
    def __post_init__(self):
        if self.required_tools is None:
            self.required_tools = ["python3", "terminal-to-html"]
        
        if self.terminal_to_html_args is None:
            self.terminal_to_html_args = []


@dataclass
class LoggingSettings:
    """日志相关设置"""
    # 日志级别
    default_level: str = "INFO"
    verbose_level: str = "DEBUG"
    
    # 日志格式
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    simple_format: str = "%(levelname)s: %(message)s"
    
    # 输出设置
    use_colored_output: bool = True
    show_progress: bool = True


@dataclass
class PathSettings:
    """路径相关设置"""
    # 项目结构
    project_root: Optional[Path] = None
    ansi_module_dir: Optional[Path] = None
    scripts_dir: Optional[Path] = None
    
    # 相对路径（相对于 ansi_module_dir）
    data_dir: str = "data"
    output_dir: str = "output"
    src_dir: str = "src"
    bin_dir: str = "bin"
    
    def __post_init__(self):
        if self.project_root is None:
            # 自动检测项目根目录
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / "package.json").exists():
                    self.project_root = parent
                    break
            else:
                # fallback: 使用相对路径推测
                self.project_root = Path(__file__).parent.parent.parent.parent.parent
        
        if self.ansi_module_dir is None:
            self.ansi_module_dir = self.project_root / "scripts" / "lib" / "ansi"
        
        if self.scripts_dir is None:
            self.scripts_dir = self.project_root / "scripts"


class AnsiConfig:
    """ANSI 转换器主配置类"""
    
    def __init__(self, config_file: Optional[str] = None):
        # 基础设置
        self.conversion = ConversionSettings()
        self.tools = ToolSettings()
        self.logging = LoggingSettings()
        self.paths = PathSettings()
        
        # 从环境变量加载配置
        self._load_from_environment()
        
        # 从配置文件加载（如果提供）
        if config_file:
            self._load_from_file(config_file)
    
    def _load_from_environment(self):
        """从环境变量加载配置"""
        # 路径相关环境变量
        if 'ANSI_PROJECT_ROOT' in os.environ:
            self.paths.project_root = Path(os.environ['ANSI_PROJECT_ROOT'])
        
        if 'ANSI_MODULE_DIR' in os.environ:
            self.paths.ansi_module_dir = Path(os.environ['ANSI_MODULE_DIR'])
        
        # 转换相关环境变量
        if 'ANSI_DEFAULT_INPUT' in os.environ:
            self.conversion.default_input_file = os.environ['ANSI_DEFAULT_INPUT']
        
        if 'ANSI_DEFAULT_OUTPUT' in os.environ:
            self.conversion.default_output_file = os.environ['ANSI_DEFAULT_OUTPUT']
        
        # 工具相关环境变量
        if 'ANSI_TIMEOUT' in os.environ:
            try:
                self.tools.terminal_to_html_timeout = int(os.environ['ANSI_TIMEOUT'])
            except ValueError:
                logger.warning(f"无效的超时值: {os.environ['ANSI_TIMEOUT']}")
        
        # 日志相关环境变量
        if 'ANSI_LOG_LEVEL' in os.environ:
            self.logging.default_level = os.environ['ANSI_LOG_LEVEL'].upper()
        
        if 'ANSI_VERBOSE' in os.environ:
            # 支持 true/false/1/0 格式
            verbose_env = os.environ['ANSI_VERBOSE'].lower()
            if verbose_env in ('true', '1', 'yes', 'on'):
                self.logging.default_level = self.logging.verbose_level
    
    def _load_from_file(self, config_file: str):
        """从配置文件加载设置（预留接口）"""
        # TODO: 支持 JSON/YAML 配置文件
        logger.info(f"配置文件支持尚未实现: {config_file}")
    
    def get_absolute_input_path(self, relative_path: str) -> Path:
        """将相对路径转换为绝对路径（相对于 ansi_module_dir）"""
        if Path(relative_path).is_absolute():
            return Path(relative_path)
        return self.paths.ansi_module_dir / relative_path
    
    def get_absolute_output_path(self, relative_path: str) -> Path:
        """将输出路径转换为绝对路径"""
        if Path(relative_path).is_absolute():
            return Path(relative_path)
        return self.paths.ansi_module_dir / relative_path
    
    def get_default_input_file(self) -> Path:
        """获取默认输入文件的绝对路径"""
        return self.get_absolute_input_path(self.conversion.default_input_file)
    
    def get_default_output_file(self) -> Path:
        """获取默认输出文件的绝对路径"""
        return self.get_absolute_output_path(self.conversion.default_output_file)
    
    def setup_python_path(self):
        """设置 Python 路径"""
        if not self.tools.auto_setup_python_path:
            return
        
        import sys
        
        paths_to_add = [
            str(self.paths.project_root),
            str(self.paths.scripts_dir)
        ]
        
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
                logger.debug(f"添加到 Python 路径: {path}")
    
    def validate_configuration(self) -> List[str]:
        """验证配置的有效性
        
        Returns:
            List[str]: 配置问题列表（空列表表示无问题）
        """
        issues = []
        
        # 检查关键路径是否存在
        if not self.paths.project_root.exists():
            issues.append(f"项目根目录不存在: {self.paths.project_root}")
        
        if not self.paths.ansi_module_dir.exists():
            issues.append(f"ANSI 模块目录不存在: {self.paths.ansi_module_dir}")
        
        # 检查默认输入文件
        default_input = self.get_default_input_file()
        if not default_input.exists():
            issues.append(f"默认输入文件不存在: {default_input}")
        
        # 检查输出目录是否可创建
        default_output = self.get_default_output_file()
        output_dir = default_output.parent
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            issues.append(f"无法创建输出目录 {output_dir}: {e}")
        
        # 检查日志级别
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.default_level not in valid_levels:
            issues.append(f"无效的日志级别: {self.logging.default_level}")
        
        return issues
    
    def __str__(self) -> str:
        """配置信息的字符串表示"""
        return f"""AnsiConfig:
  项目根目录: {self.paths.project_root}
  ANSI 模块目录: {self.paths.ansi_module_dir}
  默认输入文件: {self.get_default_input_file()}
  默认输出文件: {self.get_default_output_file()}
  日志级别: {self.logging.default_level}
  支持的扩展名: {self.conversion.supported_input_extensions}
  必需工具: {self.tools.required_tools}
"""


# 全局配置实例
_global_config: Optional[AnsiConfig] = None


def get_config() -> AnsiConfig:
    """获取全局配置实例（单例模式）"""
    global _global_config
    if _global_config is None:
        _global_config = AnsiConfig()
    return _global_config


def reload_config(config_file: Optional[str] = None) -> AnsiConfig:
    """重新加载配置"""
    global _global_config
    _global_config = AnsiConfig(config_file)
    return _global_config


def validate_config() -> bool:
    """验证当前配置是否有效"""
    config = get_config()
    issues = config.validate_configuration()
    
    if issues:
        logger.error("配置验证失败:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    
    logger.info("✅ 配置验证通过")
    return True
