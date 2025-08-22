#!/usr/bin/env python3
"""
Herd7 工具调用模块
封装 herd7 工具的运行和配置逻辑
"""

import pathlib
import subprocess
import sys
import tempfile

from scripts.lib.common.utils import ensure_dir
from .herd_config import build_herd_args


def eprint(*args, **kwargs):
    """输出到标准错误流"""
    print(*args, file=sys.stderr, **kwargs)


def run_herd(lit: pathlib.Path, theme: str = "light", output_dir: pathlib.Path = None) -> pathlib.Path:
    """运行 herd7 生成指定主题的 DOT 文件"""
    # 如果指定了输出目录，使用它，否则使用临时目录
    if output_dir:
        ensure_dir(str(output_dir))
        dot_path = output_dir / f"{lit.stem}.dot"  # 去掉主题后缀，因为已经在主题目录中
        work_dir = output_dir
    else:
        # 在临时目录生成 DOT 文件
        work_dir = pathlib.Path(tempfile.mkdtemp())
        dot_path = work_dir / (lit.stem + ".dot")

    # 使用新的配置生成器构建参数
    herd_args = build_herd_args(lit, theme, work_dir)

    eprint(f"[INFO] 处理 {lit.name} ({theme} 主题)")
    try:
        subprocess.run(herd_args, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        eprint(f"[WARN] herd7 执行失败 {lit.name} ({theme}): {e}")
        return None

    # herd7 总是生成以原始文件名命名的 DOT 文件
    original_dot = work_dir / (lit.stem + ".dot")
    if not original_dot.is_file():
        eprint(f"[WARN] herd7 未生成 DOT 文件: {original_dot}")
        return None

    # 如果需要重命名（包含主题信息），则重命名
    if output_dir and dot_path != original_dot:
        original_dot.rename(dot_path)
        return dot_path
    else:
        return original_dot
