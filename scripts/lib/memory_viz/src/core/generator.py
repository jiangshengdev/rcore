"""
内存 DOT 生成器模块
封装 GDB 输出解析与 Graphviz DOT 生成功能
"""
import math
from typing import List, Dict, Optional

from .colors import get_theme_colors
from .config import (
    FONT, FONT_SIZE, CELL_PADDING, NODE_MARGIN,
    NULL_VAL, DISPLAY_NULL_VAL, PADDED_NULL_DISPLAY, PTE_PPN_SHIFT,
    DEFAULT_THEME, DEFAULT_COLUMNS
)
from .parser import parse_gdb_output, extract_register_page_number_display


def _extract_page_number_core(pte_value: str) -> int:
    """从页表项值中提取物理页号的核心逻辑
    
    Args:
        pte_value: 页表项值，如 "0x20e97801"
        
    Returns:
        物理页号（整数），如果无效则返回-1
    """
    try:
        # 使用配置中的常量检查空值
        if not pte_value or pte_value == NULL_VAL or pte_value == DISPLAY_NULL_VAL:
            return -1

        # 移除 "0x" 前缀并转为整数
        if pte_value.startswith("0x"):
            pte_int = int(pte_value[2:], 16)
        else:
            pte_int = int(pte_value, 16)

        # 检查V位（最低位）是否为1，确保是有效页表项
        if (pte_int & 0x1) == 0:
            return -1

        # 使用配置中的位移常量提取物理页号
        page_num = pte_int >> PTE_PPN_SHIFT
        return page_num
    except (ValueError, TypeError):
        return -1


def extract_physical_page_number(pte_value: str) -> str:
    """从页表项值中提取物理页号并格式化为显示字符串
    
    Args:
        pte_value: 页表项值，如 "0x20e97801"
        
    Returns:
        格式化的物理页号字符串，如 "0x20e97" 或空字符串（如果无效）
    """
    page_num = _extract_page_number_core(pte_value)
    if page_num == -1:
        return ""
    return f"0x{page_num:x}"


def extract_physical_page_number_int(pte_value: str) -> int:
    """从页表项值中提取物理页号并返回整数

    Args:
        pte_value: 页表项值，如 "0x20e97801"

    Returns:
        物理页号（整数），如果不是有效页表项则返回-1
    """
    return _extract_page_number_core(pte_value)


class MemoryDotGenerator:
    """封装 GDB 输出解析与 Graphviz DOT 生成"""

    def __init__(self, lines: List[str]) -> None:
        self.memory, self.addresses = parse_gdb_output(lines)
        if not self.addresses:
            raise ValueError("未能从输入中解析出任何地址。")

    @staticmethod
    def to_dot(memory: Dict[str, str], addresses: List[str], prefix: str = "", theme: str = DEFAULT_THEME,
               columns: int = DEFAULT_COLUMNS,
               original_indices: Optional[Dict[str, int]] = None, label: Optional[str] = None,
               is_register: bool = False) -> str:
        """生成 Graphviz DOT 格式字符串，支持自定义列数的矩阵布局"""

        # 获取主题颜色配置
        colors = get_theme_colors(theme)

        border_color = colors["system_gray2"]
        text_color = colors["text_color"]
        # 使用预定义的带透明度背景颜色
        addr_bg = colors["addr_bg"]
        val_bg = colors["val_bg"]
        index_bg = colors["index_bg"]
        cluster_color = colors["cluster_color"]
        addr_border = border_color

        # 计算最大索引值所需的数字位数
        if original_indices:
            # 如果有原始下标信息，使用原始下标中的最大值
            max_index = max(original_indices.values()) if original_indices else len(addresses) - 1
        else:
            # 否则使用当前地址列表的最大索引
            max_index = len(addresses) - 1
        index_width = len(str(max_index))

        def make_node(name: str, node_addr: str, node_val: str, port1_name: str, port2_name: str, index: int) -> str:
            if node_val == DISPLAY_NULL_VAL:
                node_val = PADDED_NULL_DISPLAY
            # 根据最大索引值动态计算宽度，在方括号前添加空格对齐
            if is_register:
                # 寄存器：索引显示为空格
                index_display = " " * (index_width + 3)  # 与 [index] 格式保持相同宽度
            else:
                # 内存：正常显示索引
                index_display = f"{' ' * (index_width - len(str(index)))}[{index}]"

            # 根据是否为寄存器选择不同的页号提取方法
            if is_register:
                # 寄存器：使用寄存器专用的页号提取函数
                page_num_display = extract_register_page_number_display(node_addr, node_val)
            else:
                # 内存：使用页表项的页号提取函数
                page_num_display = extract_physical_page_number(node_val)

            if not page_num_display:
                page_num_display = " "

            # 使用2行2列布局：第一行地址和值，第二行索引和物理页号
            return f'''        {name} [shape=none, margin={NODE_MARGIN}, label=<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" COLOR="{addr_border}">
                <TR>
                    <TD BGCOLOR="{addr_bg}" PORT="{port1_name}" ALIGN="RIGHT" CELLPADDING="{CELL_PADDING}"><FONT COLOR="{text_color}">{node_addr}</FONT></TD>
                    <TD BGCOLOR="{val_bg}" PORT="{port2_name}" ALIGN="RIGHT" CELLPADDING="{CELL_PADDING}"><FONT COLOR="{text_color}">{node_val}</FONT></TD>
                </TR>
                <TR>
                    <TD BGCOLOR="{index_bg}" PORT="index" ALIGN="RIGHT" CELLPADDING="{CELL_PADDING}"><FONT COLOR="{text_color}">{index_display}</FONT></TD>
                    <TD BGCOLOR="{val_bg}" PORT="page" ALIGN="RIGHT" CELLPADDING="{CELL_PADDING}"><FONT COLOR="{text_color}">{page_num_display}</FONT></TD>
                </TR>
            </TABLE>
        >];'''

        all_addrs = addresses.copy()
        cols = columns  # 使用传入的列数参数
        rows = math.ceil(len(all_addrs) / cols) if all_addrs else 0

        # 基于传入的地址列表生成矩阵（已经过滤）
        matrix = [
            all_addrs[r * cols: min((r + 1) * cols, len(all_addrs))]
            for r in range(rows)
        ]
        dot_lines = [
            f"    subgraph cluster_{prefix} {{",
            f"        color=\"{cluster_color}\";",
        ]

        # 如果提供了标签，添加到子图中
        if label:
            dot_lines.append(f"        label=\"{label}\";")
            dot_lines.append(f"        fontname=\"{FONT}\";")
            dot_lines.append(f"        fontsize={FONT_SIZE};")
            dot_lines.append(f"        fontcolor=\"{text_color}\";")
            dot_lines.append("")
        # 节点生成，为每个内存单元添加从0开始的连续下标
        for r, row in enumerate(matrix):
            for c, addr in enumerate(row):
                idx = r * cols + c
                port2 = 'val'
                # 使用传入的原始下标，如果没有则使用地址在当前列表中的索引
                if original_indices and addr in original_indices:
                    original_index = original_indices[addr]
                else:
                    original_index = addresses.index(addr)
                dot_lines.append(make_node(
                    f"{prefix}node{idx}", addr,
                    memory.get(addr, DISPLAY_NULL_VAL),
                    'addr', port2, original_index
                ))
        dot_lines.append("")
        # 水平对齐
        for r, row in enumerate(matrix):
            dot_lines.append(f"        subgraph row_{prefix}_{r} {{")
            dot_lines.append("            rank = same;")
            for c in range(len(row)):
                idx = r * cols + c
                dot_lines.append(f"            {prefix}node{idx};")
            dot_lines.append("        }")
        dot_lines.append("")
        # 垂直对齐隐形边
        for c in range(cols):
            for r in range(rows - 1):
                idx1 = r * cols + c
                idx2 = (r + 1) * cols + c
                if idx2 < len(all_addrs):
                    dot_lines.append(
                        f"        {prefix}node{idx1} -> {prefix}node{idx2} "
                        "[style=invis];"
                    )
        dot_lines.append("    }")
        return "\n".join(dot_lines)
