#!/usr/bin/env python3
"""
ANSI 转换工具 v2 - 最小化版本

通过 terminal-to-html 将 ANSI 文件转换为 MDX 文件。
"""

import subprocess
from pathlib import Path


def main():
    """主函数 - 通过 terminal-to-html 转换 ANSI 为 HTML，然后保存为 MDX"""
    # 固定的输入输出路径
    input_file = Path("_assets/data/input.ansi")
    output_file = Path("_assets/dist/output.mdx")
    
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
    
    # 将 HTML 内容保存为 MDX 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"文件已转换: {input_file} -> {output_file}")


if __name__ == '__main__':
    main()
