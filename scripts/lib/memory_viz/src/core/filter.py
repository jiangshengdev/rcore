"""
内存地址过滤器模块
提供地址列表过滤功能，去除全为空值的行
"""
import math
from typing import List, Dict, Optional


def filter_zero_rows(addresses: List[str], memory: Dict[str, str], columns: int,
                     null_vals: Optional[List[str]] = None) -> List[str]:
    """
    过滤掉矩阵布局中全为空值的行
    
    Args:
        addresses: 原始地址列表
        memory: 地址到值的映射
        columns: 矩阵列数
        null_vals: 被视为空值的值列表，默认为 ["0x0000000000000000", "0x0"]
    
    Returns:
        过滤后的地址列表
    """
    if null_vals is None:
        null_vals = ["0x0000000000000000", "0x0"]

    if not addresses:
        return []

    # 计算矩阵行数
    rows = math.ceil(len(addresses) / columns)

    # 生成初始矩阵
    initial_matrix = [
        addresses[r * columns: min((r + 1) * columns, len(addresses))]
        for r in range(rows)
    ]

    # 过滤掉所有值都为空的行（但保留包含原始索引0的行）
    filtered_addrs: List[str] = []
    for row in initial_matrix:
        # 检查当前行是否包含原始索引为0的地址
        contains_index_zero = any(
            addresses.index(addr) == 0
            for addr in row if addr in addresses
        )

        # 检查这一行是否所有地址的值都为空
        is_all_zero = all(
            memory.get(addr, "0x0") in null_vals
            for addr in row
        )

        # 如果不是全空行，或者包含原始索引0的地址，则保留该行
        if not is_all_zero or contains_index_zero:
            filtered_addrs.extend(row)

    return filtered_addrs
