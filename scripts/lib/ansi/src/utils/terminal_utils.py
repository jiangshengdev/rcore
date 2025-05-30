"""
终端工具模块

提供 terminal-to-html 工具的封装和调用功能。
处理终端命令执行、进程管理和输出处理。
"""

import logging
import os
import pathlib
import shutil
import subprocess
import tempfile
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)


class TerminalToHtmlError(Exception):
    """terminal-to-html 工具相关错误"""
    pass


class TerminalUtils:
    """终端工具类"""

    def __init__(self, terminal_to_html_path: Optional[str] = None):
        """
        初始化终端工具
        
        Args:
            terminal_to_html_path: terminal-to-html 工具路径，为None时自动查找
        """
        self.tool_path = self._find_terminal_to_html_path(terminal_to_html_path)
        self._validate_tool()

        logger.info(f"终端工具初始化完成: {self.tool_path}")

    def _find_terminal_to_html_path(self, provided_path: Optional[str] = None) -> str:
        """
        获取 terminal-to-html 工具路径
        
        Args:
            provided_path: 用户提供的路径
            
        Returns:
            工具的绝对路径
            
        Raises:
            TerminalToHtmlError: 找不到工具
        """
        # 如果用户提供了路径，优先使用
        if provided_path:
            path = pathlib.Path(provided_path)
            if path.exists() and path.is_file():
                return str(path.absolute())
            else:
                raise TerminalToHtmlError(f"指定的 terminal-to-html 路径不存在: {provided_path}")

        # 直接从 PATH 环境变量获取
        tool_in_path = shutil.which("terminal-to-html")
        if tool_in_path:
            logger.debug(f"在 PATH 中找到 terminal-to-html: {tool_in_path}")
            return tool_in_path

        raise TerminalToHtmlError(
            "找不到 terminal-to-html 工具。请确保已正确安装并配置路径。\n"
            "安装方法: npm install -g terminal-to-html"
        )

    def _validate_tool(self) -> None:
        """
        验证 terminal-to-html 工具是否可用
        
        Raises:
            TerminalToHtmlError: 工具不可用
        """
        try:
            result = subprocess.run(
                [self.tool_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"terminal-to-html 版本: {version}")
            else:
                raise TerminalToHtmlError(f"工具版本检查失败: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise TerminalToHtmlError("工具响应超时")
        except FileNotFoundError:
            raise TerminalToHtmlError(f"工具文件不存在: {self.tool_path}")
        except Exception as e:
            raise TerminalToHtmlError(f"工具验证失败: {e}")

    def get_version(self) -> str:
        """
        获取 terminal-to-html 版本信息
        
        Returns:
            版本字符串
        """
        try:
            result = subprocess.run(
                [self.tool_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise TerminalToHtmlError(f"获取版本失败: {result.stderr}")

        except Exception as e:
            raise TerminalToHtmlError(f"版本查询失败: {e}")

    def convert_ansi_to_html(self,
                             input_path: Union[str, pathlib.Path],
                             output_path: Optional[Union[str, pathlib.Path]] = None,
                             options: Optional[Dict[str, Any]] = None) -> str:
        """
        将 ANSI 文件转换为 HTML
        
        Args:
            input_path: 输入的 ANSI 文件路径
            output_path: 输出的 HTML 文件路径，为None时使用临时文件
            options: 转换选项配置
            
        Returns:
            转换后的 HTML 内容
            
        Raises:
            TerminalToHtmlError: 转换失败
        """
        input_file = pathlib.Path(input_path)

        if not input_file.exists():
            raise TerminalToHtmlError(f"输入文件不存在: {input_file}")

        # 设置默认选项
        default_options: Dict[str, Any] = {
            "preview": False,  # 不生成预览页面，只输出纯 HTML 内容
            "buffer_max_lines": 0,  # 解除行数限制，处理大型 ANSI 文件
        }

        if options:
            default_options.update(options)

        # 构建命令参数
        cmd = [self.tool_path]

        # 添加选项参数
        if default_options.get("preview"):
            cmd.append("--preview")

        # 添加行数限制参数
        buffer_max_lines = default_options.get("buffer_max_lines", 0)
        if buffer_max_lines is not None:
            cmd.extend(["--buffer-max-lines", str(buffer_max_lines)])

        # 输出处理
        use_temp_file = output_path is None
        if use_temp_file:
            # 使用临时文件
            temp_fd, temp_path = tempfile.mkstemp(suffix='.html')
            os.close(temp_fd)  # 关闭文件描述符，但保留文件
            output_file = pathlib.Path(temp_path)
        else:
            output_file = pathlib.Path(output_path)
            # 确保输出目录存在
            output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"开始转换 ANSI 到 HTML: {input_file} -> {output_file}")
            logger.debug(f"转换命令: {' '.join(cmd)}")

            # 读取输入文件内容
            with open(input_file, 'r', encoding='utf-8') as f:
                ansi_content = f.read()

            # 执行转换 (使用 stdin/stdout 方式)
            result = subprocess.run(
                cmd,
                input=ansi_content,
                capture_output=True,
                text=True,
                timeout=60,  # 60秒超时
            )

            if result.returncode != 0:
                error_msg = f"转换失败 (退出码: {result.returncode})\n"
                if result.stderr:
                    error_msg += f"错误信息: {result.stderr}\n"
                if result.stdout:
                    error_msg += f"输出信息: {result.stdout}"
                raise TerminalToHtmlError(error_msg)

            # 获取转换后的 HTML 内容
            html_content = result.stdout

            if not html_content:
                raise TerminalToHtmlError("转换后的 HTML 内容为空")

            # 如果需要保存到文件
            if not use_temp_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)

            logger.info(f"转换完成: 生成 {len(html_content)} 字符的 HTML 内容")

            return html_content

        except subprocess.TimeoutExpired:
            raise TerminalToHtmlError("转换超时（60秒）")
        except Exception as e:
            # 清理临时文件
            if use_temp_file and output_file.exists():
                try:
                    output_file.unlink()
                except:
                    pass
            raise TerminalToHtmlError(f"转换过程中发生错误: {e}")

    def test_conversion(self) -> bool:
        """
        测试转换功能是否正常工作
        
        Returns:
            测试是否通过
        """
        try:
            # 创建简单的测试 ANSI 内容
            test_ansi = "\033[31mRed Text\033[0m \033[32mGreen Text\033[0m"

            # 创建临时测试文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ansi', delete=False) as f:
                f.write(test_ansi)
                test_file = f.name

            try:
                # 执行转换测试
                html_content = self.convert_ansi_to_html(test_file)

                # 检查转换结果
                success = bool(
                    html_content and
                    len(html_content) > 0 and
                    "<html>" in html_content.lower()
                )

                if success:
                    logger.info("转换功能测试通过")
                else:
                    logger.error(f"转换功能测试失败: HTML 内容无效")

                return success

            finally:
                # 清理测试文件
                try:
                    os.unlink(test_file)
                except:
                    pass

        except Exception as e:
            logger.error(f"转换功能测试失败: {e}")
            return False


# 便捷函数和全局实例
_default_terminal_utils = None


def get_terminal_utils(tool_path: Optional[str] = None) -> TerminalUtils:
    """
    获取终端工具实例（单例模式）
    
    Args:
        tool_path: terminal-to-html 工具路径
        
    Returns:
        TerminalUtils 实例
    """
    global _default_terminal_utils

    if _default_terminal_utils is None or tool_path is not None:
        _default_terminal_utils = TerminalUtils(tool_path)

    return _default_terminal_utils


def convert_ansi_to_html(input_path: Union[str, pathlib.Path],
                         output_path: Optional[Union[str, pathlib.Path]] = None,
                         options: Optional[Dict[str, Any]] = None) -> str:
    """
    转换 ANSI 到 HTML 的便捷函数
    
    Args:
        input_path: 输入的 ANSI 文件路径
        output_path: 输出的 HTML 文件路径
        options: 转换选项
        
    Returns:
        转换后的 HTML 内容
    """
    terminal_utils = get_terminal_utils()
    return terminal_utils.convert_ansi_to_html(input_path, output_path, options)


def test_terminal_tool() -> bool:
    """
    测试终端工具是否可用的便捷函数
    
    Returns:
        测试是否通过
    """
    try:
        terminal_utils = get_terminal_utils()
        return terminal_utils.test_conversion()
    except Exception as e:
        logger.error(f"终端工具测试失败: {e}")
        return False
