import math
from typing import List, Dict

from colors import get_theme_colors, hex_with_alpha
from parser import parse_gdb_output

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
    def to_dot(memory: Dict[str, str], addresses: List[str], prefix: str = "", theme: str = "light") -> str:
        """生成 Graphviz DOT 格式字符串，支持 4 列矩阵布局"""

        # 获取主题颜色配置
        colors = get_theme_colors(theme)

        border_color = colors["border_color"]
        text_color = colors["text_color"]
        addr_bg = hex_with_alpha(colors["system_pink"], 0.125)
        val_bg = hex_with_alpha(colors["system_green"], 0.125)
        cluster_color = colors["cluster_color"]
        addr_border = border_color

        def make_node(name: str, addr: str, val: str, port1: str, port2: str) -> str:
            if val == DISPLAY_NULL_VAL:
                val = PADDED_NULL_DISPLAY
            return f'''        {name} [shape=none, margin={NODE_MARGIN}, label=<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" COLOR="{addr_border}">
                <TR>
                    <TD BGCOLOR="{addr_bg}" PORT="{port1}" ALIGN="LEFT" CELLPADDING="{CELL_PADDING}"><FONT COLOR="{text_color}">{addr}</FONT></TD>
                    <TD BGCOLOR="{val_bg}" PORT="{port2}" ALIGN="LEFT" CELLPADDING="{CELL_PADDING}"><FONT COLOR="{text_color}">{val}</FONT></TD>
                </TR>
            </TABLE>
        >];'''

        all_addrs = addresses.copy()
        cols = 4
        rows = math.ceil(len(all_addrs) / cols)
        matrix = [
            all_addrs[r * cols: min((r + 1) * cols, len(all_addrs))]
            for r in range(rows)
        ]
        dot_lines = [
            f"    subgraph cluster_{prefix} {{",
            f"        color=\"{cluster_color}\";",
        ]
        # 节点生成
        for r, row in enumerate(matrix):
            for c, addr in enumerate(row):
                idx = r * cols + c
                port2 = 'next' if idx == 0 else 'val'
                dot_lines.append(make_node(
                    f"{prefix}node{idx}", addr,
                    memory.get(addr, DISPLAY_NULL_VAL),
                    'addr', port2
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
                        "[style=invis, constraint=false];"
                    )
        dot_lines.append("    }")
        return "\n".join(dot_lines)
