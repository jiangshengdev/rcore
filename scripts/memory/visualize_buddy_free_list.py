import os
from typing import List, Tuple

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.ticker import FuncFormatter
import numpy as np
from numpy.typing import NDArray

# 刻度数量常量
TICK_COUNT = 9

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


def plot_free_segment(ax: Axes, seg_list: List[Tuple[int, List[int]]], xlim: Tuple[int, int], color: str, title: str, align_last_left: bool = False) -> None:
    ax.set_xlim(xlim[0], xlim[1])
    step: float = (xlim[1] - xlim[0]) / (TICK_COUNT - 1)
    xticks_values: List[float] = [xlim[0] + i * step for i in range(TICK_COUNT)]
    ax.set_xticks(xticks_values) # type: ignore
    ax.xaxis.set_major_formatter(FuncFormatter(tick_formatter))
    total = sum(len(addrs) for _, addrs in seg_list)
    count = 0
    for order, addrs in seg_list:
        for addr in addrs:
            size: int = 1 << order
            ax.broken_barh([(addr, size)], (order - 0.4, 0.8), facecolors=color) # type: ignore
            if align_last_left:
                ha = 'left' if count == total - 1 else 'right'
            else:
                ha = 'left'
            label = f"{hex(addr)}  {human_readable_size(size)}"
            ax.text(addr, order, label, va='center', ha=ha, fontfamily='monospace') # type: ignore
            count += 1
    ax.set_xlabel("Address") # type: ignore
    ax.set_ylabel("Order") # type: ignore
    ax.set_yticks([o for o, _ in seg_list]) # type: ignore
    ax.set_yticklabels([str(o) for o, _ in seg_list]) # type: ignore
    
    current_xticks: NDArray[np.float64] = ax.get_xticks() # type: ignore # Changed to np.float64
    ax.set_xticklabels([hex(int(x)) for x in current_xticks]) # type: ignore
    
    ax.grid(True, axis='x', linestyle='--', alpha=0.5) # type: ignore
    ax.set_title(title) # type: ignore


# 将脚本执行逻辑封装到 main 函数
def main() -> None:
    # 自动分割：高地址区间（右侧）和低地址区间（左侧）
    left_list: List[Tuple[int, List[int]]] = []
    right_list: List[Tuple[int, List[int]]] = []
    for order, addrs in free_list:
        left_addrs = [a for a in addrs if a < 0x200000000]
        right_addrs = [a for a in addrs if a >= 0x200000000]
        if left_addrs:
            left_list.append((order, left_addrs))
        if right_addrs:
            right_list.append((order, right_addrs))

    # 生成 light 风格
    os.makedirs("light", exist_ok=True)
    plt.style.use('default')
    fig_light: Figure
    axs_light: NDArray[np.object_] # Type hint for the array of Axes
    fig_light, axs_light = plt.subplots(2, 1, sharey=True, figsize=(13, 13), gridspec_kw={'height_ratios': [1, 1]}) # type: ignore
    ax_top_light: Axes = axs_light[0]
    ax_bottom_light: Axes = axs_light[1]
    
    plot_free_segment(ax_top_light, left_list, (0x100000000, 0x200000000), 'tab:orange',
                      "Buddy System Free List (Low Address Segment)")
    plot_free_segment(ax_bottom_light, right_list, (0x200000000, 0x300000000), 'tab:blue',
                      "Buddy System Free List (High Address Segment)", align_last_left=True)
    plt.tight_layout()
    plt.savefig("light/buddy-free-list.svg", format="svg", backend="cairo") # type: ignore
    plt.close(fig_light)

    # 生成 dark 风格
    os.makedirs("dark", exist_ok=True)
    plt.style.use('dark_background')
    fig_dark: Figure
    axs_dark: NDArray[np.object_] # Type hint for the array of Axes
    fig_dark, axs_dark = plt.subplots(2, 1, sharey=True, figsize=(13, 13), gridspec_kw={'height_ratios': [1, 1]}) # type: ignore
    ax_top_dark: Axes = axs_dark[0]
    ax_bottom_dark: Axes = axs_dark[1]

    plot_free_segment(ax_top_dark, left_list, (0x100000000, 0x200000000), 'tab:orange',
                      "Buddy System Free List (Low Address Segment)")
    plot_free_segment(ax_bottom_dark, right_list, (0x200000000, 0x300000000), 'tab:blue',
                      "Buddy System Free List (High Address Segment)", align_last_left=True)
    plt.tight_layout()
    plt.savefig("dark/buddy-free-list.svg", format="svg", backend="cairo") # type: ignore
    plt.close(fig_dark)

    # 可选：显示最后一次（dark）风格
    plt.style.use('dark_background')
    _fig_show: Figure # Marked as unused
    axs_show: NDArray[np.object_] # Type hint for the array of Axes
    _fig_show, axs_show = plt.subplots(2, 1, sharey=True, figsize=(13, 13), gridspec_kw={'height_ratios': [1, 1]}) # type: ignore
    ax_top_show: Axes = axs_show[0]
    ax_bottom_show: Axes = axs_show[1]
    
    plot_free_segment(ax_top_show, left_list, (0x100000000, 0x200000000), 'tab:orange',
                      "Buddy System Free List (Low Address Segment)")
    plot_free_segment(ax_bottom_show, right_list, (0x200000000, 0x300000000), 'tab:blue',
                      "Buddy System Free List (High Address Segment)", align_last_left=True)
    plt.tight_layout()
    plt.show() # type: ignore


if __name__ == "__main__":
    main()
