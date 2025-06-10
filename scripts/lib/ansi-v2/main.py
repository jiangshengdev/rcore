#!/usr/bin/env python3
"""
ANSI 转换工具 v2 - 最小化版本

通过 terminal-to-html 将 ANSI 文件转换为 MDX 文件。
"""

import argparse
import re
import subprocess
from pathlib import Path


def convert_class_to_classname(html_content: str) -> str:
    """将 HTML 的 class 属性转换为 React/JSX 的 className 属性"""
    # 使用正则表达式替换 class="..." 为 className="..."
    # 处理双引号和单引号的情况
    return re.sub(r'\bclass=(["\'])', r'className=\1', html_content)


def clean_terminal_prompts(content: str) -> str:
    """清理终端命令提示符，移除 用户名@设备名 目录 % 格式的提示符"""
    # 匹配格式：jiangsheng@M2-Max os % 
    # 正则说明：用户名@设备名 目录名 %
    prompt_pattern = r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9_.-]+\s+[^\s%]*\s+%\s*'

    lines = content.split('\n')
    cleaned_lines: list[str] = []

    for line in lines:
        # 移除行首的命令提示符
        cleaned_line = re.sub(prompt_pattern, '', line)
        cleaned_lines.append(cleaned_line)

    return '\n'.join(cleaned_lines)


def escape_jsx_characters(content: str) -> str:
    """转义 JSX 特殊字符，避免在 MDX 中被误解析"""
    # 首先转义反斜杠，避免影响后续转义处理
    content = content.replace('\\', '&#92;')
    # 转义大括号
    content = content.replace('{', '&#123;').replace('}', '&#125;')
    # 转义下划线，避免被解析为斜体
    content = content.replace('_', '&#95;')
    # 转义方括号，避免被解析为链接
    content = content.replace('[', '&#91;').replace(']', '&#93;')
    # 转义反引号，避免被解析为代码块
    content = content.replace('`', '&#96;')
    # 转义星号，避免被解析为粗体或斜体
    content = content.replace('*', '&#42;')
    return content


def escape_leading_spaces(content: str) -> str:
    """转义行首的空格，避免在 MDX 中被忽略"""
    lines = content.split('\n')
    escaped_lines: list[str] = []

    for line in lines:
        # 检查行首是否有空格
        if line and line[0] == ' ':
            # 将行首的所有空格转义为 &nbsp;
            leading_spaces = len(line) - len(line.lstrip(' '))
            escaped_line = '&nbsp;' * leading_spaces + line[leading_spaces:]
            escaped_lines.append(escaped_line)
        else:
            escaped_lines.append(line)

    return '\n'.join(escaped_lines)


def wrap_with_container(content: str) -> str:
    """为内容添加 MDX 容器结构"""
    return f'<div className="term-container">{content.strip()}</div>'


def main():
    """主函数 - 通过 terminal-to-html 转换 ANSI 为 HTML，然后保存为 MDX"""
    # 获取脚本所在目录，用于智能处理默认路径
    script_dir = Path(__file__).parent
    
    # 命令行参数解析
    parser = argparse.ArgumentParser(description='ANSI 到 MDX 转换器 v2')
    parser.add_argument('input', nargs='?', default='_assets/data/input.ansi',
                        help='输入 ANSI 文件路径 (默认: _assets/data/input.ansi)')
    parser.add_argument('output', nargs='?', default='_assets/dist/output.mdx',
                        help='输出 MDX 文件路径 (默认: _assets/dist/output.mdx)')

    args = parser.parse_args()

    # 智能处理默认路径：如果使用默认值且当前目录找不到文件，则使用脚本目录
    input_file = Path(args.input)
    if args.input == '_assets/data/input.ansi' and not input_file.exists():
        # 使用脚本目录下的默认文件
        input_file = script_dir / '_assets/data/input.ansi'
    
    output_file = Path(args.output)
    if args.output == '_assets/dist/output.mdx' and not output_file.parent.exists():
        # 使用脚本目录下的默认输出路径
        output_file = script_dir / '_assets/dist/output.mdx'

    # 确保输出目录存在
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 读取 ANSI 输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        ansi_content = f.read()

    # 通过 terminal-to-html 转换为 HTML
    process = subprocess.run(
        ['terminal-to-html'],
        input=ansi_content,
        capture_output=True,
        text=True
    )

    if process.returncode != 0:
        print(f"转换失败: {process.stderr}")
        return

    html_content = process.stdout

    # 清理命令提示符
    html_content = clean_terminal_prompts(html_content)

    # 转换 class 为 className
    mdx_content = convert_class_to_classname(html_content)

    # 转义 JSX 特殊字符
    mdx_content = escape_jsx_characters(mdx_content)

    # 转义行首空格
    mdx_content = escape_leading_spaces(mdx_content)

    # 包装在容器中
    mdx_content = wrap_with_container(mdx_content)

    # 确保内容末尾有换行符
    if not mdx_content.endswith('\n'):
        mdx_content += '\n'

    # 将 MDX 内容保存为文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(mdx_content)

    print(f"文件已转换: {input_file} -> {output_file}")


if __name__ == '__main__':
    main()
