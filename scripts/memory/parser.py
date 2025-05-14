import re

PATTERN = re.compile(r"0x([0-9a-fA-F]+):\s*(.*)")  # 用于匹配GDB内存输出
GROUP_CMD_PATTERN = re.compile(r"\(gdb\) x /(g|\d+g) (0x[0-9a-fA-F]+)")


def parse_gdb_output(lines: list[str]) -> tuple[dict[str, str], list[str]]:
  """解析 GDB 内存输出为地址到值的映射和地址列表"""
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
  """按(gdb) x /g ...命令分组，返回每组的命令和内容"""
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
