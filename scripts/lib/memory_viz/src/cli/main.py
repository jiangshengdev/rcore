"""
内存可视化命令行主程序
读取 GDB 输出、生成内存布局的 Graphviz DOT 文本并输出
"""
import argparse
import math
import sys
from typing import List, Dict, Tuple, Any

# 定义类型别名来改善类型推断
GdbGroup = Dict[str, Any]  # GDB 命令组的类型
GroupInfo = Dict[str, Any]  # 组信息的类型

from ..core.config import DEFAULT_THEME, DEFAULT_COLUMNS, RANKDIR, SPLINES, FONT, FONT_SIZE, NODE_MARGIN, THEME_CHOICES
from ..core.colors import get_theme_colors
from ..core.filter import filter_zero_rows
from ..core.generator import (
    MemoryDotGenerator, NULL_VAL,
    extract_physical_page_number_int
)
from ..core.parser import (
    parse_gdb_groups,
    contains_register_output,
    parse_register_to_memory_format,
    is_register_command,
    is_register_value_line,
    extract_register_page_number,
    extract_page_number_from_string,
    format_page_number_label
)


def parse_args():
    """解析命令行参数，配置文件输入和主题选项"""
    parser = argparse.ArgumentParser(description="生成内存布局的 Graphviz DOT 可视化")
    parser.add_argument('file', nargs='?', help="GDB 内存输出文件路径；若为空则从标准输入读取内容")
    parser.add_argument('--theme', choices=THEME_CHOICES, default=DEFAULT_THEME, help="指定输出图的配色主题")
    parser.add_argument('--columns', type=int, default=DEFAULT_COLUMNS, help="指定内存布局的列数（默认为4列）")
    return parser.parse_args()


def generate_group_label(group_type: str, data: Any) -> str:
    """根据组类型生成合适的标题"""
    if group_type == "register":
        # 寄存器组：显示寄存器名称或通用标题
        try:
            # 使用类型守卫来确保安全的类型检查
            if hasattr(data, '__len__') and hasattr(data, '__getitem__'):
                if len(data) > 0:
                    if len(data) == 1:
                        return f"Register: {data[0]}"
                    else:
                        return "Registers"
        except (TypeError, IndexError):
            pass
        return "Registers"
    elif group_type == "memory":
        # 内存组：显示物理页号
        return format_page_number_label(str(data))
    else:
        return str(data)


def main():
    """读取 GDB 输出、生成内存布局的 Graphviz DOT 文本并输出"""
    args = parse_args()
    # 从文件或标准输入读取 GDB 输出内容
    if args.file:
        with open(args.file, 'r') as f:
            lines = f.read().splitlines()
    else:
        lines = sys.stdin.read().splitlines()

    # 解析每组地址与内存值，构建全局地址映射表
    group_infos: List[Dict[str, Any]] = []
    global_addr_map: Dict[str, Tuple[str, int]] = {}
    page_to_group_map: Dict[int, str] = {}  # 物理页号到组前缀的映射
    
    # 检测是否有 satp 寄存器，用于决定后续的处理方式
    has_satp = contains_register_output(lines)

    # 检测并处理寄存器输出
    if has_satp:
        # 分离寄存器和内存输出
        register_lines = [line for line in lines if is_register_value_line(line)]
        memory_lines = [line for line in lines if not is_register_command(line) and not is_register_value_line(line)]

        # 处理寄存器组
        if register_lines:
            reg_memory, reg_addresses = parse_register_to_memory_format(register_lines)
            # 明确定义寄存器组信息结构
            register_group: GroupInfo = {
                'prefix': 'reg_',
                'filtered_addrs': reg_addresses,
                'memory': reg_memory,
                'original_indices': {addr: i for i, addr in enumerate(reg_addresses)},
                'cmd': generate_group_label("register", reg_addresses),
                'group_type': 'register'
            }
            group_infos.append(register_group)

            # 建立寄存器的全局映射（用于指针连接）
            for i, addr in enumerate(reg_addresses):
                global_addr_map[addr] = ('reg_', i)
    else:
        memory_lines = lines

    # 将内存输出按 GDB 命令分组
    groups = parse_gdb_groups(memory_lines)

    for idx, group in enumerate(groups, 1):
        gen = MemoryDotGenerator(group['lines'])
        prefix = f"g{idx}_"

        # 保存原始地址和下标信息
        original_addrs = gen.addresses.copy()
        original_indices = {addr: i for i, addr in enumerate(original_addrs)}

        # 使用过滤器过滤掉全为0的行
        filtered_addrs = filter_zero_rows(original_addrs, gen.memory, args.columns)

        # 从GDB命令中提取物理页号作为标签
        page_label = generate_group_label("memory", group.get('cmd', ''))

        # 提取物理页号并建立页号到组的映射
        cmd_str = group.get('cmd', '')
        page_num = extract_page_number_from_string(cmd_str)
        if page_num is not None:
            page_to_group_map[page_num] = prefix

        group_infos.append({
            'prefix': prefix,
            'filtered_addrs': filtered_addrs,
            'original_indices': original_indices,
            'memory': gen.memory,
            'cmd': page_label,  # 使用生成的标签
            'group_type': 'memory'  # 标记组类型
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
    
    # 根据是否有 satp 寄存器决定布局参数
    ranksep_value = "0.1" if has_satp else "0.6"
    
    dot_lines.extend([
        f"    rankdir={RANKDIR};",
        f"    splines={SPLINES};",
        "    nodesep=0.3;",
        f"    ranksep={ranksep_value};",
        f"    node [shape=record, fontname=\"{FONT}\", fontsize={FONT_SIZE}, margin={NODE_MARGIN}, fontcolor=\"{font_color}\"];",
        f"    edge [fontname=\"{FONT}\", fontsize={FONT_SIZE}, fontcolor=\"{font_color}\", color=\"{font_color}\"];",
        ""
    ])
    # 为每个内存分组生成子图和节点定义
    for info in group_infos:
        # 寄存器组使用单列布局，内存组使用用户指定的列数
        columns = 1 if info.get('group_type') == 'register' else args.columns
        is_register = info.get('group_type') == 'register'
        
        # 根据是否有 satp 决定是否显示标签
        label = info['cmd'] if has_satp else None

        dot_lines.append(
            MemoryDotGenerator.to_dot(
                info['memory'],
                info['filtered_addrs'],
                prefix=info['prefix'],
                theme=args.theme,
                columns=columns,
                original_indices=info['original_indices'],
                label=label,  # 有 satp 时显示标签，无 satp 时移除标签
                is_register=is_register  # 传递寄存器标识
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

    # 生成跨组指针连接，连接节点之间而不是节点内部的元素
    dot_lines.append("")
    for info in group_infos:
        prefix = info['prefix']
        group_type = info.get('group_type', 'memory')

        for i, addr in enumerate(info['filtered_addrs']):
            val = info['memory'].get(addr)
            # 检查内存值是否为有效地址且存在于全局地址映射中
            if val and val != NULL_VAL and val in global_addr_map:
                tgt_prefix, tgt_i = global_addr_map[val]
                if has_satp:
                    # 有 satp 时使用原来的端口连接方式
                    src_port = 'val'
                    dot_lines.append(f"    {prefix}node{i}:{src_port} -> {tgt_prefix}node{tgt_i}:addr;")
                else:
                    # 无 satp 时连接整个节点，使用蓝色箭头
                    dot_lines.append(f"    {prefix}node{i} -> {tgt_prefix}node{tgt_i} [color=\"{colors['system_blue']}\", constraint=false];")

            # 检查内存值或寄存器值是否指向有效页表项
            elif val and val != NULL_VAL:
                # 根据组类型使用不同的页号提取方法
                if group_type == 'register':
                    # 寄存器：使用特殊的寄存器页号提取函数
                    page_num = extract_register_page_number(addr, val)
                else:
                    # 内存：使用普通的页表项页号提取函数
                    page_num = extract_physical_page_number_int(val)

                if page_num != -1 and page_num in page_to_group_map:
                    # 找到页表项指向的物理页号对应的组
                    tgt_prefix = page_to_group_map[page_num]
                    if has_satp:
                        # 有 satp 时使用原来的连接方式，指向特定节点并使用端口
                        # 寄存器连接使用红色，内存连接使用橙色
                        color = colors["system_red"] if group_type == 'register' else colors["system_orange"]
                        dot_lines.append(
                            f"    {prefix}node{i}:page -> {tgt_prefix}node3 [color=\"{color}\", lhead=\"cluster_{tgt_prefix}\", constraint=false];")
                    else:
                        # 无 satp 时使用蓝色箭头并指向第一个节点
                        dot_lines.append(
                            f"    {prefix}node{i} -> {tgt_prefix}node0 [color=\"{colors['system_blue']}\", lhead=\"cluster_{tgt_prefix}\", constraint=false];")
    # 输出完整的 DOT 图形定义
    dot_lines.append("}")
    print("\n".join(dot_lines))


if __name__ == "__main__":
    main()
