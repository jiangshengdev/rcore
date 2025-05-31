"""
通用工具函数模块

提供在多个模块中使用的通用功能，避免代码重复。
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Tuple, List


def setup_logging(verbose: bool = False, use_config: bool = True) -> None:
    """
    统一的日志配置函数
    
    Args:
        verbose: 是否启用详细日志输出
        use_config: 是否使用配置管理器中的配置
    """
    if use_config:
        try:
            from ..core.config_manager import get_config
            config = get_config()
            # 根据 verbose 参数选择日志级别
            level_name = config.logging.verbose_level if verbose else config.logging.default_level
            format_str = config.logging.log_format
        except ImportError:
            # 如果配置管理器不可用，使用默认配置
            level_name = "DEBUG" if verbose else "INFO"
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        # 不使用配置管理器时的默认配置
        level_name = "DEBUG" if verbose else "INFO"
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 设置日志级别
    level = getattr(logging, level_name, logging.INFO)

    # 配置基础日志
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True  # 强制重新配置，覆盖之前的设置
    )


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """
    查找项目根目录
    
    从指定路径开始向上查找包含 package.json 的目录。
    
    Args:
        start_path: 开始查找的路径，为 None 时使用当前文件路径
        
    Returns:
        项目根目录路径
        
    Raises:
        FileNotFoundError: 找不到项目根目录
    """
    current = start_path or Path(__file__).resolve()

    # 向上遍历父目录查找 package.json
    for parent in current.parents:
        if (parent / "package.json").exists():
            return parent

    # 如果找不到，返回推测的根目录
    fallback = Path(__file__).parent.parent.parent.parent.parent
    if fallback.exists():
        return fallback

    raise FileNotFoundError("无法找到项目根目录（包含 package.json 的目录）")


def validate_file_paths(input_file: str, output_file: str) -> Tuple[bool, List[str]]:
    """
    验证输入和输出文件路径
    
    统一文件路径验证逻辑，检查输入文件是否存在、输出目录是否可创建等。
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
        
    Returns:
        (是否验证通过, 错误信息列表)
    """
    errors: List[str] = []

    # 检查输入文件
    input_path = Path(input_file)
    if not input_path.exists():
        errors.append(f"输入文件不存在: {input_file}")
    elif not input_path.is_file():
        errors.append(f"输入路径不是文件: {input_file}")
    elif not input_path.stat().st_size > 0:
        errors.append(f"输入文件为空: {input_file}")

    # 检查输出路径
    output_path = Path(output_file)
    try:
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        errors.append(f"无法创建输出目录: {e}")

    # 检查是否有写入权限
    if output_path.exists() and not output_path.is_file():
        errors.append(f"输出路径不是文件: {output_file}")

    return len(errors) == 0, errors


# 为了兼容 main.py，提供别名
def validate_files(input_file: str, output_file: str) -> Tuple[bool, List[str]]:
    """validate_file_paths 的别名，保持向后兼容"""
    return validate_file_paths(input_file, output_file)


def is_ansi_content(content: str) -> bool:
    """
    检测内容是否包含 ANSI 转义序列
    
    Args:
        content: 待检测的文本内容
        
    Returns:
        是否包含 ANSI 转义序列
    """
    return '\033[' in content or '\x1b[' in content


def normalize_path(path: str, base_path: Optional[Path] = None) -> Path:
    """
    规范化路径处理
    
    将相对路径转换为绝对路径，统一路径处理逻辑。
    
    Args:
        path: 待处理的路径字符串
        base_path: 基础路径，为 None 时使用当前工作目录
        
    Returns:
        规范化后的绝对路径
    """
    path_obj = Path(path)

    if path_obj.is_absolute():
        return path_obj

    base = base_path or Path.cwd()
    return (base / path_obj).resolve()


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        人类可读的文件大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} 字节"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
