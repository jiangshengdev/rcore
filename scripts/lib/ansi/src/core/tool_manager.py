"""
统一工具管理器

管理外部工具（如 terminal-to-html）的生命周期，提供统一的工具调用接口，
避免重复的工具检查和初始化操作。
"""

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from threading import Lock
from typing import Optional, Dict, Any

from ..utils.exceptions import ToolError

logger = logging.getLogger(__name__)


class ToolManager:
    """
    外部工具管理器
    
    统一管理 terminal-to-html 等外部工具，提供工具检查、版本获取、
    调用等功能，避免重复的工具初始化和检查操作。
    """

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

        # 初始化 terminal-to-html 工具
        self._setup_terminal_to_html()

        logger.debug("工具管理器初始化完成")

    def _setup_terminal_to_html(self) -> None:
        """初始化 terminal-to-html 工具配置"""
        try:
            # 查找工具路径
            tool_path = shutil.which("terminal-to-html")
            if not tool_path:
                raise ToolError(
                    "找不到 terminal-to-html 工具。请确保已正确安装并配置路径。\n"
                    "安装方法: npm install -g terminal-to-html"
                )

            # 获取版本信息
            version = self._get_tool_version(tool_path)

            # 存储工具信息
            self._tools['terminal-to-html'] = {
                'path': tool_path,
                'version': version,
                'available': True
            }

            logger.info(f"terminal-to-html 工具已准备就绪: {version}")

        except Exception as e:
            logger.error(f"terminal-to-html 工具初始化失败: {e}")
            self._tools['terminal-to-html'] = {
                'path': None,
                'version': None,
                'available': False,
                'error': str(e)
            }
            raise ToolError(f"terminal-to-html 工具初始化失败: {e}")

    def _get_tool_version(self, tool_path: str) -> str:
        """
        获取工具版本信息
        
        Args:
            tool_path: 工具路径
            
        Returns:
            版本信息字符串
            
        Raises:
            ToolError: 版本获取失败
        """
        try:
            result = subprocess.run(
                [tool_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise ToolError(f"工具版本检查失败: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise ToolError("工具响应超时")
        except FileNotFoundError:
            raise ToolError(f"工具文件不存在: {tool_path}")
        except Exception as e:
            raise ToolError(f"工具版本获取失败: {e}")

    def is_tool_available(self, tool_name: str) -> bool:
        """
        检查工具是否可用
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具是否可用
        """
        return self._tools.get(tool_name, {}).get('available', False)

    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """
        获取工具信息
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具信息字典
        """
        return self._tools.get(tool_name, {})

    def convert_ansi_to_html(self, input_file: str, timeout: int = 30) -> str:
        """
        使用 terminal-to-html 将 ANSI 文件转换为 HTML
        
        Args:
            input_file: 输入 ANSI 文件路径
            timeout: 转换超时时间（秒）
            
        Returns:
            转换后的 HTML 内容
            
        Raises:
            ToolError: 转换失败
        """
        if not self.is_tool_available('terminal-to-html'):
            tool_info = self.get_tool_info('terminal-to-html')
            error_msg = tool_info.get('error', 'terminal-to-html 工具不可用')
            raise ToolError(error_msg)

        tool_path = self._tools['terminal-to-html']['path']

        # 使用临时文件存储输出
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.html', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            logger.info(f"开始转换 ANSI 到 HTML: {input_file} -> {temp_path}")

            # 执行转换命令
            result = subprocess.run(
                [tool_path, input_file],
                stdout=open(temp_path, 'w'),
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                raise ToolError(f"terminal-to-html 执行失败: {result.stderr}")

            # 读取转换结果
            with open(temp_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            logger.info(f"转换完成: 生成 {len(html_content)} 字符的 HTML 内容")
            return html_content

        except subprocess.TimeoutExpired:
            raise ToolError(f"转换超时（{timeout}秒）")
        except Exception as e:
            raise ToolError(f"转换过程中出错: {e}")
        finally:
            # 清理临时文件
            try:
                Path(temp_path).unlink()
            except Exception:
                pass  # 忽略清理错误

    def validate_environment(self) -> bool:
        """
        验证工具环境
        
        检查所有必需工具是否可用。
        
        Returns:
            环境是否有效
        """
        try:
            # 检查 Python
            python_result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if python_result.returncode != 0:
                logger.error("Python3 不可用")
                return False

            # 检查 terminal-to-html
            if not self.is_tool_available('terminal-to-html'):
                logger.error("terminal-to-html 不可用")
                return False

            logger.info("环境验证完成")
            return True

        except Exception as e:
            logger.error(f"环境验证失败: {e}")
            return False


# 全局工具管理器实例
_tool_manager: Optional[ToolManager] = None
_manager_lock = Lock()


def get_tool_manager() -> ToolManager:
    """
    获取全局工具管理器实例
    
    使用单例模式确保工具管理器的唯一性，避免重复初始化。
    
    Returns:
        工具管理器实例
    """
    global _tool_manager
    if _tool_manager is None:
        with _manager_lock:
            if _tool_manager is None:
                _tool_manager = ToolManager()
    return _tool_manager
