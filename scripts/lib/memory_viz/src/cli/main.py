"""
内存可视化命令行主程序
读取 GDB 输出、生成内存布局的 Graphviz DOT 文本并输出
"""
import argparse
import math
import sys
from typing import List, Dict, Tuple, Any

from ..core.colors import get_theme_colors
from ..core.filter import filter_zero_rows
from ..core.generator import (
    MemoryDotGenerator, NULL_VAL,
    RANKDIR, SPLINES, FONT, FONT_SIZE, NODE_MARGIN,
    extract_physical_page_number_int
)
from ..core.parser import parse_gdb_groups


def parse_args():
    """解析命令行参数，配置文件输入和主题选项"""
    parser = argparse.ArgumentParser(description="生成内存布局的 Graphviz DOT 可视化")
    parser.add_argument('file', nargs='?', help="GDB 内存输出文件路径；若为空则从标准输入读取内容")
    parser.add_argument('--theme', choices=['light', 'dark'], default='light', help="指定输出图的配色主题")
    parser.add_argument('--columns', type=int, default=4, help="指定内存布局的列数（默认为4列）")
    return parser.parse_args()


def extract_page_number_from_cmd(cmd: str) -> str:
    """从GDB命令中提取起始地址并计算物理页号"""
    import re
    # 匹配GDB命令中的地址，例如：(gdb) x /512g 0x83A5B000
    match = re.search(r'0x([0-9a-fA-F]+)', cmd)
    if match:
        addr = int(match.group(1), 16)
        # 右移12位得到物理页号
        page_num = addr >> 12
        return f"Physical Page: 0x{page_num:x}"
    return cmd  # 如果解析失败，返回原命令


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
    page_to_group_map: Dict[int, str] = {}  # 物理页号到组前缀的映射

    for idx, group in enumerate(groups, 1):
        gen = MemoryDotGenerator(group['lines'])
        prefix = f"g{idx}_"

        # 保存原始地址和下标信息
        original_addrs = gen.addresses.copy()
        original_indices = {addr: i for i, addr in enumerate(original_addrs)}

        # 使用过滤器过滤掉全为0的行
        filtered_addrs = filter_zero_rows(original_addrs, gen.memory, args.columns)

        # 从GDB命令中提取物理页号作为标签
        page_label = extract_page_number_from_cmd(group.get('cmd', ''))

        # 提取物理页号并建立页号到组的映射
        cmd_str = group.get('cmd', '')
        import re
        match = re.search(r'0x([0-9a-fA-F]+)', cmd_str)
        if match:
            addr = int(match.group(1), 16)
            page_num = addr >> 12  # 计算物理页号
            page_to_group_map[page_num] = prefix

        group_infos.append({
            'prefix': prefix,
            'filtered_addrs': filtered_addrs,
            'original_indices': original_indices,
            'memory': gen.memory,
            'cmd': page_label  # 使用物理页号作为标签
        })

        # 为过滤后的地址建立全局索引，用于跨组指针解析
        for i, addr in enumerate(filtered_addrs):
            global_addr_map[addr] = (prefix, i)
    # 初始化 DOT 文档头部和全局图形属性
    dot_lines = [
        "digraph MemoryLayout {",
        "    graph [bgcolor=transparent];",
        "    compound=true;"  # 启用集群间连接功能
    ]

    # 获取主题颜色配置
    colors = get_theme_colors(args.theme)
    font_color = colors["text_color"]

    dot_lines.extend([
        f"    rankdir={RANKDIR};",
        f"    splines={SPLINES};",
        "    nodesep=0.3;",
        "    ranksep=0.1;",
        f"    node [shape=record, fontname=\"{FONT}\", fontsize={FONT_SIZE}, margin={NODE_MARGIN}, fontcolor=\"{font_color}\"];",
        f"    edge [fontname=\"{FONT}\", fontsize={FONT_SIZE}, fontcolor=\"{font_color}\", color=\"{font_color}\"];",
        ""
    ])
    # 为每个内存分组生成子图和节点定义
    for info in group_infos:
        dot_lines.append(
            MemoryDotGenerator.to_dot(
                info['memory'],
                info['filtered_addrs'],
                prefix=info['prefix'],
                theme=args.theme,
                columns=args.columns,
                original_indices=info['original_indices'],
                label=info['cmd']  # 将 GDB 命令作为标签传递
            )
        )

    # 生成组间垂直对齐边，连接上一组最后一行与下一组第一行的对应列元素
    dot_lines.append("")
    for i in range(len(group_infos) - 1):
        curr_info = group_infos[i]
        next_info = group_infos[i + 1]

        curr_filtered = curr_info['filtered_addrs']
        next_filtered = next_info['filtered_addrs']

        if curr_filtered and next_filtered:
            curr_rows = math.ceil(len(curr_filtered) / args.columns)
            # 获取最后一行的起始索引
            last_row_start = (curr_rows - 1) * args.columns

            # 对于每一列，创建隐藏的对齐边保持布局结构
            for c in range(args.columns):
                curr_idx = last_row_start + c
                next_idx = c  # 下一组第一行的对应列
                if curr_idx < len(curr_filtered) and next_idx < len(next_filtered):
                    dot_lines.append(
                        f"    {curr_info['prefix']}node{curr_idx} -> {next_info['prefix']}node{next_idx} [style=invis];"
                    )

    # 生成跨组指针连接，将值字段指向对应的地址节点
    dot_lines.append("")
    for info in group_infos:
        prefix = info['prefix']
        for i, addr in enumerate(info['filtered_addrs']):
            val = info['memory'].get(addr)
            # 检查内存值是否为有效地址且存在于全局地址映射中
            if val and val != NULL_VAL and val in global_addr_map:
                tgt_prefix, tgt_i = global_addr_map[val]
                src_port = 'val'
                dot_lines.append(f"    {prefix}node{i}:{src_port} -> {tgt_prefix}node{tgt_i}:addr;")

            # 检查内存值是否为有效页表项，并生成页表指针
            elif val and val != NULL_VAL:
                page_num = extract_physical_page_number_int(val)
                if page_num != -1 and page_num in page_to_group_map:
                    # 找到页表项指向的物理页号对应的组
                    tgt_prefix = page_to_group_map[page_num]
                    # 生成页表指针，使用lhead指向整个集群
                    # 由于需要有一个实际的目标节点，我们指向第一个节点但使用lhead指向集群
                    dot_lines.append(
                        f"    {prefix}node{i}:page -> {tgt_prefix}node3 [color=\"orange\", lhead=\"cluster_{tgt_prefix}\", constraint=false];")
    # 输出完整的 DOT 图形定义
    dot_lines.append("}")
    print("\n".join(dot_lines))


if __name__ == "__main__":
    main()
