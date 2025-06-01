"""
MDX 格式化器模块

将 terminal-to-html 输出的 HTML 片段转换为 Docusaurus 兼容的 MDX 格式。
主要功能是将 HTML 的 class 属性转换为 className，并添加 MDX 容器结构。
"""

import logging
import re
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class MdxFormatterError(Exception):
    """MDX 格式化器相关错误"""
    pass


class MdxFormatter:
    """MDX 格式化器类"""

    def __init__(self):
        """初始化 MDX 格式化器"""
        logger.info("MDX 格式化器初始化完成")

    def _convert_class_to_classname(self, html_content: str) -> str:
        """
        将 HTML 的 class 属性转换为 React/JSX 的 className 属性
        
        Args:
            html_content: HTML 内容字符串
            
        Returns:
            转换后的内容字符串
        """
        # 使用正则表达式替换 class="..." 为 className="..."
        # 注意要处理单引号和双引号的情况
        result = re.sub(r'\bclass=(["\'])', r'className=\1', html_content)
        return result

    def _escape_jsx_braces(self, content: str) -> str:
        """
        转义 MDX/JSX 中的大括号，避免被解释为 JSX 表达式
        在 MDX 中，大括号有特殊含义，需要转义为 HTML 实体
        
        Args:
            content: 包含大括号的内容字符串
            
        Returns:
            转义后的内容字符串
        """
        # 将左大括号转义为 HTML 实体
        content = content.replace('{', '&#123;')
        # 将右大括号转义为 HTML 实体
        content = content.replace('}', '&#125;')
        return content

    def _escape_markdown_characters(self, content: str) -> str:
        """
        转义终端输出中可能与Markdown语法冲突的字符
        终端输出是纯文本，但某些字符在MDX中会被解析为Markdown格式
        
        Args:
            content: 包含终端输出的内容字符串
            
        Returns:
            转义后的内容字符串
        """
        # 转义反斜杠，避免被解析为转义字符
        content = content.replace('\\', '&#92;')
        # 转义反引号，避免被解析为行内代码
        content = content.replace('`', '&#96;')
        # 转义下划线，避免被解析为斜体或粗体
        content = content.replace('_', '&#95;')
        # 转义星号，避免被解析为斜体或粗体  
        content = content.replace('*', '&#42;')
        # 转义方括号，避免被解析为链接
        content = content.replace('[', '&#91;')
        content = content.replace(']', '&#93;')
        return content

    def _clean_terminal_prompts(self, content: str) -> str:
        """
        清理终端提示符和不需要的终端输出
        移除用户名@主机名格式的提示符和独立的提示符行
        
        Args:
            content: 包含终端输出的内容字符串
            
        Returns:
            清理后的内容字符串
        """
        lines = content.split('\n')
        # 存储清理后的终端输出行
        cleaned_lines: List[str] = []

        for line in lines:
            # 使用正则表达式匹配用户名@主机名格式的终端提示符
            prompt_pattern = r'[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+\s+[a-zA-Z0-9_/~-]+\s*%\s*'

            # 如果整行只是提示符（没有命令），则跳过
            if re.match(f'^{prompt_pattern}$', line.strip()):
                continue

            # 如果行包含提示符和命令，提取命令部分
            prompt_with_command = re.match(f'^{prompt_pattern}(.+)$', line.strip())
            if prompt_with_command:
                command = prompt_with_command.group(1).strip()
                cleaned_lines.append(command)
                continue

            # 保留其他行
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _wrap_with_mdx_container(self, content: str, title: Optional[str] = None) -> str:
        """
        为内容添加 MDX 容器结构
        
        Args:
            content: 要包装的内容
            title: 可选的标题
            
        Returns:
            包装后的 MDX 内容，确保文件末尾有换行符
        """
        mdx_parts: List[str] = []

        # 添加标题（如果提供）
        if title:
            mdx_parts.append(f"# {title}\n")

        # 添加 MDX 容器结构，开始标签和内容之间不要换行
        container_start = '<div className="term-container">'
        container_end = '</div>'

        # 确保内容前后没有多余的空白
        clean_content = content.strip()

        # 直接拼接，不在标签和内容之间添加换行符
        mdx_parts.append(container_start + clean_content + container_end)

        # 确保文件末尾有换行符
        result = '\n'.join(mdx_parts)
        if not result.endswith('\n'):
            result += '\n'

        return result

    def convert_html_to_mdx(self, html_content: str, title: Optional[str] = None) -> str:
        """
        将 HTML 片段转换为 MDX 格式
        
        Args:
            html_content: HTML 片段内容
            title: 可选的标题
            
        Returns:
            转换后的 MDX 内容
            
        Raises:
            MdxFormatterError: 转换过程中出现错误
        """
        try:
            # 转换 class 为 className
            mdx_content = self._convert_class_to_classname(html_content)

            # 清理终端提示符
            mdx_content = self._clean_terminal_prompts(mdx_content)

            # 转义终端输出中的Markdown特殊字符
            mdx_content = self._escape_markdown_characters(mdx_content)

            # 转义 MDX 中的大括号
            mdx_content = self._escape_jsx_braces(mdx_content)

            # 添加 MDX 容器结构
            result = self._wrap_with_mdx_container(mdx_content, title)

            logger.info("HTML 到 MDX 转换完成")
            return result

        except Exception as e:
            raise MdxFormatterError(f"HTML 到 MDX 转换失败: {e}") from e

    def convert_html_file_to_mdx(self, html_file_path: str, output_file_path: str,
                                 title: Optional[str] = None) -> bool:
        """
        将 HTML 文件转换为 MDX 文件
        
        Args:
            html_file_path: HTML 文件路径
            output_file_path: 输出 MDX 文件路径
            title: 可选标题
            
        Returns:
            转换是否成功
            
        Raises:
            MdxFormatterError: 转换过程中出现错误
        """
        try:
            html_path = Path(html_file_path)
            output_path = Path(output_file_path)

            # 检查输入文件是否存在
            if not html_path.exists():
                raise MdxFormatterError(f"HTML 文件不存在: {html_path}")

            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 读取 HTML 文件内容
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # 转换为 MDX
            mdx_content = self.convert_html_to_mdx(html_content, title)

            # 写入 MDX 文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(mdx_content)

            logger.info(f"HTML 文件已转换为 MDX: {html_path} -> {output_path}")
            return True

        except Exception as e:
            raise MdxFormatterError(f"HTML 文件到 MDX 转换失败: {e}") from e

    def batch_convert_html_to_mdx(self, input_dir: str, output_dir: str,
                                  file_pattern: str = "*.html") -> Dict[str, bool]:
        """
        批量转换 HTML 文件到 MDX
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            file_pattern: 文件匹配模式
            
        Returns:
            转换结果字典，键为文件名，值为是否成功
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)

        if not input_path.exists():
            raise MdxFormatterError(f"输入目录不存在: {input_path}")

        output_path.mkdir(parents=True, exist_ok=True)

        results: Dict[str, bool] = {}

        # 查找匹配的 HTML 文件
        html_files = list(input_path.glob(file_pattern))

        for html_file in html_files:
            try:
                # 生成对应的 MDX 文件名
                mdx_file_name = html_file.stem + '.mdx'
                mdx_file_path = output_path / mdx_file_name

                # 转换单个文件
                success = self.convert_html_file_to_mdx(
                    str(html_file),
                    str(mdx_file_path),
                    title=html_file.stem
                )
                results[html_file.name] = success

            except Exception as e:
                logger.error(f"转换文件 {html_file} 失败: {e}")
                results[html_file.name] = False

        logger.info(f"批量转换完成，共处理 {len(results)} 个文件")
        return results
