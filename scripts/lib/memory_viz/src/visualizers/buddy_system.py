"""
伙伴系统可视化模块
可视化伙伴系统的内存空闲列表
"""
import os
from typing import List, Tuple, Any

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from numpy.typing import NDArray

from ..core.colors import get_theme_colors

# Constants for memory visualization
TICK_COUNT = 9
ADDR_SPLIT_POINT = 0x200000000
LOW_PLOT_XMIN = 0x100000000
LOW_PLOT_XMAX = ADDR_SPLIT_POINT
HIGH_PLOT_XMIN = ADDR_SPLIT_POINT
HIGH_PLOT_XMAX = 0x300000000

# 示例数据：每个元素为 (order, [addr1, addr2, ...])
free_list: List[Tuple[int, List[int]]] = [
    (3, [0x2fffffff0, 0x100000008]),
    (4, [0x2ffffffe0, 0x100000010]),
    (5, [0x2ffffffc0, 0x100000020]),
    (6, [0x2ffffff80, 0x100000040]),
    (7, [0x2ffffff00, 0x100000080]),
    (8, [0x2fffffe00, 0x100000100]),
    (9, [0x2fffffc00, 0x100000200]),
    (10, [0x2fffff800, 0x100000400]),
    (11, [0x2fffff000, 0x100000800]),
    (12, [0x2ffffe000, 0x100001000]),
    (13, [0x2ffffc000, 0x100002000]),
    (14, [0x2ffff8000, 0x100004000]),
    (15, [0x2ffff0000, 0x100008000]),
    (16, [0x2fffe0000, 0x100010000]),
    (17, [0x2fffc0000, 0x100020000]),
    (18, [0x2fff80000, 0x100040000]),
    (19, [0x2fff00000, 0x100080000]),
    (20, [0x2ffe00000, 0x100100000]),
    (21, [0x2ffc00000, 0x100200000]),
    (22, [0x2ff800000, 0x100400000]),
    (23, [0x2ff000000, 0x100800000]),
    (24, [0x2fe000000, 0x101000000]),
    (25, [0x2fc000000, 0x102000000]),
    (26, [0x2f8000000, 0x104000000]),
    (27, [0x2f0000000, 0x108000000]),
    (28, [0x2e0000000, 0x110000000]),
    (29, [0x2c0000000, 0x120000000]),
    (30, [0x280000000, 0x140000000]),
    (31, [0x200000000, 0x180000000]),
]


def human_readable_size(size: int, width: int = 8) -> str:
    if size >= 1024 ** 3:
        s = f"{int(size / (1024 ** 3))} GiB"
    elif size >= 1024 ** 2:
        s = f"{int(size / (1024 ** 2))} MiB"
    elif size >= 1024:
        s = f"{int(size / 1024)} KiB"
    else:
        s = f"{size} B"
    # 块大小右对齐，宽度补空格
    return f"{s:>{width}}"


# Define a formatter function for clarity and better type hinting
def tick_formatter(x_val: float, pos_val: int) -> str:
    # pos_val is unused in this formatter but required by FuncFormatter
    _ = pos_val
    return hex(int(x_val))


def plot_free_segment(ax: Axes, seg_list: List[Tuple[int, List[int]]], xlim: Tuple[int, int], color: str, title: str,
                      align_left: bool = False, theme: str = "light") -> None:
    # 获取主题颜色配置
    colors = get_theme_colors(theme)
    text_color = colors["text_color"]
    border_color = colors["border_color"]

    ax.set_xlim(xlim[0], xlim[1])
    step: float = (xlim[1] - xlim[0]) / (TICK_COUNT - 1)
    xticks_values: List[float] = [xlim[0] + i * step for i in range(TICK_COUNT)]
    ax.set_xticks(xticks_values)  # type: ignore[misc]
    ax.xaxis.set_major_formatter(FuncFormatter(tick_formatter))
    for order, addrs in seg_list:
        for addr in addrs:
            size: int = 1 << order
            ax.broken_barh([(addr, size)], (order - 0.4, 0.8), facecolors=color)  # type: ignore[misc]

            ha = 'left' if align_left else 'right'
            offset = 10000000  # Offset for text positioning
            x_pos = addr + offset if align_left else addr + size - offset

            raw_size_str = human_readable_size(size)
            label_to_plot = f"{hex(addr)}{raw_size_str}"

            ax.text(x_pos, order, label_to_plot,  # type: ignore[misc]
                    va='center', ha=ha, fontfamily='SF Mono', color=text_color)

    ax.set_xlabel("Address", color=text_color)  # type: ignore[misc]
    ax.set_ylabel("Order", color=text_color)  # type: ignore[misc]
    ax.set_yticks([o for o, _ in seg_list])  # type: ignore[misc]
    ax.set_yticklabels([str(o) for o, _ in seg_list], color=text_color)  # type: ignore[misc]

    current_xticks: NDArray[Any] = ax.get_xticks()  # type: ignore[misc]
    ax.set_xticklabels([hex(int(x)) for x in current_xticks], color=text_color)  # type: ignore[misc]

    # 设置刻度线颜色
    ax.tick_params(axis='both', colors=text_color)  # type: ignore[misc]
    ax.grid(True, axis='x', linestyle='--', alpha=0.5, color=text_color)  # type: ignore[misc]
    ax.set_title(title, color=text_color)  # type: ignore[misc]

    # 设置边框颜色
    for spine in ax.spines.values():  # type: ignore[misc]
        spine.set_edgecolor(border_color)
        spine.set_linewidth(1.0)


def split_address_ranges(buddy_free_list: List[Tuple[int, List[int]]]) -> Tuple[
    List[Tuple[int, List[int]]], List[Tuple[int, List[int]]]]:
    """将地址列表分割为低地址区间和高地址区间"""
    left_list: List[Tuple[int, List[int]]] = []
    right_list: List[Tuple[int, List[int]]] = []

    for order, addrs in buddy_free_list:
        left_addrs = [a for a in addrs if a < ADDR_SPLIT_POINT]
        right_addrs = [a for a in addrs if a >= ADDR_SPLIT_POINT]

        if left_addrs:
            left_list.append((order, left_addrs))
        if right_addrs:
            right_list.append((order, right_addrs))

    return left_list, right_list


def create_and_plot_figure(left_list: List[Tuple[int, List[int]]],
                           right_list: List[Tuple[int, List[int]]], theme: str = "light") -> Figure:
    """创建并绘制图表，返回Figure对象"""
    # 获取主题颜色配置
    colors = get_theme_colors(theme)
    orange_color = colors["system_orange"]
    blue_color = colors["system_blue"]

    fig: Figure
    axs: Tuple[Axes, Axes]
    fig, axs = plt.subplots(2, 1, sharey=True, figsize=(13, 13),  # type: ignore[misc]
                            gridspec_kw={'height_ratios': [1, 1]})

    # 设置图表背景为透明
    fig.patch.set_alpha(0)  # type: ignore[misc]

    ax_top: Axes = axs[0]
    ax_bottom: Axes = axs[1]

    # 设置子图背景为透明
    ax_top.patch.set_alpha(0)  # type: ignore[misc]
    ax_bottom.patch.set_alpha(0)  # type: ignore[misc]

    plot_free_segment(ax_top, left_list, (LOW_PLOT_XMIN, LOW_PLOT_XMAX), orange_color,
                      "Buddy System Free List (Low Address Segment)", align_left=True, theme=theme)
    plot_free_segment(ax_bottom, right_list, (HIGH_PLOT_XMIN, HIGH_PLOT_XMAX), blue_color,
                      "Buddy System Free List (High Address Segment)", align_left=False, theme=theme)
    plt.tight_layout()

    return fig


def save_figure_with_style(left_list: List[Tuple[int, List[int]]],
                           right_list: List[Tuple[int, List[int]]],
                           style: str, output_dir: str, filename: str) -> None:
    """使用指定样式保存图表"""
    os.makedirs(output_dir, exist_ok=True)
    plt.style.use(style)

    # 根据样式确定主题
    theme = "dark" if style == "dark_background" else "light"
    fig = create_and_plot_figure(left_list, right_list, theme)
    plt.savefig(f"{output_dir}/{filename}", format="svg", backend="cairo", transparent=True)  # type: ignore[misc]
    plt.close(fig)


# 将脚本执行逻辑封装到 main 函数
def main() -> None:
    # 获取当前模块的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_base_dir = os.path.join(current_dir, '..', '..', 'output')

    # 确保输出目录存在
    light_dir = os.path.join(output_base_dir, 'light')
    dark_dir = os.path.join(output_base_dir, 'dark')

    # 自动分割：高地址区间（右侧）和低地址区间（左侧）
    left_list, right_list = split_address_ranges(free_list)

    # 生成 light 风格输出
    save_figure_with_style(left_list, right_list, 'default', light_dir, 'buddy-free-list.svg')

    # 生成 dark 风格输出
    save_figure_with_style(left_list, right_list, 'dark_background', dark_dir, 'buddy-free-list.svg')

    print("伙伴系统可视化文件已生成完成")


if __name__ == "__main__":
    main()
