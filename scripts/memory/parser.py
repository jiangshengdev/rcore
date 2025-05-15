import re

# 匹配 GDB 内存输出行中的地址和值
PATTERN = re.compile(r"0x([0-9a-fA-F]+):\s*(.*)")

# 匹配 GDB 内存查看命令及其参数
GROUP_CMD_PATTERN = re.compile(r"\(gdb\) x /(g|\d+g) (0x[0-9a-fA-F]+)")


def parse_gdb_output(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    """将 GDB 内存输出解析为地址到值的映射，以及按访问顺序排列的地址列表"""
    memory: dict[str, str] = {}
    addresses: list[str] = []
    for line in lines:
        match = PATTERN.match(line)
        if not match:
            continue
        addr_int = int(match.group(1), 16)
        addr = f"0x{addr_int:x}"
        values = match.group(2).split()
        for v in values:
            addresses.append(addr)
            memory[addr] = f"0x{int(v, 16):x}"
            addr_int += 8
            addr = f"0x{addr_int:x}"
    return memory, addresses


def parse_gdb_groups(lines: list[str]) -> list[dict]:
    """将 GDB 内存查看命令和其输出按命令分组，返回每组的命令文本与对应输出行"""
    groups: list[dict] = []
    curr_group = None
    for line in lines:
        m = GROUP_CMD_PATTERN.match(line)
        if m:
            if curr_group:
                groups.append(curr_group)
            curr_group = {'cmd': line, 'lines': []}
        elif curr_group is not None:
            curr_group['lines'].append(line)
    if curr_group:
        groups.append(curr_group)
    return groups
