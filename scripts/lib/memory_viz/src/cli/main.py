"""
内存可视化命令行主程序
读取 GDB 输出、生成内存布局的 Graphviz DOT 文本并输出
"""
import argparse
import sys
from typing import List, Dict, Tuple, Any

from ..core.colors import get_theme_colors
from ..core.generator import (
    MemoryDotGenerator, NULL_VAL,
    RANKDIR, SPLINES, FONT, FONT_SIZE, NODE_MARGIN
)
from ..core.parser import parse_gdb_groups


def parse_args():
    """解析命令行参数，配置文件输入和主题选项"""
    parser = argparse.ArgumentParser(description="生成内存布局的 Graphviz DOT 可视化")
    parser.add_argument('file', nargs='?', help="GDB 内存输出文件路径；若为空则从标准输入读取内容")
    parser.add_argument('--theme', choices=['light', 'dark'], default='light', help="指定输出图的配色主题")
    return parser.parse_args()


def main():
    """读取 GDB 输出、生成内存布局的 Graphviz DOT 文本并输出"""
    args = parse_args()
    # 从文件或标准输入读取 GDB 输出内容
    if args.file:
        with open(args.file, 'r') as f:
            lines = f.read().splitlines()
    else:
        lines = sys.stdin.read().splitlines()
    # 将内存输出按 GDB 命令分组
    groups = parse_gdb_groups(lines)
    # 解析每组地址与内存值，构建全局地址映射表
    group_infos: List[Dict[str, Any]] = []
    global_addr_map: Dict[str, Tuple[str, int]] = {}
    for idx, group in enumerate(groups, 1):
        gen = MemoryDotGenerator(group['lines'])
        prefix = f"g{idx}_"
        all_addrs = gen.addresses.copy()
        group_infos.append({
            'prefix': prefix,
            'all_addrs': all_addrs,
            'memory': gen.memory
        })
        # 为每个地址建立全局索引，用于跨组指针解析
        for i, addr in enumerate(all_addrs):
            global_addr_map[addr] = (prefix, i)
    # 初始化 DOT 文档头部和全局图形属性
    dot_lines = [
        "digraph MemoryLayout {",
        "    graph [bgcolor=transparent];"
    ]

    # 获取主题颜色配置
    colors = get_theme_colors(args.theme)
    font_color = colors["text_color"]

    dot_lines.extend([
        f"    rankdir={RANKDIR};",
        f"    splines={SPLINES};",
        "    nodesep=0.3;",
        "    ranksep=0.6;",
        f"    node [shape=record, fontname=\"{FONT}\", fontsize={FONT_SIZE}, margin={NODE_MARGIN}, fontcolor=\"{font_color}\"];",
        f"    edge [fontname=\"{FONT}\", fontsize={FONT_SIZE}, fontcolor=\"{font_color}\", color=\"{font_color}\"];",
        ""
    ])
    # 为每个内存分组生成子图和节点定义
    for info in group_infos:
        dot_lines.append(
            MemoryDotGenerator.to_dot(info['memory'], info['all_addrs'], prefix=info['prefix'], theme=args.theme)
        )
    # 生成跨组指针连接，将值字段指向对应的地址节点
    dot_lines.append("")
    for info in group_infos:
        prefix = info['prefix']
        for i, addr in enumerate(info['all_addrs']):
            val = info['memory'].get(addr)
            # 检查内存值是否为有效地址且存在于全局地址映射中
            if val and val != NULL_VAL and val in global_addr_map:
                tgt_prefix, tgt_i = global_addr_map[val]
                src_port = 'val'
                dot_lines.append(f"    {prefix}node{i}:{src_port} -> {tgt_prefix}node{tgt_i}:addr;")
    # 输出完整的 DOT 图形定义
    dot_lines.append("}")
    print("\n".join(dot_lines))


if __name__ == "__main__":
    main()
