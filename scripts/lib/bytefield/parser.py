"""
EDN 文件解析器模块。

此模块负责从包含 AsciiDoc 标记的 EDN 文件中提取纯 bytefield 内容。
"""

import re
from pathlib import Path
from typing import Optional


def extract_bytefield_content(edn_file_path: Path) -> Optional[str]:
    """
    从 EDN 文件中提取 bytefield 内容。
    
    处理逻辑：
    1. 读取文件内容
    2. 查找 [bytefield] 标记
    3. 提取 ---- 分隔符之间的内容
    4. 返回纯 bytefield 内容
    
    EDN 文件格式示例：
        [bytefield]
        ----
        (defattrs :plain [:plain {:font-family "M+ 1p Fallback"}])
        (def row-height 35)
        ...
        ----
    
    参数:
        edn_file_path: EDN 文件路径
        
    返回:
        提取的 bytefield 内容（去除前后空白），如果未找到则返回 None
    """
    try:
        # 读取文件内容
        content = edn_file_path.read_text(encoding='utf-8')

        # 使用正则表达式匹配 [bytefield] 和 ---- 分隔符之间的内容
        # re.DOTALL 标志使 . 匹配包括换行符在内的所有字符
        pattern = r'\[bytefield\]\s*----\s*\n(.*?)\n\s*----'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            # 提取匹配的内容并去除前后空白
            bytefield_content = match.group(1).strip()
            return bytefield_content

        # 未找到匹配的 bytefield 块
        return None

    except Exception as e:
        # 文件读取或解析错误
        return None
