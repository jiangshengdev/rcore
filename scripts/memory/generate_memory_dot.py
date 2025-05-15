import sys
import argparse
from scripts.memory.parser import parse_gdb_groups
from scripts.memory.memory_dot_generator import (
    MemoryDotGenerator, NULL_VAL,
    RANKDIR, SPLINES, FONT, FONT_SIZE, NODE_MARGIN
)
from typing import List, Dict, Tuple, Any


def parse_args():
    parser = argparse.ArgumentParser(description="获取输入文件路径和主题(light/dark)选项，解析命令行参数")
    parser.add_argument('file', nargs='?', help="GDB 内存输出文件路径；若为空则从标准输入读取内容")
    parser.add_argument('--theme', choices=['light', 'dark'], default='light', help="指定输出图的配色主题")
    return parser.parse_args()


def main():
    """读取 GDB 输出、生成内存布局的 Graphviz DOT 文本并输出"""
    args = parse_args()
    # 获取并按行拆分 GDB 输出
    if args.file:
        with open(args.file, 'r') as f:
            lines = f.read().splitlines()
    else:
        lines = sys.stdin.read().splitlines()
    # 按命令分组内存输出
    groups = parse_gdb_groups(lines)
    # 遍历每组，解析并收集地址与内存值，同时构建全局地址索引
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
        for i, addr in enumerate(all_addrs):
            global_addr_map[addr] = (prefix, i)
    # 初始化 DOT 内容和图属性
    dot_lines = ["digraph MemoryLayout {"]
    # 设置透明背景
    dot_lines.append("    graph [bgcolor=transparent];")
    dot_lines.extend([
        f"    rankdir={RANKDIR};",
        f"    splines={SPLINES};",
        "    nodesep=0.3;",
        "    ranksep=0.6;",
        f"    node [shape=record, fontname=\"{FONT}\", fontsize={FONT_SIZE}, margin={NODE_MARGIN}" + (
            ", fontcolor=white" if args.theme == 'dark' else "") + "];",
        f"    edge [fontname=\"{FONT}\", fontsize={FONT_SIZE}" + (
            ", fontcolor=white, color=white" if args.theme == 'dark' else "") + "];",
        ""
    ])
    # 生成每个分组的子图节点和布局约束
    for info in group_infos:
        dot_lines.append(
            MemoryDotGenerator.to_dot(info['memory'], info['all_addrs'], prefix=info['prefix'], theme=args.theme)
        )
    # 添加组间指针指向真实地址的连接
    dot_lines.append("")
    for info in group_infos:
        prefix = info['prefix']
        for i, addr in enumerate(info['all_addrs']):
            val = info['memory'].get(addr)
            if val and val != NULL_VAL and val in global_addr_map:
                tgt_prefix, tgt_i = global_addr_map[val]
                src_port = 'next' if i == 0 else 'val'
                dot_lines.append(f"    {prefix}node{i}:{src_port} -> {tgt_prefix}node{tgt_i}:addr;")
    # 结束 DOT 定义并打印输出
    dot_lines.append("}")
    print("\n".join(dot_lines))


if __name__ == "__main__":
    main()
