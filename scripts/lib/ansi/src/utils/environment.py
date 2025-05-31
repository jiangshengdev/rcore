#!/usr/bin/env python3
"""
环境验证工具模块

提供系统环境检查、依赖验证、路径处理等功能。
这些功能将 Shell 脚本中的环境检查逻辑集中到 Python 中处理。
"""

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class EnvironmentError(Exception):
    """环境相关错误的基类"""
    pass


class EnvironmentValidator:
    """环境验证器 - 集中处理所有环境相关检查"""

    def __init__(self):
        self.project_root = self._find_project_root()
        self.ansi_module_dir = self.project_root / "scripts" / "lib" / "ansi"

    def _find_project_root(self) -> Path:
        """查找项目根目录（包含 package.json 的目录）"""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "package.json").exists():
                return parent
        # 如果找不到，使用当前路径的4级父目录作为fallback
        return Path(__file__).parent.parent.parent.parent.parent

    def check_required_tools(self) -> List[str]:
        """检查所需的系统工具是否可用"""
        required_tools = ["python3", "terminal-to-html"]
        missing_tools = []

        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)
                logger.error(f"必需工具未找到: {tool}")
            else:
                logger.debug(f"工具检查通过: {tool}")

        return missing_tools

    def check_terminal_to_html_version(self) -> Optional[str]:
        """检查 terminal-to-html 工具版本"""
        try:
            result = subprocess.run(
                ["terminal-to-html", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_info = result.stdout.strip()
                logger.info(f"terminal-to-html 版本: {version_info}")
                return version_info
            else:
                logger.warning("无法获取 terminal-to-html 版本信息")
                return None
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"检查 terminal-to-html 版本失败: {e}")
            return None

    def validate_input_file(self, file_path: str) -> Tuple[bool, str]:
        """验证输入文件
        
        Args:
            file_path: 输入文件路径
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息或警告)
        """
        path = Path(file_path)

        # 基本存在性检查
        if not path.exists():
            return False, f"文件不存在: {file_path}"

        if not path.is_file():
            return False, f"路径不是文件: {file_path}"

        # 可读性检查
        if not os.access(path, os.R_OK):
            return False, f"文件不可读: {file_path}"

        # 文件大小检查（避免处理过大文件）
        file_size = path.stat().st_size
        if file_size > 50 * 1024 * 1024:  # 50MB
            return False, f"文件过大 ({file_size // 1024 // 1024}MB): {file_path}"

        # 文件扩展名检查
        valid_extensions = {'.ansi', '.txt', '.html', '.htm'}
        if path.suffix.lower() not in valid_extensions:
            logger.warning(f"文件扩展名不在推荐列表中: {path.suffix}")

        # ANSI 序列检查（仅对可能的 ANSI 文件）
        if path.suffix.lower() in {'.ansi', '.txt'} or 'ansi' in path.name.lower():
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    # 只读取前 1MB 来检查 ANSI 序列
                    content = f.read(1024 * 1024)
                    if '\033[' not in content:
                        logger.warning(f"文件可能不包含 ANSI 转义序列: {file_path}")
            except Exception as e:
                logger.warning(f"无法检查文件内容: {e}")

        return True, "文件验证通过"

    def validate_output_path(self, file_path: str) -> Tuple[bool, str]:
        """验证输出文件路径
        
        Args:
            file_path: 输出文件路径
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        path = Path(file_path)

        # 检查输出目录
        output_dir = path.parent

        # 如果目录不存在，尝试创建
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建输出目录: {output_dir}")
            except OSError as e:
                return False, f"无法创建输出目录 {output_dir}: {e}"

        # 检查目录可写性
        if not os.access(output_dir, os.W_OK):
            return False, f"输出目录不可写: {output_dir}"

        # 检查输出文件扩展名
        if path.suffix.lower() != '.mdx':
            logger.warning(f"输出文件扩展名不是 .mdx: {path.suffix}")

        # 如果文件已存在，检查是否可覆写
        if path.exists():
            if not os.access(path, os.W_OK):
                return False, f"输出文件存在但不可写: {file_path}"
            logger.warning(f"输出文件已存在，将被覆盖: {file_path}")

        return True, "输出路径验证通过"

    def ensure_python_path(self) -> None:
        """确保 Python 路径正确设置"""
        project_root_str = str(self.project_root)
        scripts_path_str = str(self.project_root / "scripts")

        if project_root_str not in sys.path:
            sys.path.insert(0, project_root_str)
            logger.debug(f"添加项目根目录到 Python 路径: {project_root_str}")

        if scripts_path_str not in sys.path:
            sys.path.insert(0, scripts_path_str)
            logger.debug(f"添加 scripts 目录到 Python 路径: {scripts_path_str}")

    def get_default_paths(self) -> Tuple[Path, Path]:
        """获取默认的输入和输出文件路径"""
        default_input = self.ansi_module_dir / "data" / "input.ansi"
        default_output = self.ansi_module_dir / "output" / "_output.pre.mdx"
        return default_input, default_output

    def validate_environment(self) -> bool:
        """执行完整的环境验证
        
        Returns:
            bool: 环境是否有效
        """
        logger.info("开始环境验证...")

        # 检查必需工具
        missing_tools = self.check_required_tools()
        if missing_tools:
            logger.error(f"缺少必需工具: {', '.join(missing_tools)}")
            return False

        # 检查 terminal-to-html 版本
        version = self.check_terminal_to_html_version()
        if not version:
            logger.warning("无法验证 terminal-to-html 版本，但工具存在")

        # 确保 Python 路径正确
        self.ensure_python_path()

        # 检查模块目录结构
        required_dirs = [
            self.ansi_module_dir / "src",
            self.ansi_module_dir / "data",
            self.ansi_module_dir / "output"
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"创建必需目录: {dir_path}")
                except OSError as e:
                    logger.error(f"无法创建目录 {dir_path}: {e}")
                    return False

        logger.info("✅ 环境验证完成")
        return True


def check_environment() -> bool:
    """便捷函数：检查环境是否满足要求"""
    validator = EnvironmentValidator()
    return validator.validate_environment()


def validate_files(input_file: str, output_file: str) -> Tuple[bool, List[str]]:
    """便捷函数：验证输入和输出文件
    
    Returns:
        Tuple[bool, List[str]]: (是否全部有效, 错误信息列表)
    """
    validator = EnvironmentValidator()
    errors = []

    # 验证输入文件
    input_valid, input_msg = validator.validate_input_file(input_file)
    if not input_valid:
        errors.append(f"输入文件错误: {input_msg}")

    # 验证输出路径
    output_valid, output_msg = validator.validate_output_path(output_file)
    if not output_valid:
        errors.append(f"输出路径错误: {output_msg}")

    return len(errors) == 0, errors
