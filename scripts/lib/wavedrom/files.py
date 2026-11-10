#!/usr/bin/env python3
"""
文件发现和路径处理模块
处理 wavedrom 文件的查找和路径操作
"""

import pathlib
from typing import List, Tuple

from scripts.lib.common.utils import find_project_root


def find_wavedrom_files(themes: List[str]) -> List[Tuple[pathlib.Path, List[Tuple[str, pathlib.Path]]]]:
    """查找所有的 wavedrom 文件及其对应的主题输出目录"""
    # 使用 common 工具查找项目根目录
    repo_root_str = find_project_root()
    if not repo_root_str:
        raise FileNotFoundError("无法找到项目根目录")

    repo_root = pathlib.Path(repo_root_str)
    blog_dir = repo_root / "blog"

    if not blog_dir.is_dir():
        raise FileNotFoundError(f"找不到 blog 目录: {blog_dir}")

    wavedrom_files = []

    # 递归查找所有 _assets/wavedrom 目录
    for wavedrom_dir in blog_dir.rglob("_assets/wavedrom"):
        if not wavedrom_dir.is_dir():
            continue

        # 查找该目录下的所有 .edn 文件
        for edn_file in wavedrom_dir.glob("*.edn"):
            # 为每个主题创建对应的输出目录
            theme_dirs = []
            for theme in themes:
                images_theme_dir = wavedrom_dir.parent / "images" / theme
                theme_dirs.append((theme, images_theme_dir))

            wavedrom_files.append((edn_file, theme_dirs))

    return wavedrom_files
