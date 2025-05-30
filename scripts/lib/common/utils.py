"""
通用工具函数模块

提供各种共享的实用函数。
"""

import os
from typing import Optional, Tuple


def find_project_root(marker_files: Tuple[str, ...] = ("docusaurus.config.ts", "package.json")) -> Optional[str]:
    """
    自动寻找项目根目录
    
    Args:
        marker_files: 用于识别项目根目录的标记文件
        
    Returns:
        项目根目录的绝对路径，如果未找到则返回 None
    """
    current_dir = os.getcwd()

    while current_dir != "/":
        for marker in marker_files:
            if os.path.isfile(os.path.join(current_dir, marker)):
                return current_dir
        current_dir = os.path.dirname(current_dir)

    return None


def ensure_dir(path: str) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
    """
    os.makedirs(path, exist_ok=True)


def ensure_parent_dir(file_path: str) -> None:
    """
    为文件创建父目录
    
    Args:
        file_path: 文件路径
    """
    parent_dir = os.path.dirname(file_path)
    if parent_dir:
        ensure_dir(parent_dir)


def get_script_dir() -> str:
    """
    获取当前脚本所在目录
    
    Returns:
        脚本目录的绝对路径
    """
    return os.path.dirname(os.path.abspath(__file__))


def get_file_dir(file_path: str) -> str:
    """
    获取指定文件所在目录
    
    Args:
        file_path: 文件路径 (通常是 __file__)
        
    Returns:
        文件目录的绝对路径
    """
    return os.path.dirname(os.path.abspath(file_path))
