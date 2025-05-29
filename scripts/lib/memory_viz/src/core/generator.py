"""
内存 DOT 生成器模块
封装 GDB 输出解析与 Graphviz DOT 生成功能
"""
import math
from typing import List, Dict, Optional

from .colors import get_theme_colors
from .parser import parse_gdb_output

# DOT 生成及内存格式化相关常量
# 空指针的实际数值表示
NULL_VAL = "0x0000000000000000"
# 空指针的显示值
DISPLAY_NULL_VAL = "0x0"
# 空指针的填充后显示
PADDED_NULL_DISPLAY = "0x00000000"
# 子图布局方向：TB（自顶向下）
RANKDIR = "TB"
# 边的样式：使用平滑样条曲线
SPLINES = "spline"
# 字体名称
FONT = "SF Mono,monospace"
# 字体大小
FONT_SIZE = 12
# 表格单元格内边距
CELL_PADDING = 4
# 节点间距
NODE_MARGIN = 0.125


class MemoryDotGenerator:
    """封装 GDB 输出解析与 Graphviz DOT 生成"""

    def __init__(self, lines: List[str]) -> None:
        self.memory, self.addresses = parse_gdb_output(lines)
        if not self.addresses:
            raise ValueError("未能从输入中解析出任何地址。")

    @staticmethod
    def to_dot(memory: Dict[str, str], addresses: List[str], prefix: str = "", theme: str = "light", columns: int = 4,
               original_indices: Optional[Dict[str, int]] = None, label: Optional[str] = None) -> str:
        """生成 Graphviz DOT 格式字符串，支持自定义列数的矩阵布局"""

        # 获取主题颜色配置
        colors = get_theme_colors(theme)

        border_color = colors["border_color"]
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
            index_display = f"{' ' * (index_width - len(str(index)))}[{index}]"
            return f'''        {name} [shape=none, margin={NODE_MARGIN}, label=<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" COLOR="{addr_border}">
                <TR>
                    <TD BGCOLOR="{index_bg}" PORT="index" ALIGN="CENTER" CELLPADDING="{CELL_PADDING}"><FONT COLOR="{text_color}">{index_display}</FONT></TD>
                    <TD BGCOLOR="{addr_bg}" PORT="{port1_name}" ALIGN="LEFT" CELLPADDING="{CELL_PADDING}"><FONT COLOR="{text_color}">{node_addr}</FONT></TD>
                    <TD BGCOLOR="{val_bg}" PORT="{port2_name}" ALIGN="LEFT" CELLPADDING="{CELL_PADDING}"><FONT COLOR="{text_color}">{node_val}</FONT></TD>
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
