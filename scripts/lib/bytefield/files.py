"""
文件发现和路径处理模块。

此模块负责查找项目中的 bytefield EDN 文件，
并生成对应的输出路径映射。
"""

from pathlib import Path
from typing import List, Tuple

# 导入通用工具函数
from scripts.lib.common.utils import find_project_root


def find_bytefield_files(themes: List[str]) -> List[Tuple[Path, List[Tuple[str, Path]]]]:
    """
    查找所有的 bytefield 文件及其对应的主题输出目录。
    
    扫描逻辑：
    1. 从项目根目录开始
    2. 递归查找 blog/*/_assets/bytefield/ 目录
    3. 查找目录下的所有 *.edn 文件
    4. 为每个文件生成对应的输出路径
    
    路径映射示例：
        输入：blog/2025-10-06-riscv-privileged/_assets/bytefield/mtvec.edn
        输出（light）：blog/2025-10-06-riscv-privileged/_assets/images/light/mtvec.svg
        输出（dark）：blog/2025-10-06-riscv-privileged/_assets/images/dark/mtvec.svg
    
    参数:
        themes: 要生成的主题列表，例如 ['light', 'dark']
        
    返回:
        列表，每个元素是一个元组：(edn_file_path, [(theme, output_path), ...])
        其中 edn_file_path 是 EDN 文件的 Path 对象
        output_path 是对应主题的输出 SVG 文件 Path 对象
    """
    # 查找项目根目录
    project_root_str = find_project_root()
    if not project_root_str:
        return []

    project_root = Path(project_root_str)

    # 查找所有 blog 目录
    blog_dir = project_root / "blog"
    if not blog_dir.exists():
        return []

    result = []

    # 递归查找所有 _assets/bytefield/ 目录下的 .edn 文件
    for bytefield_dir in blog_dir.glob("*/_assets/bytefield"):
        if not bytefield_dir.is_dir():
            continue

        # 查找该目录下的所有 .edn 文件
        for edn_file in bytefield_dir.glob("*.edn"):
            # 获取文件所在的博客文章目录
            # 例如：blog/2025-10-06-riscv-privileged/_assets/bytefield/mtvec.edn
            # 博客目录：blog/2025-10-06-riscv-privileged
            blog_post_dir = edn_file.parent.parent.parent

            # 生成每个主题的输出路径
            theme_outputs = []
            for theme in themes:
                # 输出目录：blog/2025-10-06-riscv-privileged/_assets/images/{theme}/
                output_dir = blog_post_dir / "_assets" / "images" / theme

                # 输出文件：blog/2025-10-06-riscv-privileged/_assets/images/{theme}/mtvec.svg
                output_file = output_dir / f"{edn_file.stem}.svg"

                theme_outputs.append((theme, output_file))

            result.append((edn_file, theme_outputs))

    return result
