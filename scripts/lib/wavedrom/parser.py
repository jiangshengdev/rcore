#!/usr/bin/env python3
"""
EDN 文件解析器
提取 .edn 文件中 .... 标记内的 wavedrom 内容
"""

import re
from pathlib import Path
from typing import Optional


def extract_wavedrom_content(edn_file_path: Path) -> Optional[str]:
    """
    从 EDN 文件中提取 wavedrom 内容
    
    Args:
        edn_file_path: .edn 文件路径
        
    Returns:
        提取的 wavedrom JSON5 内容，如果未找到则返回 None
    """
    try:
        content = edn_file_path.read_text(encoding='utf-8')

        # 使用正则表达式匹配 .... 标记内的内容
        pattern = r'\.{4}\s*\n(.*?)\n\s*\.{4}'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            return match.group(1).strip()

        return None
    except Exception as e:
        print(f"解析文件 {edn_file_path} 时出错: {e}")
        return None
