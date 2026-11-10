#!/usr/bin/env python3
"""
文件发现和路径处理模块
处理 litmus 测试文件的查找和路径操作
"""

import pathlib
from typing import List, Tuple

from scripts.lib.common.utils import find_project_root


def find_litmus_files(themes: List[str]) -> List[Tuple[pathlib.Path, List[Tuple[str, pathlib.Path]]]]:
    """查找所有的 litmus 文件及其对应的主题输出目录"""
    # 使用 common 工具查找项目根目录
    repo_root_str = find_project_root()
    if not repo_root_str:
        raise FileNotFoundError("无法找到项目根目录")

    repo_root = pathlib.Path(repo_root_str)
    docs_dir = repo_root / "docs"

    if not docs_dir.is_dir():
        raise FileNotFoundError(f"找不到 docs 目录: {docs_dir}")

    litmus_files = []

    # 递归查找所有 _assets/litmus 目录
    for litmus_dir in docs_dir.rglob("_assets/litmus"):
        if not litmus_dir.is_dir():
            continue

        # 查找该目录下的所有 .litmus 文件
        for litmus_file in litmus_dir.glob("*.litmus"):
            # 为每个主题创建对应的输出目录
            theme_dirs = []
            for theme in themes:
                images_theme_dir = litmus_dir.parent / "images" / theme
                theme_dirs.append((theme, images_theme_dir))

            litmus_files.append((litmus_file, theme_dirs))

    return litmus_files
