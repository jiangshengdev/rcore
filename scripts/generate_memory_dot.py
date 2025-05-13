import re
import sys

PATTERN = re.compile(r"0x([0-9a-fA-F]+):\s*(.*)")  # 用于匹配GDB内存输出

def parse_gdb_output(lines):
    memory = {}
    addresses = []
    for line in lines:
        match = PATTERN.match(line)
        if not match:
            continue
        # 将起始地址归一化为无前导零的十六进制
        addr_int = int(match.group(1), 16)
        addr = f"0x{addr_int:x}"
        values = match.group(2).split()
        for v in values:
            # 记录该地址及其归一化后的值
            addresses.append(addr)
            memory[addr] = f"0x{int(v, 16):x}"
            # 地址向后移动一个 8 字节槽
            addr_int += 8
            addr = f"0x{addr_int:x}"
    return memory, addresses

def generate_dot(memory, addresses):
    # head 为第一个地址
    head = addresses[0]
    head_next = memory.get(head)
    # 遍历指针链
    chain = []
    visited = set()
    curr = head_next
    while curr and curr not in visited:
        chain.append(curr)
        visited.add(curr)
        val = memory.get(curr)
        if val == "0x0000000000000000" or val not in memory:
            break
        curr = val

    dot = [
        "digraph MemoryLayout {",
        "    rankdir=TB;",
        "    splines=polyline;",  # 折线样式
        "    node [shape=record, fontname=\"SF Mono,monospace\"];",
        "    edge [fontname=\"SF Mono,monospace\"];",
        ""
    ]
    # 使用 HTML 标签为每个内存地址创建节点，单元格边框着色
    dot.append(f'''    node_head [shape=none, margin=0, label=<
<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
  <TR>
    <TD BORDER="1" COLOR="#FF2D55" PORT="addr" ALIGN="LEFT" CELLPADDING="4">{head}</TD>
    <TD BORDER="1" COLOR="#34C759" PORT="next" ALIGN="LEFT" CELLPADDING="4">{head_next}</TD>
  </TR>
</TABLE>
>];''')
    for i, addr in enumerate(chain, start=1):
        val = memory.get(addr)
        # 对 0x0 补零，显示为 0x00000000
        if val == "0x0":
            val = "0x00000000"
        dot.append(f'''    node{i} [shape=none, margin=0, label=<
<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0">
  <TR>
    <TD BORDER="1" COLOR="#FF2D55" PORT="addr" ALIGN="LEFT" CELLPADDING="4">{addr}</TD>
    <TD BORDER="1" COLOR="#34C759" PORT="val" ALIGN="LEFT" CELLPADDING="4">{val}</TD>
  </TR>
</TABLE>
>];''')

    dot.append("")  # 在不可见边之前添加空行
    # 不可见链，用于垂直对齐节点
    dot.append(f'    node_head -> node1 [style=invis, weight=10];')
    for i in range(1, len(chain)):
        dot.append(f'    node{i} -> node{i+1} [style=invis, weight=10];')

    dot.append("")  # 在实际边之前添加空行
    # 右侧字段（next/val）指向下一个节点左侧字段（addr）
    dot.append(f'    node_head:next -> node1:addr;')
    for i, addr in enumerate(chain, start=1):
        val = memory.get(addr)
        if val != "0x0000000000000000" and i < len(chain):
            dot.append(f'    node{i}:val -> node{i+1}:addr;')
    dot.append("}")
    return "\n".join(dot)

def main():
    # 从文件或标准输入读取
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()
    memory, addresses = parse_gdb_output(lines)
    print(generate_dot(memory, addresses))

if __name__ == "__main__":
    main()
