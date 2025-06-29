"""
纯二叉树分形可视化模块
基于伙伴系统的面积1:2递归模式，生成纯图形的二叉树
"""

import math
import os
import sys

# 添加项目根目录到路径，用于导入公共工具
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))
from scripts.lib.common.utils import ensure_dir, get_file_dir

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from ..core.colors import get_theme_colors

MAX_TREE_DEPTH = 10


def draw_binary_tree(ax: Axes, theme: str = 'light') -> None:
    """绘制纯二叉树分形结构"""

    colors = get_theme_colors(theme)
    line_color = colors["tree_line"]

    def draw_branch(x: float, y: float, angle: float, length: float, order: int):
        """递归绘制树枝"""
        if order > MAX_TREE_DEPTH:
            return

        end_x = x + length * math.cos(angle)
        end_y = y + length * math.sin(angle)

        color_intensity = 1.0 - (order / MAX_TREE_DEPTH) * 0.4
        ax.plot([x, end_x], [y, end_y],  # type: ignore
                color=line_color,
                linewidth=max(1, int(length * 10)),
                alpha=color_intensity)

        if length > 0.1:
            ax.plot(end_x, end_y, 'o',  # type: ignore
                    markersize=max(3, int(length * 20)),
                    color=plt.cm.Set3(order / MAX_TREE_DEPTH),  # type: ignore
                    alpha=0.5)

        new_length = length / math.sqrt(2)
        draw_branch(end_x, end_y, angle - math.pi / 4, new_length, order + 1)
        draw_branch(end_x, end_y, angle + math.pi / 4, new_length, order + 1)

    draw_branch(0, -1.125, math.pi / 2, 1.125, 0)

    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-1.5, 2.5)
    ax.set_aspect('equal')
    ax.axis('off')


def create_pure_binary_tree(theme: str = 'light') -> Figure:
    """创建纯二叉树图形"""

    fig = plt.figure(figsize=(13, 10))  # type: ignore

    fig.patch.set_facecolor('none')

    ax = fig.add_subplot(111)  # type: ignore

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)  # type: ignore

    draw_binary_tree(ax, theme)

    return fig


def save_binary_tree_svg(output_dir: str, theme: str = 'light') -> None:
    """保存二叉树为SVG格式"""
    ensure_dir(output_dir)

    fig = create_pure_binary_tree(theme)

    filename = 'binary-tree-pure.svg'
    plt.savefig(f"{output_dir}/{filename}", format="svg", backend="cairo", transparent=True)  # type: ignore
    plt.close(fig)
    print(f"已保存: {output_dir}/{filename}")


def main() -> None:
    """主函数：生成纯二叉树图形"""
    # 获取当前模块的目录
    current_dir = get_file_dir(__file__)
    output_base_dir = os.path.join(current_dir, '..', '..', '_assets', 'output')

    # 确保输出目录存在
    light_dir = os.path.join(output_base_dir, 'light')
    dark_dir = os.path.join(output_base_dir, 'dark')

    save_binary_tree_svg(light_dir, 'light')
    save_binary_tree_svg(dark_dir, 'dark')

    print("纯二叉树SVG文件已生成完成")


if __name__ == "__main__":
    main()
