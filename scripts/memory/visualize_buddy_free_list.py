import os

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# type: ignore

# 刻度数量常量
TICK_COUNT = 9

# 示例数据：每个元素为 (order, [addr1, addr2, ...])
free_list = [
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


def human_readable_size(size, width=8):
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


def plot_free_segment(ax, seg_list, xlim, color, title, align_last_left=False):
    ax.set_xlim(xlim[0], xlim[1])
    step = (xlim[1] - xlim[0]) // (TICK_COUNT - 1)
    ax.set_xticks([xlim[0] + i * step for i in range(TICK_COUNT)])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: hex(int(x))))
    total = sum(len(addrs) for _, addrs in seg_list)
    count = 0
    for order, addrs in seg_list:
        for addr in addrs:
            size = 1 << order
            ax.broken_barh([(addr, size)], (order - 0.4, 0.8), facecolors=color)
            if align_last_left:
                ha = 'left' if count == total - 1 else 'right'
            else:
                ha = 'left'
            # 标签内容：一行显示地址和右对齐的人类可读单位
            label = f"{hex(addr)}  {human_readable_size(size)}"
            ax.text(addr, order, label, va='center', ha=ha, fontsize=6, fontfamily='monospace')
            count += 1
    ax.set_xlabel("Address", fontsize=8)
    ax.set_ylabel("Order", fontsize=8)
    ax.set_yticks([o for o, _ in seg_list])
    ax.set_yticklabels([str(o) for o, _ in seg_list], fontsize=7)
    ax.set_xticklabels([hex(int(x)) for x in ax.get_xticks()], fontsize=7)
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)
    ax.set_title(title, fontsize=10)


# 将脚本执行逻辑封装到 main 函数
def main():
    # 自动分割：高地址区间（右侧）和低地址区间（左侧）
    left_list = []
    right_list = []
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
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharey=True, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 1]})
    plot_free_segment(ax_top, left_list, (0x100000000, 0x200000000), 'tab:orange',
                      "Buddy System Free List (Low Address Segment)")
    plot_free_segment(ax_bottom, right_list, (0x200000000, 0x300000000), 'tab:blue',
                      "Buddy System Free List (High Address Segment)", align_last_left=True)
    plt.tight_layout()
    plt.savefig("light/buddy-free-list.svg", format="svg", dpi=96)
    plt.close(fig)

    # 生成 dark 风格
    os.makedirs("dark", exist_ok=True)
    plt.style.use('dark_background')
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharey=True, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 1]})
    plot_free_segment(ax_top, left_list, (0x100000000, 0x200000000), 'tab:orange',
                      "Buddy System Free List (Low Address Segment)")
    plot_free_segment(ax_bottom, right_list, (0x200000000, 0x300000000), 'tab:blue',
                      "Buddy System Free List (High Address Segment)", align_last_left=True)
    plt.tight_layout()
    plt.savefig("dark/buddy-free-list.svg", format="svg", dpi=96)
    plt.close(fig)

    # 可选：显示最后一次（dark）风格
    plt.style.use('dark_background')
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, sharey=True, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 1]})
    plot_free_segment(ax_top, left_list, (0x100000000, 0x200000000), 'tab:orange',
                      "Buddy System Free List (Low Address Segment)")
    plot_free_segment(ax_bottom, right_list, (0x200000000, 0x300000000), 'tab:blue',
                      "Buddy System Free List (High Address Segment)", align_last_left=True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
